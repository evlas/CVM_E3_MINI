"""Binary sensor platform for Circutor CVM-E3-MINI integration."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CvmE3MiniCoordinator


@dataclass(frozen=True)
class CvmBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing CVM-E3-MINI binary sensor entities."""


BINARY_SENSOR_DESCRIPTIONS: tuple[CvmBinarySensorEntityDescription, ...] = (
    CvmBinarySensorEntityDescription(
        key="phase_rotation_error",
        translation_key="phase_rotation_error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmBinarySensorEntityDescription(
        key="quadrant_consumed",
        translation_key="quadrant_consumed",
        icon="mdi:transmission-tower-import",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmBinarySensorEntityDescription(
        key="quadrant_generated",
        translation_key="quadrant_generated",
        icon="mdi:transmission-tower-export",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmBinarySensorEntityDescription(
        key="quadrant_inductive",
        translation_key="quadrant_inductive",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmBinarySensorEntityDescription(
        key="quadrant_capacitive",
        translation_key="quadrant_capacitive",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Circutor CVM-E3-MINI binary sensors."""
    coordinator: CvmE3MiniCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        CvmE3MiniBinarySensor(coordinator, desc, entry.entry_id)
        for desc in BINARY_SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class CvmE3MiniBinarySensor(CoordinatorEntity[CvmE3MiniCoordinator], BinarySensorEntity):
    """Representation of a Circutor CVM-E3-MINI binary sensor."""

    entity_description: CvmBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CvmE3MiniCoordinator,
        description: CvmBinarySensorEntityDescription,
        entry_id: str,
    ) -> None:
        """Initialize binary sensor."""
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

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.entity_description.key)
