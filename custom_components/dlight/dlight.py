"""Config flow for dlight."""
import asyncio
from collections.abc import Coroutine
import contextlib
from contextlib import contextmanager
from dataclasses import dataclass
import json
import logging
import math
import random
import socket
import threading
import time
from typing import Any, Text, Union

from homeassistant.components import network
from homeassistant.core import HomeAssistant

from .const import MAGIC_DISCOVERY_STRING

_LOGGER = logging.getLogger(__name__)


class _TimeoutLock:
    def __init__(self) -> None:
        self._lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        return self._lock.acquire(blocking, timeout)

    @contextmanager
    def acquire_timeout(self, timeout):
        result = self._lock.acquire(timeout=timeout)
        yield result
        if result:
            self._lock.release()


class _GlobalLockDict:
    def __init__(self) -> None:
        self._locks: dict[str, _TimeoutLock] = {}
        self._root_lock = _TimeoutLock()

    def get_lock(self, key) -> _TimeoutLock:
        with self._root_lock.acquire_timeout(1) as locked:
            if not locked:
                _LOGGER.error("FAILED TO AQUIRE GLOBAL LOCK")
                raise TimeoutError("FAILED TO AQUIRE GLOBAL LOCK")

            lock = self._locks.get(key)
            if not lock:
                lock = _TimeoutLock()
                self._locks[key] = lock
            return lock


# dLight's break if there is concurrent access, a global dict of locks is
# keyed on deviceId to ensure a single device is never accessed concurrently
_DEVICE_LOCKS = _GlobalLockDict()


@dataclass(frozen=True)
class DLightDiscovery:
    """Lamp Discovery Response model."""

    addr: str
    device_id: str
    sw_version: str
    hw_version: str
    device_model: str


Address = tuple[str, int]


class _BroadcastProtocol(asyncio.DatagramProtocol):
    def __init__(self, devices: set) -> None:
        self._devices = devices
        self._sockname = None

    def connection_made(self, transport: asyncio.transports.DatagramTransport):
        self._sockname = transport.get_extra_info("sockname")
        sock = transport.get_extra_info("socket")  # type: socket.socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        _LOGGER.debug("%s: Connected UDP transport", self._sockname)

    def datagram_received(self, data: Union[bytes, Text], addr: Address):
        try:
            device_json = json.loads(data)
            device = DLightDiscovery(**device_json, addr=addr[0])
            if device not in self._devices:
                self._devices.add(device)
                _LOGGER.info("%s: Found: %s", self._sockname, device)
        except ValueError as err:
            _LOGGER.error(
                "%s: Error handling data\n\t%s", self._sockname, data, exc_info=err
            )


async def discover_devices_on_ip(ip: str, devices: set) -> None:
    """Return if there are devices that can be discovered."""

    loop = asyncio.get_event_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: _BroadcastProtocol(devices), local_addr=(ip, 9487)
    )

    try:
        # sleep 0-100ms to jitter initial broadcast
        await asyncio.sleep(random.randrange(0, 10) / 100)

        start = time.time()
        while (len(devices) == 0 and (time.time() - start) < 1) or (
            len(devices) > 0 and (time.time() - start) < 1
        ):
            _LOGGER.info(
                "%s: Broadcasting Discovery", transport.get_extra_info("sockname")
            )
            transport.sendto(MAGIC_DISCOVERY_STRING, ("255.255.255.255", 9478))

            # sleep 1s with +-100ms jitter
            await asyncio.sleep(random.randrange(90, 110) / 100)
    finally:
        transport.close()


async def discover_devices(hass: HomeAssistant) -> list[DLightDiscovery]:
    """Return if there are devices that can be discovered."""
    # Set to collect discovered devices in
    devices = set()

    discovery: list[Coroutine[Any, Any, None]] = []
    adapters = await network.async_get_adapters(hass)
    for adapter in adapters:
        for ip_info in adapter["ipv4"]:
            local_ip = ip_info["address"]
            discovery.append(discover_devices_on_ip(local_ip, devices))

    # Wait for all discovery to complete
    await asyncio.gather(*discovery)

    _LOGGER.info("Discovered: %s", devices)
    return list(devices)


def _get_query_device_info(device_id: str) -> dict[str, Any]:
    """Query to get device discovery info."""
    return {
        "commandId": "1",
        "deviceId": device_id,
        "commandType": "QUERY_DEVICE_INFO",
    }


