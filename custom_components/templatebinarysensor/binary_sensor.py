"""Sensor platform for templatebinarysensor."""
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import template as templater


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([CustomTemplateBinarySensor(hass, config_entry)], True)


class CustomTemplateBinarySensor(Entity):
    """CustomTemplateBinarySensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.config = config
        self._state = None

    async def async_update(self):
        """Update the sensor."""
        try:
            state = templater.Template(
                self.config.data.get("template"), self.hass
            ).async_render()
            if state == "True":
                self._state = "on"
            else:
                self._state = "off"
        except Exception:
            self._state = self._state

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self.config.entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.config.data.get("name")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_class(self):
        """Return the device_class of the sensor."""
        return self.config.data.get("device_class")

