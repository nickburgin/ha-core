"""Platform for light integration."""
import logging

import voluptuous as vol

# Import the device class from the component that you want to support
from homeassistant.components.light import ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .wiz import WizDevice

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up WiZ lights based on a config entry."""
    await platform_async_setup_entry(hass, entry, async_add_entities)


async def platform_async_setup_entry(hass, entry, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = entry.data[CONF_HOST]

    # Setup connection with devices/cloud
    dev = WizDevice(host)

    # Verify that passed in configuration works
    if not await dev.connect():
        _LOGGER.error("Could not connect to WiZ Device with address: " + host)
        return

    # Add devices
    add_entities([WizLight(dev)])


class WizLight(LightEntity):
    """Representation of an WiZ Light."""

    def __init__(self, device):
        """Initialize an AwesomeLight."""
        self._device = device
        self._name = device.name()
        self._state = None
        self._brightness = None

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        self._device.set_brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._device.turn_on()

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        self._device.turn_off()

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._device.update()
        self._state = self._device.is_on()
        self._brightness = self._device.brightness
