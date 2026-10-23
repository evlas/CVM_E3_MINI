"""Base entity for Circutor CVM-E3-MINI."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CvmE3MiniCoordinator


class CvmE3MiniEntity(CoordinatorEntity[CvmE3MiniCoordinator]):
    """Defines a base CVM-E3-MINI entity."""

    _attr_has_entity_name = True

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
            sw_version=self.coordinator.version or "0.0.5",
        )
