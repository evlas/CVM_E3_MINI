"""Sensor platform for Circutor CVM-E3-MINI integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    PERCENTAGE,
    UnitOfApparentPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_WIRING_SYSTEM,
    DOMAIN,
    WIRING_1P2W,
    WIRING_3P3W,
    WIRING_3P4W,
)
from .coordinator import CvmE3MiniCoordinator
from .entity import CvmE3MiniEntity


@dataclass(frozen=True)
class CvmSensorEntityDescription(SensorEntityDescription):
    """Class describing CVM-E3-MINI sensor entities."""

    wiring_supported: tuple[str, ...] = (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)
    translation_placeholders: dict[str, str] | None = None


SENSOR_DESCRIPTIONS: tuple[CvmSensorEntityDescription, ...] = (
    # --- VOLTAGES ---
    CvmSensorEntityDescription(
        key="voltage_l1",
        translation_key="voltage_l1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="voltage_l2",
        translation_key="voltage_l2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l3",
        translation_key="voltage_l3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l1_l2",
        translation_key="voltage_l1_l2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l2_l3",
        translation_key="voltage_l2_l3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l3_l1",
        translation_key="voltage_l3_l1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- CURRENTS ---
    CvmSensorEntityDescription(
        key="current_l1",
        translation_key="current_l1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
    ),
    CvmSensorEntityDescription(
        key="current_l2",
        translation_key="current_l2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="current_l3",
        translation_key="current_l3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="current_neutral",
        translation_key="current_neutral",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        wiring_supported=(WIRING_3P4W,),
    ),

    # --- ACTIVE POWERS ---
    CvmSensorEntityDescription(
        key="power_active_total",
        translation_key="power_active_total",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    CvmSensorEntityDescription(
        key="power_active_l1",
        translation_key="power_active_l1",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    CvmSensorEntityDescription(
        key="power_active_l2",
        translation_key="power_active_l2",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_active_l3",
        translation_key="power_active_l3",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- REACTIVE INDUCTIVE POWERS ---
    CvmSensorEntityDescription(
        key="power_reactive_ind_total",
        translation_key="power_reactive_ind_total",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
    ),
    CvmSensorEntityDescription(
        key="power_reactive_ind_l1",
        translation_key="power_reactive_ind_l1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_reactive_ind_l2",
        translation_key="power_reactive_ind_l2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_reactive_ind_l3",
        translation_key="power_reactive_ind_l3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- REACTIVE CAPACITIVE POWERS ---
    CvmSensorEntityDescription(
        key="power_reactive_cap_total",
        translation_key="power_reactive_cap_total",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
    ),
    CvmSensorEntityDescription(
        key="power_reactive_cap_l1",
        translation_key="power_reactive_cap_l1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_reactive_cap_l2",
        translation_key="power_reactive_cap_l2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_reactive_cap_l3",
        translation_key="power_reactive_cap_l3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- APPARENT POWERS ---
    CvmSensorEntityDescription(
        key="power_apparent_total",
        translation_key="power_apparent_total",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
    ),
    CvmSensorEntityDescription(
        key="power_apparent_l1",
        translation_key="power_apparent_l1",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_apparent_l2",
        translation_key="power_apparent_l2",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_apparent_l3",
        translation_key="power_apparent_l3",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- POWER FACTOR ---
    CvmSensorEntityDescription(
        key="power_factor_total",
        translation_key="power_factor_total",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    CvmSensorEntityDescription(
        key="power_factor_l1",
        translation_key="power_factor_l1",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_factor_l2",
        translation_key="power_factor_l2",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_factor_l3",
        translation_key="power_factor_l3",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- COS PHI ---
    CvmSensorEntityDescription(
        key="cos_phi_total",
        translation_key="cos_phi_total",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
    ),
    CvmSensorEntityDescription(
        key="cos_phi_l1",
        translation_key="cos_phi_l1",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="cos_phi_l2",
        translation_key="cos_phi_l2",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="cos_phi_l3",
        translation_key="cos_phi_l3",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=0,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- FREQUENCY ---
    CvmSensorEntityDescription(
        key="frequency",
        translation_key="frequency",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        suggested_display_precision=2,
    ),

    # --- HARMONICS / THD ---
    CvmSensorEntityDescription(
        key="thd_voltage_l1",
        translation_key="thd_voltage_l1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="thd_voltage_l2",
        translation_key="thd_voltage_l2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="thd_voltage_l3",
        translation_key="thd_voltage_l3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="thd_current_l1",
        translation_key="thd_current_l1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="thd_current_l2",
        translation_key="thd_current_l2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="thd_current_l3",
        translation_key="thd_current_l3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- ENERGIES CONSUMED (HA ENERGY DASHBOARD) ---
    CvmSensorEntityDescription(
        key="energy_active_consumed_total",
        translation_key="energy_active_consumed_total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_ind_consumed_total",
        translation_key="energy_reactive_ind_consumed_total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=3,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_cap_consumed_total",
        translation_key="energy_reactive_cap_consumed_total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=3,
    ),
    CvmSensorEntityDescription(
        key="energy_apparent_consumed_total",
        translation_key="energy_apparent_consumed_total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kVAh",
        suggested_display_precision=3,
    ),

    # --- ENERGIES GENERATED ---
    CvmSensorEntityDescription(
        key="energy_active_generated_total",
        translation_key="energy_active_generated_total",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_ind_generated_total",
        translation_key="energy_reactive_ind_generated_total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=3,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_cap_generated_total",
        translation_key="energy_reactive_cap_generated_total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=3,
    ),
    CvmSensorEntityDescription(
        key="energy_apparent_generated_total",
        translation_key="energy_apparent_generated_total",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kVAh",
        suggested_display_precision=3,
    ),

    # --- INTERNAL TEMPERATURE ---
    CvmSensorEntityDescription(
        key="internal_temperature",
        translation_key="internal_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # --- OPERATING HOURS ---
    CvmSensorEntityDescription(
        key="operating_hours_total",
        translation_key="operating_hours_total",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


# Dynamically generate Harmonic entity descriptions (disabled by default)
HARMONIC_DESCRIPTIONS: list[CvmSensorEntityDescription] = []
for phase, p_name, w_sup in [
    ("l1", "L1", (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("l2", "L2", (WIRING_3P4W, WIRING_3P3W)),
    ("l3", "L3", (WIRING_3P4W, WIRING_3P3W)),
]:
    HARMONIC_DESCRIPTIONS.append(
        CvmSensorEntityDescription(
            key=f"voltage_fundamental_{phase}",
            translation_key=f"voltage_fundamental_{phase}",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            suggested_display_precision=1,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            wiring_supported=w_sup,
        )
    )
    HARMONIC_DESCRIPTIONS.append(
        CvmSensorEntityDescription(
            key=f"current_fundamental_{phase}",
            translation_key=f"current_fundamental_{phase}",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            suggested_display_precision=2,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            wiring_supported=w_sup,
        )
    )
    for h in range(2, 32):
        HARMONIC_DESCRIPTIONS.append(
            CvmSensorEntityDescription(
                key=f"harmonic_v_{phase}_h{h}",
                translation_key="voltage_harmonic",
                translation_placeholders={"phase": p_name, "order": str(h)},
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement="%",
                suggested_display_precision=1,
                entity_category=EntityCategory.DIAGNOSTIC,
                entity_registry_enabled_default=False,
                wiring_supported=w_sup,
            )
        )
        HARMONIC_DESCRIPTIONS.append(
            CvmSensorEntityDescription(
                key=f"harmonic_i_{phase}_h{h}",
                translation_key="current_harmonic",
                translation_placeholders={"phase": p_name, "order": str(h)},
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement="%",
                suggested_display_precision=1,
                entity_category=EntityCategory.DIAGNOSTIC,
                entity_registry_enabled_default=False,
                wiring_supported=w_sup,
            )
        )

ALL_SENSOR_DESCRIPTIONS: list[CvmSensorEntityDescription] = (
    list(SENSOR_DESCRIPTIONS) + HARMONIC_DESCRIPTIONS
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Circutor CVM-E3-MINI sensors."""
    coordinator: CvmE3MiniCoordinator = hass.data[DOMAIN][entry.entry_id]
    wiring = entry.options.get(
        CONF_WIRING_SYSTEM, entry.data.get(CONF_WIRING_SYSTEM, WIRING_3P4W)
    )

    entities = [
        CvmE3MiniSensor(coordinator, desc, entry.entry_id)
        for desc in ALL_SENSOR_DESCRIPTIONS
        if wiring in desc.wiring_supported
    ]

    async_add_entities(entities)


class CvmE3MiniSensor(CvmE3MiniEntity, SensorEntity):
    """Representation of a Circutor CVM-E3-MINI sensor."""

    entity_description: CvmSensorEntityDescription

    def __init__(
        self,
        coordinator: CvmE3MiniCoordinator,
        description: CvmSensorEntityDescription,
        entry_id: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        if description.translation_placeholders:
            self._attr_translation_placeholders = description.translation_placeholders
        device_id = coordinator.serial_number or entry_id
        self._attr_unique_id = f"{device_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return native value of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
