"""Config flow for Circutor CVM-E3-MINI integration."""

from __future__ import annotations

import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient

try:
    from pymodbus.transaction import ModbusRtuFramer, ModbusSocketFramer
except ImportError:
    try:
        from pymodbus.framer.rtu_framer import ModbusRtuFramer
        from pymodbus.framer.socket_framer import ModbusSocketFramer
    except ImportError:
        ModbusRtuFramer = None
        ModbusSocketFramer = None

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .const import (
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_CONNECTION_TYPE,
    CONF_ENABLE_HARMONICS,
    CONF_FRAMER,
    CONF_HOST,
    CONF_PARITY,
    CONF_PORT,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_STOPBITS,
    CONF_TIMEOUT,
    CONF_WIRING_SYSTEM,
    CONF_SCAN_INTERVAL,
    CONN_TYPE_RTU,
    CONN_TYPE_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_BYTESIZE,
    DEFAULT_ENABLE_HARMONICS,
    DEFAULT_FRAMER,
    DEFAULT_NAME,
    DEFAULT_PARITY,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DEFAULT_STOPBITS,
    DEFAULT_TIMEOUT,
    DOMAIN,
    FRAMER_RTU,
    FRAMER_SOCKET,
    WIRING_1P2W,
    WIRING_3P3W,
    WIRING_3P4W,
)

_LOGGER = logging.getLogger(__name__)


async def _read_reg_universal(
    client: Any,
    is_input: bool,
    reg: int,
    count: int,
    slave_id: int,
) -> Any:
    """Read registers trying device_id (PyModbus >=3.8.3/3.10+), slave, and unit safely."""
    method = client.read_input_registers if is_input else client.read_holding_registers

    # 1. Modern PyModbus >= 3.8.3 / 3.10+ uses device_id
    try:
        return await method(reg, count=count, device_id=slave_id)
    except TypeError:
        try:
            return await method(reg, count, device_id=slave_id)
        except TypeError:
            pass
    except Exception as ex:
        _LOGGER.debug("read with device_id error at %s: %s", hex(reg), ex)

    # 2. PyModbus 3.0 - 3.8 uses slave
    try:
        return await method(reg, count=count, slave=slave_id)
    except TypeError:
        try:
            return await method(reg, count, slave=slave_id)
        except TypeError:
            pass
    except Exception as ex:
        _LOGGER.debug("read with slave error at %s: %s", hex(reg), ex)

    # 3. Legacy PyModbus 2.x uses unit
    try:
        return await method(reg, count=count, unit=slave_id)
    except TypeError:
        try:
            return await method(reg, count, unit=slave_id)
        except TypeError:
            pass
    except Exception as ex:
        _LOGGER.debug("read with unit error at %s: %s", hex(reg), ex)

    # 4. Fallback without target id
    try:
        return await method(reg, count=count)
    except TypeError:
        try:
            return await method(reg, count)
        except Exception as ex:
            _LOGGER.debug("read fallback error at %s: %s", hex(reg), ex)
    except Exception as ex:
        _LOGGER.debug("read fallback error at %s: %s", hex(reg), ex)

    return None


