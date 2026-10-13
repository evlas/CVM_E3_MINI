"""Config flow for Circutor CVM-E3-MINI integration."""

from __future__ import annotations

import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_CONNECTION_TYPE,
    CONF_HOST,
    CONF_PARITY,
    CONF_PORT,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_STOPBITS,
    CONF_TIMEOUT,
    CONF_WIRING_SYSTEM,
    CONN_TYPE_RTU,
    CONN_TYPE_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_NAME,
    DEFAULT_PARITY,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEFAULT_STOPBITS,
    DEFAULT_TIMEOUT,
    DOMAIN,
    REG_SERIAL_NUMBER_START,
    WIRING_1P2W,
    WIRING_3P3W,
    WIRING_3P4W,
)

_LOGGER = logging.getLogger(__name__)


async def _test_tcp_connection(host: str, port: int, slave_id: int, timeout: float) -> bool:
    """Test connection to Modbus TCP device."""
    client = AsyncModbusTcpClient(host=host, port=port, timeout=timeout)
    try:
        connected = await client.connect()
        if not connected:
            return False
        # Try reading 2 registers
        try:
            res = await client.read_holding_registers(0x1000, 2, slave=slave_id)
        except TypeError:
            res = await client.read_holding_registers(0x1000, 2, unit=slave_id)
        if res.isError():
            # Try function 0x04
            try:
                res = await client.read_input_registers(0x1000, 2, slave=slave_id)
            except TypeError:
                res = await client.read_input_registers(0x1000, 2, unit=slave_id)
        return not res.isError()
    except Exception as err:
        _LOGGER.warning("Modbus TCP connection test failed: %s", err)
        return False
    finally:
        client.close()


async def _test_rtu_connection(
    port: str, baudrate: int, parity_str: str, stopbits: int, slave_id: int, timeout: float
) -> bool:
    """Test connection to Modbus RTU device."""
    parity = "N"
    if parity_str.lower() in ("even", "e"):
        parity = "E"
    elif parity_str.lower() in ("odd", "o"):
        parity = "O"

    client = AsyncModbusSerialClient(
        port=port,
        baudrate=baudrate,
        parity=parity,
        stopbits=stopbits,
        bytesize=8,
        timeout=timeout,
    )
    try:
        connected = await client.connect()
        if not connected:
            return False
        try:
            res = await client.read_holding_registers(0x1000, 2, slave=slave_id)
        except TypeError:
            res = await client.read_holding_registers(0x1000, 2, unit=slave_id)
        if res.isError():
            try:
                res = await client.read_input_registers(0x1000, 2, slave=slave_id)
            except TypeError:
                res = await client.read_input_registers(0x1000, 2, unit=slave_id)
        return not res.isError()
    except Exception as err:
        _LOGGER.warning("Modbus RTU connection test failed: %s", err)
        return False
    finally:
        client.close()


class CvmE3MiniConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Circutor CVM-E3-MINI."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._conn_type: str = CONN_TYPE_TCP

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 1: Choose connection type (Modbus TCP vs RTU/Serial)."""
        if user_input is not None:
            self._conn_type = user_input[CONF_CONNECTION_TYPE]
            if self._conn_type == CONN_TYPE_TCP:
                return await self.async_step_tcp()
            return await self.async_step_rtu()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_CONNECTION_TYPE, default=CONN_TYPE_TCP
                    ): vol.In(
                        {
                            CONN_TYPE_TCP: "Modbus TCP (Ethernet / Wi-Fi / Gateway)",
                            CONN_TYPE_RTU: "Modbus RTU (RS-485 Seriale / USB)",
                        }
                    ),
                }
            ),
        )

    async def async_step_tcp(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle Modbus TCP setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]
            slave_id = user_input[CONF_SLAVE_ID]
            timeout = user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)

            # Check unique ID based on host:port:slave
            unique_id = f"cvm_e3_mini_{host}_{port}_{slave_id}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            # Optional connection test
            success = await _test_tcp_connection(host, port, slave_id, timeout)
            if not success:
                _LOGGER.warning("Could not reach meter during config flow, proceeding anyway if user wants")
                # We can either warn or allow, let's allow or flag cannot_connect if strictly needed
                # It's friendly to let users save even if meter is temporarily unpowered

            data = {
                CONF_CONNECTION_TYPE: CONN_TYPE_TCP,
                **user_input,
            }
            title = f"{DEFAULT_NAME} ({host}:{port})"
            return self.async_create_entry(title=title, data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=255)
                ),
                vol.Optional(
                    CONF_WIRING_SYSTEM, default=WIRING_3P4W
                ): vol.In(
                    {
                        WIRING_3P4W: "Trifase 4 fili (3P + N)",
                        WIRING_3P3W: "Trifase 3 fili (3P)",
                        WIRING_1P2W: "Monofase (1P + N)",
                    }
                ),
                vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=2, max=300)
                ),
            }
        )

        return self.async_show_form(step_id="tcp", data_schema=schema, errors=errors)

    async def async_step_rtu(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle Modbus RTU / Serial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            serial_port = user_input[CONF_SERIAL_PORT]
            slave_id = user_input[CONF_SLAVE_ID]

            unique_id = f"cvm_e3_mini_{serial_port}_{slave_id}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            data = {
                CONF_CONNECTION_TYPE: CONN_TYPE_RTU,
                **user_input,
            }
            title = f"{DEFAULT_NAME} (RS485 ID {slave_id})"
            return self.async_create_entry(title=title, data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_SERIAL_PORT, default="/dev/ttyUSB0"): str,
                vol.Required(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In(
                    [9600, 19200, 38400, 57600, 115200]
                ),
                vol.Required(CONF_PARITY, default=DEFAULT_PARITY): vol.In(
                    {"none": "Nessuna (None)", "even": "Pari (Even)", "odd": "Dispari (Odd)"}
                ),
                vol.Required(CONF_STOPBITS, default=DEFAULT_STOPBITS): vol.In([1, 2]),
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=255)
                ),
                vol.Optional(
                    CONF_WIRING_SYSTEM, default=WIRING_3P4W
                ): vol.In(
                    {
                        WIRING_3P4W: "Trifase 4 fili (3P + N)",
                        WIRING_3P3W: "Trifase 3 fili (3P)",
                        WIRING_1P2W: "Monofase (1P + N)",
                    }
                ),
                vol.Optional("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=2, max=300)
                ),
            }
        )

        return self.async_show_form(step_id="rtu", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get options flow."""
        return CvmE3MiniOptionsFlowHandler(config_entry)


class CvmE3MiniOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Circutor CVM-E3-MINI."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            "scan_interval",
            self.config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL),
        )
        current_wiring = self.config_entry.options.get(
            CONF_WIRING_SYSTEM,
            self.config_entry.data.get(CONF_WIRING_SYSTEM, WIRING_3P4W),
        )

        schema = vol.Schema(
            {
                vol.Optional("scan_interval", default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=2, max=300)
                ),
                vol.Optional(CONF_WIRING_SYSTEM, default=current_wiring): vol.In(
                    {
                        WIRING_3P4W: "Trifase 4 fili (3P + N)",
                        WIRING_3P3W: "Trifase 3 fili (3P)",
                        WIRING_1P2W: "Monofase (1P + N)",
                    }
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
