"""Per-device MQTT-over-WSS connection to the Philips Air+ AWS IoT device shadow.

Each device gets its own paho 2.x websocket client. The SigV4 WSS URL from
``mqttInfo`` is **single-use** (one connection per URL, 1h validity) and the
``client_id`` rotates per call, so every (re)connect re-fetches ``mqttInfo`` and
builds a brand-new paho client. We disable paho's built-in auto-reconnect (it
would reuse the expired URL) and drive reconnect ourselves with backoff.

paho runs its network loop in its own thread; ``on_message`` fires there. We
bridge to the HA asyncio loop with ``hass.loop.call_soon_threadsafe``. Commands
from entities run on the HA loop and call ``client.publish`` directly (paho
publish is thread-safe and non-blocking — it queues to the network thread).
"""
from __future__ import annotations

import asyncio
import json
import logging
import ssl
from threading import Event
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

from . import airmatters_auth as auth
from .const import (
    RECONNECT_MAX,
    RECONNECT_MIN,
    TOPIC_GET,
    TOPIC_GET_ACCEPTED,
    TOPIC_GET_REJECTED,
    TOPIC_UPDATE,
    TOPIC_UPDATE_ACCEPTED,
    TOPIC_UPDATE_DOCUMENTS,
    TOPIC_UPDATE_REJECTED,
)

_LOGGER = logging.getLogger(__name__)


