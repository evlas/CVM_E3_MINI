"""Select platform for Circutor CVM-E3-MINI integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, REG_BACKLIGHT, REG_TARIFF_SELECT
from .coordinator import CvmE3MiniCoordinator

_LOGGER = logging.getLogger(__name__)

TARIFF_OPTIONS = ["Tariffa 1", "Tariffa 2"]
BACKLIGHT_OPTIONS = ["Sempre Acceso", "Temporizzato"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Circutor CVM-E3-MINI selects."""
    coordinator: CvmE3MiniCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CvmE3MiniTariffSelect(coordinator, entry.entry_id),
        CvmE3MiniBacklightSelect(coordinator, entry.entry_id),
    ]

    async_add_entities(entities)


class CvmE3MiniTariffSelect(CoordinatorEntity[CvmE3MiniCoordinator], SelectEntity):
    """Representation of Tariff selection entity."""

    def __init__(self, coordinator: CvmE3MiniCoordinator, entry_id: str) -> None:
        """Initialize select entity."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Selezione Tariffa"
        device_id = coordinator.serial_number or entry_id
        self._attr_unique_id = f"{device_id}_tariff_select"
        self._attr_options = TARIFF_OPTIONS
        self._attr_current_option = TARIFF_OPTIONS[0]
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_icon = "mdi:calendar-clock"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device_id = self.coordinator.serial_number or self.coordinator.entry_data.get("unique_id", "cvm_e3_mini")
        return DeviceInfo(
            identifiers={(DOMAIN, str(device_id))},
            name="Circutor CVM-E3-MINI",
            manufacturer="Circutor",
            model="CVM-E3-MINI",
            serial_number=self.coordinator.serial_number,
        )

    async def async_select_option(self, option: str) -> None:
        """Change selected option."""
        val = 0 if option == "Tariffa 1" else 1
        success = await self.coordinator.write_register(REG_TARIFF_SELECT, val)
        if success:
            self._attr_current_option = option
            self.async_write_ha_state()


class CvmE3MiniBacklightSelect(CoordinatorEntity[CvmE3MiniCoordinator], SelectEntity):
    """Representation of Backlight mode entity."""

    def __init__(self, coordinator: CvmE3MiniCoordinator, entry_id: str) -> None:
        """Initialize backlight entity."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True
        self._attr_name = "Retroilluminazione Display"
        device_id = coordinator.serial_number or entry_id
        self._attr_unique_id = f"{device_id}_backlight_select"
        self._attr_options = BACKLIGHT_OPTIONS
        self._attr_current_option = BACKLIGHT_OPTIONS[0]
        self._attr_entity_category = EntityCategory.CONFIG
        self._attr_icon = "mdi:brightness-6"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        device_id = self.coordinator.serial_number or self.coordinator.entry_data.get("unique_id", "cvm_e3_mini")
        return DeviceInfo(
            identifiers={(DOMAIN, str(device_id))},
            name="Circutor CVM-E3-MINI",
            manufacturer="Circutor",
            model="CVM-E3-MINI",
            serial_number=self.coordinator.serial_number,
        )

    async def async_select_option(self, option: str) -> None:
        """Change selected option."""
        val = 0 if option == "Sempre Acceso" else 1
        success = await self.coordinator.write_register(REG_BACKLIGHT, val)
        if success:
            self._attr_current_option = option
            self.async_write_ha_state()
