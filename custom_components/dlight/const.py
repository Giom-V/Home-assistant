"""Constants for the dlight integration."""
from __future__ import annotations

from datetime import timedelta
import logging
import math
from typing import Final

DOMAIN: Final = "dlight"

CONF_DISCOVERY: Final = "discovery"
CONF_DISCOVERED_LIGHTS: Final = "discovered_lights"
CONF_MANUAL: Final = "MANUAL"

MAGIC_DISCOVERY_STRING: Final = b"476f6f676c654e50455f457269635f5761796e65"

LOGGER = logging.getLogger(__package__)
SCAN_INTERVAL = timedelta(seconds=10)
MAX_TIMEOUT_BACKOFF_COUNT = math.ceil(timedelta(minutes=2) / timedelta(seconds=7))
