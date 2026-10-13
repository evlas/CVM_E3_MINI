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


@dataclass(frozen=True)
class CvmSensorEntityDescription(SensorEntityDescription):
    """Class describing CVM-E3-MINI sensor entities."""

    wiring_supported: tuple[str, ...] = (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)


SENSOR_DESCRIPTIONS: tuple[CvmSensorEntityDescription, ...] = (
    # --- VOLTAGES ---
    CvmSensorEntityDescription(
        key="voltage_l1",
        name="Tensione L1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="voltage_l2",
        name="Tensione L2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l3",
        name="Tensione L3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l1_l2",
        name="Tensione Concatenata L1-L2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l2_l3",
        name="Tensione Concatenata L2-L3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="voltage_l3_l1",
        name="Tensione Concatenata L3-L1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- CURRENTS ---
    CvmSensorEntityDescription(
        key="current_l1",
        name="Corrente L1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
    ),
    CvmSensorEntityDescription(
        key="current_l2",
        name="Corrente L2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="current_l3",
        name="Corrente L3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="current_neutral",
        name="Corrente di Neutro",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        wiring_supported=(WIRING_3P4W,),
    ),

    # --- POWERS ---
    CvmSensorEntityDescription(
        key="power_active_total",
        name="Potenza Attiva Totale",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    CvmSensorEntityDescription(
        key="power_active_l1",
        name="Potenza Attiva L1",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    CvmSensorEntityDescription(
        key="power_active_l2",
        name="Potenza Attiva L2",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_active_l3",
        name="Potenza Attiva L3",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_reactive_ind_total",
        name="Potenza Reattiva Induttiva Totale",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
    ),
    CvmSensorEntityDescription(
        key="power_reactive_ind_l1",
        name="Potenza Reattiva Induttiva L1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_reactive_ind_l2",
        name="Potenza Reattiva Induttiva L2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_reactive_ind_l3",
        name="Potenza Reattiva Induttiva L3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_reactive_cap_total",
        name="Potenza Reattiva Capacitiva Totale",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
    ),
    CvmSensorEntityDescription(
        key="power_reactive_cap_l1",
        name="Potenza Reattiva Capacitiva L1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_reactive_cap_l2",
        name="Potenza Reattiva Capacitiva L2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_reactive_cap_l3",
        name="Potenza Reattiva Capacitiva L3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_apparent_total",
        name="Potenza Apparente Totale",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
    ),
    CvmSensorEntityDescription(
        key="power_apparent_l1",
        name="Potenza Apparente L1",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_apparent_l2",
        name="Potenza Apparente L2",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_apparent_l3",
        name="Potenza Apparente L3",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_factor_total",
        name="Fattore di Potenza Totale",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    CvmSensorEntityDescription(
        key="power_factor_l1",
        name="Fattore di Potenza L1",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="power_factor_l2",
        name="Fattore di Potenza L2",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="power_factor_l3",
        name="Fattore di Potenza L3",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="cos_phi_total",
        name="Cos φ Totale",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    CvmSensorEntityDescription(
        key="cos_phi_l1",
        name="Cos φ L1",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="cos_phi_l2",
        name="Cos φ L2",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="cos_phi_l3",
        name="Cos φ L3",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- FREQUENCY ---
    CvmSensorEntityDescription(
        key="frequency",
        name="Frequenza di Rete",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        suggested_display_precision=2,
    ),

    # --- HARMONICS / THD ---
    CvmSensorEntityDescription(
        key="thd_voltage_l1",
        name="THD Tensione L1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="thd_voltage_l2",
        name="THD Tensione L2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="thd_voltage_l3",
        name="THD Tensione L3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="thd_current_l1",
        name="THD Corrente L1",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="thd_current_l2",
        name="THD Corrente L2",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="thd_current_l3",
        name="THD Corrente L3",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="%",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- MAX DEMANDS ---
    CvmSensorEntityDescription(
        key="max_demand_active_power",
        name="Massima Richiesta Potenza Attiva",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_apparent_power",
        name="Massima Richiesta Potenza Apparente",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_apparent_power_max",
        name="Massima Richiesta Potenza Apparente (Max)",
        device_class=SensorDeviceClass.APPARENT_POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_active_power_max",
        name="Massima Richiesta Potenza Attiva (Max)",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_reactive_ind_power",
        name="Massima Richiesta Potenza Reattiva Induttiva",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_reactive_ind_power_max",
        name="Massima Richiesta Potenza Reattiva Induttiva (Max)",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_reactive_cap_power",
        name="Massima Richiesta Potenza Reattiva Capacitiva",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_reactive_cap_power_max",
        name="Massima Richiesta Potenza Reattiva Capacitiva (Max)",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_current_l1",
        name="Massima Richiesta Corrente L1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_current_l1_max",
        name="Massima Richiesta Corrente L1 (Max)",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="max_demand_current_l2",
        name="Massima Richiesta Corrente L2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="max_demand_current_l2_max",
        name="Massima Richiesta Corrente L2 (Max)",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="max_demand_current_l3",
        name="Massima Richiesta Corrente L3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),
    CvmSensorEntityDescription(
        key="max_demand_current_l3_max",
        name="Massima Richiesta Corrente L3 (Max)",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
        wiring_supported=(WIRING_3P4W, WIRING_3P3W),
    ),

    # --- ENERGIES CONSUMED (HA ENERGY DASHBOARD & HIGH RES) ---
    CvmSensorEntityDescription(
        key="energy_active_consumed_total",
        name="Energia Attiva Consumata Totale",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_active_consumed_wh_total",
        name="Energia Attiva Consumata Totale (Wh)",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_ind_consumed_total",
        name="Energia Reattiva Induttiva Consumata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_ind_consumed_varh_total",
        name="Energia Reattiva Induttiva Consumata Totale (varh)",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_cap_consumed_total",
        name="Energia Reattiva Capacitiva Consumata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_cap_consumed_varh_total",
        name="Energia Reattiva Capacitiva Consumata Totale (varh)",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="energy_apparent_consumed_total",
        name="Energia Apparente Consumata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kVAh",
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_apparent_consumed_vah_total",
        name="Energia Apparente Consumata Totale (VAh)",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="VAh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # --- ENERGIES GENERATED ---
    CvmSensorEntityDescription(
        key="energy_active_generated_total",
        name="Energia Attiva Generata Totale",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_active_generated_wh_total",
        name="Energia Attiva Generata Totale (Wh)",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_ind_generated_total",
        name="Energia Reattiva Induttiva Generata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_ind_generated_varh_total",
        name="Energia Reattiva Induttiva Generata Totale (varh)",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_cap_generated_total",
        name="Energia Reattiva Capacitiva Generata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kvarh",
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_reactive_cap_generated_varh_total",
        name="Energia Reattiva Capacitiva Generata Totale (varh)",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="energy_apparent_generated_total",
        name="Energia Apparente Generata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kVAh",
        suggested_display_precision=1,
    ),
    CvmSensorEntityDescription(
        key="energy_apparent_generated_vah_total",
        name="Energia Apparente Generata Totale (VAh)",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="VAh",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # --- INTERNAL TEMPERATURE ---
    CvmSensorEntityDescription(
        key="internal_temperature",
        name="Temperatura Interna",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="internal_temperature_max",
        name="Temperatura Interna (Max)",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="internal_temperature_min",
        name="Temperatura Interna (Min)",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

    # --- DIGITAL INPUT PULSE COUNTER & CO2 / COST ---
    CvmSensorEntityDescription(
        key="pulse_counter",
        name="Contatore Impulsi Ingresso Digitale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="impulsi",
        icon="mdi:counter",
    ),
    CvmSensorEntityDescription(
        key="co2_consumed_total",
        name="Emissioni CO2 Consumate Totali",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kg",
        icon="mdi:molecule-co2",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="co2_generated_total",
        name="Emissioni CO2 Evitate Totali",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="kg",
        icon="mdi:molecule-co2",
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="cost_consumed_total",
        name="Costo Energia Consumata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:currency-eur",
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="cost_generated_total",
        name="Valore Energia Generata Totale",
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:currency-eur",
        suggested_display_precision=2,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    CvmSensorEntityDescription(
        key="operating_hours_total",
        name="Ore di Esercizio Totali",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.HOURS,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


# Dynamically generate Max and Min entity descriptions
MAX_MIN_BASE_VARS: list[tuple[str, str, SensorDeviceClass | None, str | None, int | None, tuple[str, ...]]] = [
    ("voltage_l1", "Tensione L1", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, 1, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("voltage_l2", "Tensione L2", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, 1, (WIRING_3P4W, WIRING_3P3W)),
    ("voltage_l3", "Tensione L3", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, 1, (WIRING_3P4W, WIRING_3P3W)),
    ("voltage_l1_l2", "Tensione Concatenata L1-L2", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, 1, (WIRING_3P4W, WIRING_3P3W)),
    ("voltage_l2_l3", "Tensione Concatenata L2-L3", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, 1, (WIRING_3P4W, WIRING_3P3W)),
    ("voltage_l3_l1", "Tensione Concatenata L3-L1", SensorDeviceClass.VOLTAGE, UnitOfElectricPotential.VOLT, 1, (WIRING_3P4W, WIRING_3P3W)),
    ("current_l1", "Corrente L1", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, 2, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("current_l2", "Corrente L2", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, 2, (WIRING_3P4W, WIRING_3P3W)),
    ("current_l3", "Corrente L3", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, 2, (WIRING_3P4W, WIRING_3P3W)),
    ("current_neutral", "Corrente di Neutro", SensorDeviceClass.CURRENT, UnitOfElectricCurrent.AMPERE, 2, (WIRING_3P4W,)),
    ("power_active_total", "Potenza Attiva Totale", SensorDeviceClass.POWER, UnitOfPower.WATT, None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_active_l1", "Potenza Attiva L1", SensorDeviceClass.POWER, UnitOfPower.WATT, None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_active_l2", "Potenza Attiva L2", SensorDeviceClass.POWER, UnitOfPower.WATT, None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_active_l3", "Potenza Attiva L3", SensorDeviceClass.POWER, UnitOfPower.WATT, None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_reactive_ind_total", "Potenza Reattiva Induttiva Totale", None, "var", None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_reactive_ind_l1", "Potenza Reattiva Induttiva L1", None, "var", None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_reactive_ind_l2", "Potenza Reattiva Induttiva L2", None, "var", None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_reactive_ind_l3", "Potenza Reattiva Induttiva L3", None, "var", None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_reactive_cap_total", "Potenza Reattiva Capacitiva Totale", None, "var", None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_reactive_cap_l1", "Potenza Reattiva Capacitiva L1", None, "var", None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_reactive_cap_l2", "Potenza Reattiva Capacitiva L2", None, "var", None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_reactive_cap_l3", "Potenza Reattiva Capacitiva L3", None, "var", None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_apparent_total", "Potenza Apparente Totale", SensorDeviceClass.APPARENT_POWER, UnitOfApparentPower.VOLT_AMPERE, None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_apparent_l1", "Potenza Apparente L1", SensorDeviceClass.APPARENT_POWER, UnitOfApparentPower.VOLT_AMPERE, None, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_apparent_l2", "Potenza Apparente L2", SensorDeviceClass.APPARENT_POWER, UnitOfApparentPower.VOLT_AMPERE, None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_apparent_l3", "Potenza Apparente L3", SensorDeviceClass.APPARENT_POWER, UnitOfApparentPower.VOLT_AMPERE, None, (WIRING_3P4W, WIRING_3P3W)),
    ("power_factor_total", "Fattore di Potenza Totale", SensorDeviceClass.POWER_FACTOR, None, 2, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_factor_l1", "Fattore di Potenza L1", SensorDeviceClass.POWER_FACTOR, None, 2, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("power_factor_l2", "Fattore di Potenza L2", SensorDeviceClass.POWER_FACTOR, None, 2, (WIRING_3P4W, WIRING_3P3W)),
    ("power_factor_l3", "Fattore di Potenza L3", SensorDeviceClass.POWER_FACTOR, None, 2, (WIRING_3P4W, WIRING_3P3W)),
    ("cos_phi_total", "Cos φ Totale", None, None, 2, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("cos_phi_l1", "Cos φ L1", None, None, 2, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("cos_phi_l2", "Cos φ L2", None, None, 2, (WIRING_3P4W, WIRING_3P3W)),
    ("cos_phi_l3", "Cos φ L3", None, None, 2, (WIRING_3P4W, WIRING_3P3W)),
    ("frequency", "Frequenza di Rete", SensorDeviceClass.FREQUENCY, UnitOfFrequency.HERTZ, 2, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("thd_voltage_l1", "THD Tensione L1", None, "%", 1, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("thd_voltage_l2", "THD Tensione L2", None, "%", 1, (WIRING_3P4W, WIRING_3P3W)),
    ("thd_voltage_l3", "THD Tensione L3", None, "%", 1, (WIRING_3P4W, WIRING_3P3W)),
    ("thd_current_l1", "THD Corrente L1", None, "%", 1, (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("thd_current_l2", "THD Corrente L2", None, "%", 1, (WIRING_3P4W, WIRING_3P3W)),
    ("thd_current_l3", "THD Corrente L3", None, "%", 1, (WIRING_3P4W, WIRING_3P3W)),
]

MAX_MIN_DESCRIPTIONS: list[CvmSensorEntityDescription] = []
for key, name, dev_class, unit, prec, wirings in MAX_MIN_BASE_VARS:
    MAX_MIN_DESCRIPTIONS.append(
        CvmSensorEntityDescription(
            key=f"{key}_max",
            name=f"{name} (Max)",
            device_class=dev_class,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=unit,
            suggested_display_precision=prec,
            entity_category=EntityCategory.DIAGNOSTIC,
            wiring_supported=wirings,
        )
    )
    MAX_MIN_DESCRIPTIONS.append(
        CvmSensorEntityDescription(
            key=f"{key}_min",
            name=f"{name} (Min)",
            device_class=dev_class,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=unit,
            suggested_display_precision=prec,
            entity_category=EntityCategory.DIAGNOSTIC,
            wiring_supported=wirings,
        )
    )

# Dynamically generate Harmonic entity descriptions (Fundamental + 2nd to 31st harmonic)
HARMONIC_DESCRIPTIONS: list[CvmSensorEntityDescription] = []
for phase, p_name, w_sup in [
    ("l1", "L1", (WIRING_3P4W, WIRING_3P3W, WIRING_1P2W)),
    ("l2", "L2", (WIRING_3P4W, WIRING_3P3W)),
    ("l3", "L3", (WIRING_3P4W, WIRING_3P3W)),
]:
    HARMONIC_DESCRIPTIONS.append(
        CvmSensorEntityDescription(
            key=f"voltage_fundamental_{phase}",
            name=f"Tensione Fondamentale {p_name}",
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricPotential.VOLT,
            suggested_display_precision=1,
            entity_category=EntityCategory.DIAGNOSTIC,
            wiring_supported=w_sup,
        )
    )
    HARMONIC_DESCRIPTIONS.append(
        CvmSensorEntityDescription(
            key=f"current_fundamental_{phase}",
            name=f"Corrente Fondamentale {p_name}",
            device_class=SensorDeviceClass.CURRENT,
            state_class=SensorStateClass.MEASUREMENT,
            native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
            suggested_display_precision=2,
            entity_category=EntityCategory.DIAGNOSTIC,
            wiring_supported=w_sup,
        )
    )
    for h in range(2, 32):
        HARMONIC_DESCRIPTIONS.append(
            CvmSensorEntityDescription(
                key=f"harmonic_v_{phase}_h{h}",
                name=f"Armonica Tensione {p_name} H{h}",
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement="%",
                suggested_display_precision=1,
                entity_category=EntityCategory.DIAGNOSTIC,
                wiring_supported=w_sup,
            )
        )
        HARMONIC_DESCRIPTIONS.append(
            CvmSensorEntityDescription(
                key=f"harmonic_i_{phase}_h{h}",
                name=f"Armonica Corrente {p_name} H{h}",
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement="%",
                suggested_display_precision=1,
                entity_category=EntityCategory.DIAGNOSTIC,
                wiring_supported=w_sup,
            )
        )

ALL_SENSOR_DESCRIPTIONS: list[CvmSensorEntityDescription] = (
    list(SENSOR_DESCRIPTIONS) + MAX_MIN_DESCRIPTIONS + HARMONIC_DESCRIPTIONS
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


class CvmE3MiniSensor(CoordinatorEntity[CvmE3MiniCoordinator], SensorEntity):
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
        self._attr_has_entity_name = True
        self._attr_name = description.name
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
    def native_value(self) -> Any:
        """Return native value of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)
