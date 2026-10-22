"""Button platform for Circutor CVM-E3-MINI integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COIL_RESET_ALL_PARAMETERS,
    COIL_RESET_ENERGY_ALL,
    COIL_RESET_ENERGY_THREEPHASE,
    DOMAIN,
)
from .coordinator import CvmE3MiniCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class CvmButtonEntityDescription(ButtonEntityDescription):
    """Class describing CVM-E3-MINI button entities."""

    coil_address: int = 0


BUTTON_DESCRIPTIONS: tuple[CvmButtonEntityDescription, ...] = (
    CvmButtonEntityDescription(
        key="reset_energy_threephase",
        translation_key="reset_energy_threephase",
        icon="mdi:counter",
        entity_category=EntityCategory.CONFIG,
        coil_address=COIL_RESET_ENERGY_THREEPHASE,
    ),
    CvmButtonEntityDescription(
        key="reset_energy_all",
        translation_key="reset_energy_all",
        icon="mdi:restore-alert",
        entity_category=EntityCategory.CONFIG,
        coil_address=COIL_RESET_ENERGY_ALL,
    ),
    CvmButtonEntityDescription(
        key="reset_all_parameters",
        translation_key="reset_all_parameters",
        icon="mdi:delete-alert",
        entity_category=EntityCategory.CONFIG,
        coil_address=COIL_RESET_ALL_PARAMETERS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Circutor CVM-E3-MINI buttons."""
    coordinator: CvmE3MiniCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CvmE3MiniButton(coordinator, desc, entry.entry_id)
        for desc in BUTTON_DESCRIPTIONS
    ]

    async_add_entities(entities)


class CvmE3MiniButton(CoordinatorEntity[CvmE3MiniCoordinator], ButtonEntity):
    """Representation of a Circutor CVM-E3-MINI control button."""

    entity_description: CvmButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CvmE3MiniCoordinator,
        description: CvmButtonEntityDescription,
        entry_id: str,
    ) -> None:
        """Initialize button."""
        super().__init__(coordinator)
        self.entity_description = description
        device_id = coordinator.serial_number or entry_id
        self._attr_unique_id = f"{device_id}_{description.key}"

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

    async def async_press(self) -> None:
        """Handle button press."""
        coil = self.entity_description.coil_address
        _LOGGER.info("Executing reset command on coil %s (%s)", hex(coil), self.entity_description.key)
        success = await self.coordinator.write_coil(coil, True)
        if success:
            await self.coordinator.async_request_refresh()