async def _test_tcp_connection(
    host: str,
    port: int,
    slave_id: int,
    timeout: float,
    framer_type: str = FRAMER_SOCKET,
) -> tuple[bool, str]:
    """Test connection to Modbus TCP device. Returns (success, detected_framer)."""
    framers_to_try = [framer_type]
    alt_framer = FRAMER_RTU if framer_type == FRAMER_SOCKET else FRAMER_SOCKET
    framers_to_try.append(alt_framer)

    for current_framer in framers_to_try:
        kwargs: dict[str, Any] = {
            "host": host,
            "port": port,
            "timeout": timeout,
        }
        if current_framer == FRAMER_RTU and ModbusRtuFramer is not None:
            kwargs["framer"] = ModbusRtuFramer

        client = AsyncModbusTcpClient(**kwargs)
        try:
            try:
                connected = await client.connect()
            except Exception as conn_err:
                _LOGGER.warning(
                    "TCP connection to %s:%s (framer: %s) failed: %s",
                    host,
                    port,
                    current_framer,
                    conn_err,
                )
                continue

            if not connected and not getattr(client, "connected", False):
                _LOGGER.warning(
                    "TCP socket to %s:%s could not be opened (framer: %s)",
                    host,
                    port,
                    current_framer,
                )
                continue

            # Try reading registers at 0x1000 (Mapa 2 V1), 0x0000 (Mapa 1 V1), or 0x05AA (Serial)
            success = False
            for reg in (0x1000, 0x0000, 0x05AA):
                # Try holding registers (0x03)
                res = await _read_reg_universal(client, False, reg, 2, slave_id)
                if res is not None and not res.isError():
                    success = True
                    break

                # Try input registers (0x04)
                res = await _read_reg_universal(client, True, reg, 2, slave_id)
                if res is not None and not res.isError():
                    success = True
                    break

            if success:
                _LOGGER.info(
                    "Connection to CVM-E3-MINI at %s:%s successfully verified (framer: %s, slave: %s)",
                    host,
                    port,
                    current_framer,
                    slave_id,
                )
                return True, current_framer

            _LOGGER.warning(
                "Connected to %s:%s, but meter did not answer on slave ID %s (framer: %s)",
                host,
                port,
                slave_id,
                current_framer,
            )

        except Exception as err:
            _LOGGER.warning("Modbus TCP test with framer %s failed: %s", current_framer, err)
        finally:
            try:
                client.close()
            except Exception:
                pass

    return False, framer_type


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
        if not connected and not getattr(client, "connected", False):
            return False

        for reg in (0x1000, 0x0000):
            res = await _read_reg_universal(client, False, reg, 2, slave_id)
            if res is not None and not res.isError():
                return True

            res = await _read_reg_universal(client, True, reg, 2, slave_id)
            if res is not None and not res.isError():
                return True

        return False
    except Exception as err:
        _LOGGER.warning("Modbus RTU connection test failed: %s", err)
        return False
    finally:
        try:
            client.close()
        except Exception:
            pass


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
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            slave_id = int(user_input[CONF_SLAVE_ID])
            timeout = float(user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))
            framer_type = user_input.get(CONF_FRAMER, DEFAULT_FRAMER)

            # Check unique ID based on host:port:slave
            unique_id = f"cvm_e3_mini_{host}_{port}_{slave_id}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            ignore_test = bool(user_input.get("ignore_test", False))

            # Connection test
            success, detected_framer = await _test_tcp_connection(
                host, port, slave_id, timeout, framer_type
            )
            if not success and not ignore_test:
                _LOGGER.warning(
                    "Could not reach CVM-E3-MINI at %s:%s (slave ID: %s, framer: %s). Check IP, port, Slave ID, or check 'ignore_test' to proceed anyway.",
                    host,
                    port,
                    slave_id,
                    framer_type,
                )
                errors["base"] = "cannot_connect"
            else:
                final_framer = detected_framer if success else framer_type
                clean_input = {k: v for k, v in user_input.items() if k != "ignore_test"}
                data = {
                    CONF_CONNECTION_TYPE: CONN_TYPE_TCP,
                    **clean_input,
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_SLAVE_ID: slave_id,
                    CONF_TIMEOUT: timeout,
                    CONF_FRAMER: final_framer,
                }
                title = f"{DEFAULT_NAME} ({host}:{port})"
                return self.async_create_entry(title=title, data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=255,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_FRAMER, default=DEFAULT_FRAMER): vol.In(
                    {
                        FRAMER_SOCKET: "Modbus TCP (Standard / WiEth / Gateway Modbus TCP)",
                        FRAMER_RTU: "Modbus RTU over TCP (Gateway seriale trasparente)",
                    }
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
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): NumberSelector(
                    NumberSelectorConfig(
                        min=2,
                        max=300,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): NumberSelector(
                    NumberSelectorConfig(
                        min=0.5,
                        max=30.0,
                        step=0.5,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_ENABLE_HARMONICS, default=DEFAULT_ENABLE_HARMONICS): bool,
                vol.Optional("ignore_test", default=False): bool,
            }
        )

        return self.async_show_form(step_id="tcp", data_schema=schema, errors=errors)

    async def async_step_rtu(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle Modbus RTU / Serial setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            serial_port = str(user_input[CONF_SERIAL_PORT]).strip()
            baudrate = int(user_input[CONF_BAUDRATE])
            parity = user_input[CONF_PARITY]
            stopbits = int(user_input[CONF_STOPBITS])
            slave_id = int(user_input[CONF_SLAVE_ID])
            timeout = float(user_input.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))
            ignore_test = bool(user_input.get("ignore_test", False))

            unique_id = f"cvm_e3_mini_{serial_port}_{slave_id}"
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            success = await _test_rtu_connection(
                serial_port, baudrate, parity, stopbits, slave_id, timeout
            )
            if not success and not ignore_test:
                _LOGGER.warning(
                    "Could not reach CVM-E3-MINI on %s (slave ID: %s). Check connection or check 'ignore_test' to proceed anyway.",
                    serial_port,
                    slave_id,
                )
                errors["base"] = "cannot_connect"
            else:
                clean_input = {k: v for k, v in user_input.items() if k != "ignore_test"}
                data = {
                    CONF_CONNECTION_TYPE: CONN_TYPE_RTU,
                    **clean_input,
                    CONF_SERIAL_PORT: serial_port,
                    CONF_BAUDRATE: baudrate,
                    CONF_STOPBITS: stopbits,
                    CONF_SLAVE_ID: slave_id,
                    CONF_TIMEOUT: timeout,
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
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=255,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
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
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): NumberSelector(
                    NumberSelectorConfig(
                        min=2,
                        max=300,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): NumberSelector(
                    NumberSelectorConfig(
                        min=0.5,
                        max=30.0,
                        step=0.5,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_ENABLE_HARMONICS, default=DEFAULT_ENABLE_HARMONICS): bool,
                vol.Optional("ignore_test", default=False): bool,
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

    def __init__(self, config_entry: config_entries.ConfigEntry | None = None) -> None:
        """Initialize options flow."""
        self._config_entry_compat = config_entry

    @property
    def config_entry(self) -> config_entries.ConfigEntry:
        """Return the config entry, compatible across HA versions."""
        try:
            entry = super().config_entry
            if entry is not None:
                return entry
        except Exception:
            pass
        return self._config_entry_compat  # type: ignore[return-value]

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        current_wiring = self.config_entry.options.get(
            CONF_WIRING_SYSTEM,
            self.config_entry.data.get(CONF_WIRING_SYSTEM, WIRING_3P4W),
        )
        current_timeout = self.config_entry.options.get(
            CONF_TIMEOUT,
            self.config_entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
        )
        current_harmonics = self.config_entry.options.get(
            CONF_ENABLE_HARMONICS,
            self.config_entry.data.get(CONF_ENABLE_HARMONICS, DEFAULT_ENABLE_HARMONICS),
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): NumberSelector(
                    NumberSelectorConfig(
                        min=2,
                        max=300,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_WIRING_SYSTEM, default=current_wiring): vol.In(
                    {
                        WIRING_3P4W: "Trifase 4 fili (3P + N)",
                        WIRING_3P3W: "Trifase 3 fili (3P)",
                        WIRING_1P2W: "Monofase (1P + N)",
                    }
                ),
                vol.Optional(CONF_TIMEOUT, default=current_timeout): NumberSelector(
                    NumberSelectorConfig(
                        min=0.5,
                        max=30.0,
                        step=0.5,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                vol.Optional(CONF_ENABLE_HARMONICS, default=current_harmonics): bool,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
