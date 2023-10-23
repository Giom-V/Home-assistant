"""Config flow for dlight."""
import asyncio
import json
import logging
import socket
import time
import random

from collections.abc import Coroutine
from dataclasses import dataclass
from typing import Union, Text, Any


from homeassistant.core import HomeAssistant
from homeassistant.components import network

from .const import MAGIC_DISCOVERY_STRING

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DLightDiscovery(object):
    """Lamp Discovery Response model"""

    addr: str
    deviceId: str
    swVersion: str
    hwVersion: str
    deviceModel: str


Address = tuple[str, int]


class BroadcastProtocol(asyncio.DatagramProtocol):
    def __init__(self, devices: set) -> None:
        self._devices = devices
        self._sockname = None

    def connection_made(self, transport: asyncio.transports.DatagramTransport):
        self._sockname = transport.get_extra_info("sockname")
        sock = transport.get_extra_info("socket")  # type: socket.socket
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        _LOGGER.info("%s: Connected UDP transport", self._sockname)

    def datagram_received(self, data: Union[bytes, Text], addr: Address):
        try:
            device_json = json.loads(data)
            device = DLightDiscovery(**device_json, addr=addr[0])
            if device not in self._devices:
                self._devices.add(device)
                _LOGGER.info("%s: Found: %s", self._sockname, device)
        except ValueError as err:
            _LOGGER.error("%s: Error handling data %s\n%s", self._sockname, err, data)


class DLightRequestUnsuccessfulException(Exception):
    pass


async def discover_devices_on_ip(ip: str, devices: set) -> None:
    """Return if there are devices that can be discovered."""

    loop = asyncio.get_event_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: BroadcastProtocol(devices), local_addr=(ip, 9487)
    )

    try:
        # sleep 0-100ms to jitter initial broadcast
        await asyncio.sleep(random.randrange(0, 10) / 100)

        start = time.time()
        while (len(devices) == 0 and (time.time() - start) < 9) or (
            len(devices) > 0 and (time.time() - start) < 3
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
    """Query to get device discovery info"""
    return {
        "commandId": "1",
        "deviceId": device_id,
        "commandType": "QUERY_DEVICE_INFO",
    }


def _get_query_device_states(device_id: str) -> dict[str, Any]:
    """Query to get device states"""
    return {
        "commandId": "2",
        "deviceId": device_id,
        "commandType": "QUERY_DEVICE_STATES",
    }


def _get_execute(device_id: str, commands: dict[str, Any]) -> dict[str, Any]:
    """Executes Commands"""
    return {
        "commandId": "3",
        "deviceId": device_id,
        "commandType": "EXECUTE",
        "commands": [commands],
    }


async def _make_call(device: DLightDiscovery, query):
    jquery = json.dumps(query)

    reader, writer = await asyncio.open_connection(device.addr, 3333)
    writer.write(bytes(jquery, encoding="UTF-8"))

    try:
        await writer.drain()
        data = await reader.read(8 * 1024)
    except asyncio.CancelledError as e:
        _LOGGER.warn("Call canceled after connection was made.")
        writer.close()
        raise e

    recv = data.decode("UTF-8")

    writer.close()
    await writer.wait_closed()

    response = json.loads(recv[4:])

    if response["status"] != "SUCCESS":
        raise DLightRequestUnsuccessfulException

    return response



async def get_state(device: DLightDiscovery) -> dict[str, Any]:
    """Get state of light"""
    query = _get_query_device_states(device.deviceId)
    return await asyncio.wait_for(_make_call(device, query), timeout=3.0)


async def set_values(
    device: DLightDiscovery, commands: dict[str, Any]
) -> dict[str, Any]:
    """Set state of light"""
    query = _get_execute(device.deviceId, commands)
    return await asyncio.wait_for(_make_call(device, query), timeout=5.0)