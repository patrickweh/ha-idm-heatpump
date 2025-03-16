"""Device definition for iDM Heat Pump integration."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

class IdmHeatPumpDevice(Entity):
    """Representation of an iDM Heat Pump device."""

    def __init__(self, coordinator, entry_id):
        """Initialize the device."""
        self._coordinator = coordinator
        self._entry_id = entry_id
        self._device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": DEFAULT_NAME,
            "manufacturer": "iDM Energiesysteme GmbH",
            "model": "Navigator 2.0",
            "sw_version": coordinator.data.get("sw_version", "Unknown"),
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self._device_info

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._coordinator.last_update_success