def _get_query_device_states(device_id: str) -> dict[str, Any]:
    """Query to get device states."""
    return {
        "commandId": "2",
        "deviceId": device_id,
        "commandType": "QUERY_DEVICE_STATES",
    }


def _get_execute(device_id: str, commands: dict[str, Any]) -> dict[str, Any]:
    """Query to execute commands."""
    return {
        "commandId": "3",
        "deviceId": device_id,
        "commandType": "EXECUTE",
        "commands": [commands],
    }


def _make_call(host: str, query):
    _LOGGER.debug("_make_call(%s, %s)", host, query)
    start_time = time.time()

    device_id = query["deviceId"]
    _LOGGER.debug("%s: Aquiring lock for %s", host, device_id)
    with _DEVICE_LOCKS.get_lock(device_id).acquire_timeout(2) as locked:
        if not locked:
            _LOGGER.error("%s: Timeout aquiring lock for %s", host, device_id)
            return {"status": "TIMEOUT"}

        _LOGGER.debug("%s: Locked %s", host, device_id)
        jquery = json.dumps(query)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                _LOGGER.debug("_make_call Start Connect")
                # Socket timeouts with dLight are BAD as unclean connection shutdown locks up the
                # light's API server
                s.settimeout(60)  # 60s timeout

                s.connect((host, 3333))
                _LOGGER.debug("%s: Connected, Sending Command:\n\t%s", host, jquery)
                s.sendall(bytes(jquery, encoding="UTF-8"))
                _LOGGER.debug("%s: Sent Command:\n\t%s", host, jquery)

                data = s.recv(1024)
                recv = data.decode("UTF-8")
                _LOGGER.debug("%s: Received Response:\n\t%s", host, recv)

                jRecv = json.loads(recv[4:])
                _LOGGER.debug("%s: Command Response:\n\t%s", host, jRecv)
                return jRecv

            except TimeoutError as err:
                _LOGGER.error(
                    "_make_call(%s[%s]) Timed Out", host, device_id, exc_info=err
                )
                return {"status": "TIMEOUT"}
            except ConnectionRefusedError as err:
                _LOGGER.error(
                    "_make_call(%s[%s]) Connection Refused",
                    host,
                    device_id,
                    exc_info=err,
                )
                return {"status": "TIMEOUT"}
            except OSError as err:
                _LOGGER.error(
                    "_make_call(%s[%s]) Failed with an unknown error",
                    host,
                    device_id,
                    exc_info=err,
                )
                return {"status": "UNKNOWN"}
            finally:
                try:
                    _LOGGER.debug("_make_call shutdown")
                    # dLight is VERY sensitive to early-closed sockets, signal a shutdown then do another
                    # read with a 20ms timeout, then explicitly close the socket
                    s.shutdown(socket.SHUT_WR)
                    s.settimeout(20 / 1000)
                    with contextlib.suppress(OSError):
                        s.recv(1024)
                    _LOGGER.debug("_make_call close")
                    s.close()
                    _LOGGER.debug("_make_call closed")
                except OSError as err:
                    _LOGGER.debug(
                        "_make_call(%s[%s]) cleanup failed:",
                        host,
                        device_id,
                        exc_info=err,
                    )

                _LOGGER.debug(
                    "_make_call complete in %sms",
                    math.floor((time.time() - start_time) * 1000),
                )


def get_state(host: str, device_id: str) -> dict[str, Any]:
    """Get state of light."""
    query = _get_query_device_states(device_id)
    return _make_call(host, query)


def set_values(host: str, device_id: str, commands: dict[str, Any]) -> dict[str, Any]:
    """Set state of light."""
    query = _get_execute(device_id, commands)
    return _make_call(host, query)


def get_device_info(host: str, device_id: str) -> DLightDiscovery:
    """Get device information."""
    query = _get_query_device_info(device_id)
    result: dict[str, Any] = _make_call(host, query)
    if result["status"] != "SUCCESS":
        raise Exception("Failed to connect to: %s", host)

    return DLightDiscovery(
        addr=host,
        device_id=result["deviceId"],
        sw_version=result["swVersion"],
        hw_version=result["hwVersion"],
        device_model=result["deviceModel"],
    )
