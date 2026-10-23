"""Circutor CVM-E3-MINI Home Assistant integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.loader import async_get_integration

from .const import (
    COIL_RESET_ALL_PARAMETERS,
    COIL_RESET_ENERGY_ALL,
    COIL_RESET_ENERGY_THREEPHASE,
    COIL_RESET_MAX_DEMAND,
    COIL_RESET_MAXIMUMS,
    COIL_RESET_MINIMUMS,
    COIL_RESET_PULSE_COUNTER,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    REG_BACKLIGHT,
    REG_TARIFF_SELECT,
    SERVICE_RESET_ALL,
    SERVICE_RESET_ENERGY_COUNTERS,
    SERVICE_RESET_MAX_DEMAND,
    SERVICE_RESET_MAXIMUMS,
    SERVICE_RESET_MINIMUMS,
    SERVICE_RESET_PULSE_COUNTER,
    SERVICE_SET_BACKLIGHT,
    SERVICE_SET_TARIFF,
)
from .coordinator import CvmE3MiniCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Circutor CVM-E3-MINI from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    integration_version: str | None = None
    try:
        integration = await async_get_integration(hass, DOMAIN)
        integration_version = integration.version
    except Exception:
        pass

    coordinator = CvmE3MiniCoordinator(
        hass=hass,
        entry_data=entry.data,
        scan_interval=scan_interval,
        version=integration_version,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.error("Failed to connect or initialize CVM-E3-MINI: %s", ex)
        await coordinator.async_close()
        raise ConfigEntryNotReady(f"Failed to communicate with CVM-E3-MINI: {ex}") from ex

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services once
    if len(hass.data[DOMAIN]) == 1:
        _register_services(hass)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: CvmE3MiniCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


def _register_services(hass: HomeAssistant) -> None:
    """Register custom services for Circutor CVM-E3-MINI."""

    async def _handle_reset_maximums(call: ServiceCall) -> None:
        """Handle resetting maximum values."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_coil(COIL_RESET_MAXIMUMS, True)

    async def _handle_reset_minimums(call: ServiceCall) -> None:
        """Handle resetting minimum values."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_coil(COIL_RESET_MINIMUMS, True)

    async def _handle_reset_max_demand(call: ServiceCall) -> None:
        """Handle resetting max demand."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_coil(COIL_RESET_MAX_DEMAND, True)

    async def _handle_reset_energy(call: ServiceCall) -> None:
        """Handle resetting energy counters."""
        include_phase = call.data.get("include_phase_energies", True)
        coil = COIL_RESET_ENERGY_ALL if include_phase else COIL_RESET_ENERGY_THREEPHASE
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_coil(coil, True)

    async def _handle_reset_pulse(call: ServiceCall) -> None:
        """Handle resetting pulse counter."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_coil(COIL_RESET_PULSE_COUNTER, True)

    async def _handle_reset_all(call: ServiceCall) -> None:
        """Handle resetting all parameters."""
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_coil(COIL_RESET_ALL_PARAMETERS, True)

    async def _handle_set_tariff(call: ServiceCall) -> None:
        """Handle setting active tariff."""
        tariff = str(call.data.get("tariff", "1"))
        val = 0 if tariff == "1" else 1
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_register(REG_TARIFF_SELECT, val)

    async def _handle_set_backlight(call: ServiceCall) -> None:
        """Handle setting backlight mode."""
        mode = call.data.get("mode", "always_on")
        val = 0 if mode == "always_on" else 1
        for coordinator in hass.data[DOMAIN].values():
            await coordinator.write_register(REG_BACKLIGHT, val)

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_MAXIMUMS,
        _handle_reset_maximums,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_MINIMUMS,
        _handle_reset_minimums,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_MAX_DEMAND,
        _handle_reset_max_demand,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_ENERGY_COUNTERS,
        _handle_reset_energy,
        schema=vol.Schema({vol.Optional("include_phase_energies", default=True): cv.boolean}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_PULSE_COUNTER,
        _handle_reset_pulse,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_ALL,
        _handle_reset_all,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TARIFF,
        _handle_set_tariff,
        schema=vol.Schema({vol.Required("tariff"): vol.In([1, 2])}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BACKLIGHT,
        _handle_set_backlight,
        schema=vol.Schema({vol.Required("mode"): vol.In(["always_on", "timed"])}),
    )
