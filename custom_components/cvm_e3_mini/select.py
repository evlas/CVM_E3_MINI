"""Select platform for Circutor CVM-E3-MINI integration."""

from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, REG_BACKLIGHT
from .coordinator import CvmE3MiniCoordinator
from .entity import CvmE3MiniEntity

_LOGGER = logging.getLogger(__name__)

BACKLIGHT_OPTIONS = ["always_on", "timed"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Circutor CVM-E3-MINI selects."""
    coordinator: CvmE3MiniCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CvmE3MiniBacklightSelect(coordinator, entry.entry_id),
    ]

    async_add_entities(entities)


class CvmE3MiniBacklightSelect(CvmE3MiniEntity, SelectEntity):
    """Representation of Backlight mode entity."""

    _attr_translation_key = "backlight"

    def __init__(self, coordinator: CvmE3MiniCoordinator, entry_id: str) -> None:
        """Initialize backlight entity."""
        super().__init__(coordinator)
        device_id = coordinator.serial_number or entry_id
        self._attr_unique_id = f"{device_id}_backlight_select"
        self._attr_options = BACKLIGHT_OPTIONS
        self._attr_current_option = BACKLIGHT_OPTIONS[0]
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_icon = "mdi:brightness-6"

    async def async_select_option(self, option: str) -> None:
        """Change selected option."""
        val = 0 if option == "always_on" else 1
        success = await self.coordinator.write_register(REG_BACKLIGHT, val)
        if success:
            self._attr_current_option = option
            self.async_write_ha_state()