class DeviceConnection:
    """One persistent MQTT-over-WSS connection to one fan's device shadow."""

    def __init__(self, hass, device_id, coordinator, auth_data):
        self.hass = hass
        self.device_id = device_id
        self.coordinator = coordinator
        self.auth_data = auth_data

        self._client: mqtt.Client | None = None
        self._info: dict | None = None          # latest mqttInfo entry for this device
        self._connected = False
        self._connect_event = Event()            # set on CONNACK
        self._stopping = False
        self._reconnect_delay = RECONNECT_MIN
        self._reconnecting = False

        # topics (filled on connect, thing == device_id)
        self._topic_get = TOPIC_GET.format(thing=device_id)
        self._topic_get_accepted = TOPIC_GET_ACCEPTED.format(thing=device_id)
        self._topic_get_rejected = TOPIC_GET_REJECTED.format(thing=device_id)
        self._topic_update = TOPIC_UPDATE.format(thing=device_id)
        self._topic_update_accepted = TOPIC_UPDATE_ACCEPTED.format(thing=device_id)
        self._topic_update_rejected = TOPIC_UPDATE_REJECTED.format(thing=device_id)
        self._topic_update_documents = TOPIC_UPDATE_DOCUMENTS.format(thing=device_id)

    # ------------------------------------------------------------------ connect
    async def async_connect(self) -> bool:
        """Fetch fresh mqttInfo, build a client, connect, wait for CONNACK."""
        if self._stopping:
            return False
        # Tear down any previous client/socket before creating a new one.
        self._teardown_client()
        try:
            info = await self.hass.async_add_executor_job(self._fetch_mqtt_info)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Philips Air+ %s: mqttInfo fetch failed: %s", self.device_id, err)
            self.coordinator.set_connection_state(connected=False, error=str(err))
            self._schedule_reconnect()
            return False
        self._info = info
        host = info["endpoint"]
        path = info["path"]
        client_id = info["client_id"]

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            transport="websockets",
            clean_session=True,
            reconnect_on_failure=False,   # we manage reconnect (URL is single-use)
        )
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

        # paho adds an Origin header by default; AWS IoT rejects unknown headers,
        # so strip it (mirrors the verified control_test scaffold).
        def _strip_origin(headers):
            headers.pop("Origin", None)
            return headers

        client.ws_set_options(path=path, headers=_strip_origin)
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        client.on_message = self._on_message
        client.on_connect_fail = self._on_connect_fail
        self._client = client
        self._connect_event.clear()

        try:
            await self.hass.async_add_executor_job(
                lambda: client.connect(host, 443, keepalive=30))
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Philips Air+ %s: MQTT connect failed: %s", self.device_id, err)
            self.coordinator.set_connection_state(connected=False, error=str(err))
            self._schedule_reconnect()
            return False

        client.loop_start()

        # Wait for CONNACK on the loop thread (the event is set from paho thread).
        try:
            got = await self.hass.async_add_executor_job(self._connect_event.wait)
        except Exception:  # noqa: BLE001
            got = False
        if not got or not self._connected:
            _LOGGER.warning("Philips Air+ %s: no CONNACK within timeout", self.device_id)
            self.coordinator.set_connection_state(connected=False, error="no CONNACK")
            self._schedule_reconnect()
            return False

        self._reconnect_delay = RECONNECT_MIN
        return True

    def _fetch_mqtt_info(self) -> dict:
        jwt = self.auth_data.get_jwt()
        info = auth.get_mqtt_info(jwt, [self.device_id])
        if self.device_id not in info:
            raise RuntimeError(f"mqttInfo returned no entry for {self.device_id}")
        mi = info[self.device_id]
        # mqttInfo provides host+path separately; endpoint is the full wss URL.
        return {
            "endpoint": mi.get("endpoint") or mi["host"],
            "path": mi["path"],
            "client_id": mi["client_id"],
        }

    # ----------------------------------------------------------- paho callbacks (network thread)
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc != 0:
            _LOGGER.warning("Philips Air+ %s: CONNACK rejected rc=%s", self.device_id, rc)
            self._connected = False
            self._connect_event.set()   # unblock the waiter (it will see _connected False)
            return
        _LOGGER.info("Philips Air+ %s: connected (client_id=%s)", self.device_id, self._info["client_id"][:12] if self._info else "?")
        self._connected = True
        for tp in (
            self._topic_get_accepted,
            self._topic_get_rejected,
            self._topic_update_accepted,
            self._topic_update_rejected,
            self._topic_update_documents,
        ):
            client.subscribe(tp, qos=1)
        # Pull the current state immediately.
        self.request_shadow_get()
        self._connect_event.set()
        self.coordinator.set_connection_state(connected=True)

    def request_shadow_get(self) -> None:
        """Publish shadow/get to pull current reported state. paho publish is
        thread-safe/non-blocking; callable from the HA loop or the paho thread."""
        if self._client is None or not self._connected:
            return
        self._client.publish(self._topic_get, "{}", qos=1)

    def _on_connect_fail(self, client, userdata):
        _LOGGER.warning("Philips Air+ %s: paho connect_fail", self.device_id)
        self._connected = False
        self._connect_event.set()
        self.coordinator.set_connection_state(connected=False, error="connect_fail")

    def _on_disconnect(self, client, userdata, *args, **kwargs):
        was = self._connected
        self._connected = False
        rc = args[0] if args else kwargs.get("reason_code", "?")
        _LOGGER.info("Philips Air+ %s: disconnected rc=%s", self.device_id, rc)
        self.coordinator.set_connection_state(connected=False)
        # rc 128 = another client connected with same client_id (the phone app).
        # In any case, the single-use URL is now consumed -> fetch a fresh one.
        if was and not self._stopping:
            self._schedule_reconnect()

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            pl = json.loads(msg.payload.decode("utf-8", "replace"))
        except Exception:  # noqa: BLE001
            return
        reported = None
        if topic.endswith("/get/accepted"):
            reported = pl.get("state", {}).get("reported")
        elif topic.endswith("/get/rejected"):
            _LOGGER.warning("Philips Air+ %s: shadow/get rejected: %s", self.device_id, pl)
            return
        elif topic.endswith("/update/accepted"):
            # accepted carries desired or reported delta; not a full state. Ignore;
            # the following /update/documents delivers the merged reported state.
            return
        elif topic.endswith("/update/rejected"):
            _LOGGER.warning("Philips Air+ %s: shadow/update rejected: %s", self.device_id, pl)
            return
        elif topic.endswith("/update/documents"):
            # documents = {"previous":{...},"current":{"state":{"reported":{...}}}}
            cur = pl.get("current") if isinstance(pl, dict) else None
            if isinstance(cur, dict):
                reported = cur.get("state", {}).get("reported")
        if reported is not None:
            self._push_reported(reported)

    # -------------------------------------------------------------- loop bridge
    def _push_reported(self, reported: dict):
        """Called from the paho network thread; hop to the HA loop."""
        loop = self.hass.loop
        loop.call_soon_threadsafe(self._dispatch_reported, reported)

    def _dispatch_reported(self, reported: dict):
        """Runs on the HA loop: feed the coordinator and update entities."""
        self.coordinator.threadsafe_set_data(reported)

    # -------------------------------------------------------------- commands (HA loop)
    async def async_set_desired(self, desired: dict) -> None:
        """Publish a desired-state patch to the shadow (turn on/off, set speed, ...)."""
        if not self._connected:
            await self.async_connect()
        if not self._connected or self._client is None:
            from homeassistant.exceptions import HomeAssistantError
            raise HomeAssistantError(f"Philips Air+ {self.device_id} not connected")
        payload = json.dumps({"state": {"desired": desired}})
        _LOGGER.debug("Philips Air+ %s: publish desired %s", self.device_id, payload)
        # paho publish is thread-safe and non-blocking; safe to call from the loop.
        info = self._client.publish(self._topic_update, payload, qos=1)
        # Don't wait for PUBACK here — the device echoes reported via /update/documents,
        # which updates the coordinator and reflects in the entity state.

    # -------------------------------------------------------------- reconnect / shutdown
    def _schedule_reconnect(self):
        if self._stopping or self._reconnecting:
            return
        self._reconnecting = True
        self.hass.loop.call_soon_threadsafe(self._create_reconnect_task)

    def _create_reconnect_task(self):
        self.hass.async_create_task(self._reconnect())

    async def _reconnect(self):
        if self._stopping:
            self._reconnecting = False
            return
        delay = self._reconnect_delay
        self._reconnect_delay = min(self._reconnect_delay * 2, RECONNECT_MAX)
        _LOGGER.info("Philips Air+ %s: reconnecting in %ss", self.device_id, delay)
        try:
            await asyncio.sleep(delay)
            await self.async_connect()
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Philips Air+ %s: reconnect error: %s", self.device_id, err)
            self._schedule_reconnect()
        finally:
            self._reconnecting = False

    def _teardown_client(self):
        if self._client is None:
            return
        try:
            self._client.loop_stop()
        except Exception:  # noqa: BLE001
            pass
        try:
            self._client.disconnect()
        except Exception:  # noqa: BLE001
            pass
        self._client = None

    async def async_shutdown(self):
        self._stopping = True
        self._connected = False
        await self.hass.async_add_executor_job(self._teardown_client)