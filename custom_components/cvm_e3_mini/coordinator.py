"""DataUpdateCoordinator for Circutor CVM-E3-MINI."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import struct
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

try:
    from pymodbus.transaction import ModbusRtuFramer, ModbusSocketFramer
except ImportError:
    try:
        from pymodbus.framer.rtu_framer import ModbusRtuFramer
        from pymodbus.framer.socket_framer import ModbusSocketFramer
    except ImportError:
        ModbusRtuFramer = None
        ModbusSocketFramer = None

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_CONNECTION_TYPE,
    CONF_FRAMER,
    CONF_HOST,
    CONF_PARITY,
    CONF_PORT,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_STOPBITS,
    CONF_TIMEOUT,
    CONN_TYPE_TCP,
    DEFAULT_FRAMER,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DOMAIN,
    FRAMER_RTU,
    FRAMER_SOCKET,
    REG_DIGITAL_INPUT_STATE,
    REG_DIGITAL_OUTPUT_STATE,
    REG_PHASE_ROTATION_ERROR,
    REG_POWER_STATUS,
    REG_PULSE_COUNTER_START,
    REG_SERIAL_NUMBER_START,
)

_LOGGER = logging.getLogger(__name__)


def _decode_s32(r0: int, r1: int) -> int:
    """Decode two 16-bit registers as signed 32-bit big-endian integer."""
    return struct.unpack(">i", struct.pack(">HH", r0, r1))[0]


def _decode_u32(r0: int, r1: int) -> int:
    """Decode two 16-bit registers as unsigned 32-bit big-endian integer."""
    return struct.unpack(">I", struct.pack(">HH", r0, r1))[0]


def _decode_u64(r0: int, r1: int, r2: int, r3: int) -> int:
    """Decode four 16-bit registers as unsigned 64-bit big-endian integer."""
    return struct.unpack(">Q", struct.pack(">HHHH", r0, r1, r2, r3))[0]


class CvmE3MiniCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching CVM-E3-MINI data from Modbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_data: dict[str, Any],
        scan_interval: int,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.entry_data = entry_data
        self.slave_id = int(entry_data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))
        self.conn_type = entry_data.get(CONF_CONNECTION_TYPE, CONN_TYPE_TCP)
        self.timeout = float(entry_data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))

        self._client: AsyncModbusTcpClient | AsyncModbusSerialClient | None = None
        self._lock = asyncio.Lock()
        self.serial_number: str | None = None
        self.model: str = "CVM-E3-MINI"

    def _create_client(self) -> AsyncModbusTcpClient | AsyncModbusSerialClient:
        """Create Modbus client instance based on connection type."""
        if self.conn_type == CONN_TYPE_TCP:
            host = self.entry_data[CONF_HOST]
            port = int(self.entry_data.get(CONF_PORT, DEFAULT_PORT))
            framer_type = self.entry_data.get(CONF_FRAMER, DEFAULT_FRAMER)
            framer_cls = (
                ModbusRtuFramer
                if (framer_type == FRAMER_RTU and ModbusRtuFramer is not None)
                else ModbusSocketFramer
            )
            kwargs: dict[str, Any] = {
                "host": host,
                "port": port,
                "timeout": self.timeout,
            }
            if framer_cls is not None:
                kwargs["framer"] = framer_cls
            return AsyncModbusTcpClient(**kwargs)

        # Serial / RTU
        port = self.entry_data[CONF_SERIAL_PORT]
        baudrate = int(self.entry_data.get(CONF_BAUDRATE, 19200))
        parity_str = self.entry_data.get(CONF_PARITY, "none").lower()
        parity = "N"
        if parity_str in ("even", "e"):
            parity = "E"
        elif parity_str in ("odd", "o"):
            parity = "O"

        stopbits = int(self.entry_data.get(CONF_STOPBITS, 1))
        bytesize = int(self.entry_data.get(CONF_BYTESIZE, 8))

        return AsyncModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=self.timeout,
        )

    async def _ensure_connected(self) -> None:
        """Ensure client is connected."""
        if self._client is None:
            self._client = self._create_client()

        if not getattr(self._client, "connected", False):
            try:
                connected = await self._client.connect()
            except Exception as err:
                _LOGGER.warning("Connection failed to %s: %s", self.conn_type, err)
                try:
                    self._client.close()
                except Exception:
                    pass
                self._client = None
                raise UpdateFailed(f"Unable to connect to Modbus device ({self.conn_type}): {err}") from err

            if not connected and not getattr(self._client, "connected", False):
                try:
                    self._client.close()
                except Exception:
                    pass
                self._client = None
                raise UpdateFailed(f"Unable to connect to Modbus device ({self.conn_type})")

    async def _call_client_method(self, method_name: str, *args, **kwargs) -> Any:
        """Call client method trying device_id (PyModbus >=3.8.3/3.10+), slave, and unit gracefully."""
        client_method = getattr(self._client, method_name, None)
        if client_method is None:
            _LOGGER.error("Modbus client missing method: %s", method_name)
            return None

        # 1. Modern PyModbus >= 3.8.3 / 3.10+ (device_id)
        try:
            return await client_method(*args, device_id=self.slave_id, **kwargs)
        except TypeError:
            pass
        except Exception as ex:
            _LOGGER.debug("%s with device_id error: %s", method_name, ex)
            return None

        # 2. PyModbus 3.0 - 3.8 (slave)
        try:
            return await client_method(*args, slave=self.slave_id, **kwargs)
        except TypeError:
            pass
        except Exception as ex:
            _LOGGER.debug("%s with slave error: %s", method_name, ex)
            return None

        # 3. Legacy PyModbus 2.x (unit)
        try:
            return await client_method(*args, unit=self.slave_id, **kwargs)
        except TypeError:
            pass
        except Exception as ex:
            _LOGGER.debug("%s with unit error: %s", method_name, ex)
            return None

        # 4. Fallback without target device identifier
        try:
            return await client_method(*args, **kwargs)
        except Exception as ex:
            _LOGGER.debug("%s fallback error: %s", method_name, ex)
            return None

    async def _exec_read_holding(self, address: int, count: int) -> Any:
        """Attempt reading holding registers (0x03)."""
        return await self._call_client_method("read_holding_registers", address, count)

    async def _exec_read_input(self, address: int, count: int) -> Any:
        """Attempt reading input registers (0x04)."""
        return await self._call_client_method("read_input_registers", address, count)

    async def _read_registers(
        self,
        address: int,
        count: int,
        prefer_input: bool = False,
    ) -> list[int]:
        """Read holding or input registers with backward/forward pymodbus compatibility."""
        await self._ensure_connected()
        assert self._client is not None

        result = None
        if prefer_input:
            result = await self._exec_read_input(address, count)
            if result is None or result.isError():
                result = await self._exec_read_holding(address, count)
        else:
            result = await self._exec_read_holding(address, count)
            if result is None or result.isError():
                result = await self._exec_read_input(address, count)

        if result is None or result.isError():
            raise ModbusException(f"Error reading {count} registers from address {hex(address)}: {result}")

        return list(result.registers)

    async def write_coil(self, address: int, value: bool = True) -> bool:
        """Write single coil (Function 0x05, 0xFF00 for True)."""
        async with self._lock:
            await self._ensure_connected()
            assert self._client is not None
            try:
                result = await self._call_client_method("write_coil", address, value)
                if result is None or result.isError():
                    _LOGGER.error("Failed writing coil %s: %s", hex(address), result)
                    return False
                _LOGGER.info("Successfully executed command on coil %s", hex(address))
                return True
            except Exception as ex:
                _LOGGER.exception("Exception writing coil %s: %s", hex(address), ex)
                return False

    async def write_register(self, address: int, value: int) -> bool:
        """Write single holding register (Function 0x06 / 0x10)."""
        async with self._lock:
            await self._ensure_connected()
            assert self._client is not None
            try:
                result = await self._call_client_method("write_register", address, value)
                if result is None or result.isError():
                    _LOGGER.error("Failed writing register %s: %s", hex(address), result)
                    return False
                _LOGGER.info("Successfully wrote register %s = %s", hex(address), value)
                return True
            except Exception as ex:
                _LOGGER.exception("Exception writing register %s: %s", hex(address), ex)
                return False

    async def fetch_device_info(self) -> None:
        """Fetch static device information (serial number)."""
        try:
            # Serial number register 0x05AA uses Function 0x04 per Circutor manual p.98
            regs = await self._read_registers(REG_SERIAL_NUMBER_START, 7, prefer_input=True)
            raw_bytes = bytearray()
            for r in regs:
                raw_bytes.extend(struct.pack(">H", r))

            # Check if it's ASCII or numeric hex
            ascii_str = raw_bytes.decode("ascii", errors="ignore").strip().strip("\x00")
            if ascii_str and all(c.isalnum() or c in "-_" for c in ascii_str):
                self.serial_number = ascii_str
            else:
                self.serial_number = "".join(f"{b:02X}" for b in raw_bytes if b != 0)

            _LOGGER.info("CVM-E3-MINI detected with Serial Number: %s", self.serial_number)
        except Exception as err:
            _LOGGER.warning("Could not read serial number from device: %s", err)
            self.serial_number = f"cvm_e3_mini_{self.slave_id}"

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all data from the meter in compliant batches."""
        async with self._lock:
            if not self.serial_number:
                await self.fetch_device_info()

            data: dict[str, Any] = {}

            try:
                # -------------------------------------------------------------
                # BLOCK 1: Instantaneous phase measurements (0x1000 - 0x1033)
                # 52 registers = 26 variables (<= 30 variables per frame)
                # -------------------------------------------------------------
                b1 = await self._read_registers(0x1000, 52)
                await asyncio.sleep(0.1)  # Inter-frame delay for hardware stability

                # Phase 1
                data["voltage_l1"] = _decode_u32(b1[0], b1[1]) / 10.0
                data["current_l1"] = _decode_u32(b1[2], b1[3]) / 1000.0
                data["power_active_l1"] = _decode_s32(b1[4], b1[5])
                data["power_reactive_ind_l1"] = _decode_s32(b1[6], b1[7])
                data["power_reactive_cap_l1"] = _decode_s32(b1[8], b1[9])
                data["power_apparent_l1"] = _decode_u32(b1[10], b1[11])
                data["power_factor_l1"] = _decode_s32(b1[12], b1[13]) / 100.0
                data["cos_phi_l1"] = _decode_s32(b1[14], b1[15]) / 100.0

                # Phase 2
                data["voltage_l2"] = _decode_u32(b1[16], b1[17]) / 10.0
                data["current_l2"] = _decode_u32(b1[18], b1[19]) / 1000.0
                data["power_active_l2"] = _decode_s32(b1[20], b1[21])
                data["power_reactive_ind_l2"] = _decode_s32(b1[22], b1[23])
                data["power_reactive_cap_l2"] = _decode_s32(b1[24], b1[25])
                data["power_apparent_l2"] = _decode_u32(b1[26], b1[27])
                data["power_factor_l2"] = _decode_s32(b1[28], b1[29]) / 100.0
                data["cos_phi_l2"] = _decode_s32(b1[30], b1[31]) / 100.0

                # Phase 3
                data["voltage_l3"] = _decode_u32(b1[32], b1[33]) / 10.0
                data["current_l3"] = _decode_u32(b1[34], b1[35]) / 1000.0
                data["power_active_l3"] = _decode_s32(b1[36], b1[37])
                data["power_reactive_ind_l3"] = _decode_s32(b1[38], b1[39])
                data["power_reactive_cap_l3"] = _decode_s32(b1[40], b1[41])
                data["power_apparent_l3"] = _decode_u32(b1[42], b1[43])
                data["power_factor_l3"] = _decode_s32(b1[44], b1[45]) / 100.0
                data["cos_phi_l3"] = _decode_s32(b1[46], b1[47]) / 100.0

                # Three-phase partial
                data["power_active_total"] = _decode_s32(b1[48], b1[49])
                data["power_reactive_ind_total"] = _decode_s32(b1[50], b1[51])

                # -------------------------------------------------------------
                # BLOCK 2: Totals, frequency, line voltages, THD & Max Demand (0x1034 - 0x105D)
                # 42 registers = 21 variables
                # -------------------------------------------------------------
                b2 = await self._read_registers(0x1034, 42)
                await asyncio.sleep(0.1)

                data["power_reactive_cap_total"] = _decode_s32(b2[0], b2[1])
                data["power_apparent_total"] = _decode_u32(b2[2], b2[3])
                data["power_factor_total"] = _decode_s32(b2[4], b2[5]) / 100.0
                data["cos_phi_total"] = _decode_s32(b2[6], b2[7]) / 100.0
                data["frequency"] = _decode_u32(b2[8], b2[9]) / 100.0
                data["voltage_l1_l2"] = _decode_u32(b2[10], b2[11]) / 10.0
                data["voltage_l2_l3"] = _decode_u32(b2[12], b2[13]) / 10.0
                data["voltage_l3_l1"] = _decode_u32(b2[14], b2[15]) / 10.0
                data["current_neutral"] = _decode_u32(b2[16], b2[17]) / 1000.0
                data["thd_voltage_l1"] = _decode_u32(b2[18], b2[19]) / 10.0
                data["thd_voltage_l2"] = _decode_u32(b2[20], b2[21]) / 10.0
                data["thd_voltage_l3"] = _decode_u32(b2[22], b2[23]) / 10.0
                data["thd_current_l1"] = _decode_u32(b2[24], b2[25]) / 10.0
                data["thd_current_l2"] = _decode_u32(b2[26], b2[27]) / 10.0
                data["thd_current_l3"] = _decode_u32(b2[28], b2[29]) / 10.0

                # Max demands
                data["max_demand_active_power"] = _decode_s32(b2[30], b2[31])
                data["max_demand_apparent_power"] = _decode_u32(b2[32], b2[33])
                data["max_demand_current_l1"] = _decode_u32(b2[36], b2[37]) / 1000.0
                data["max_demand_current_l2"] = _decode_u32(b2[38], b2[39]) / 1000.0
                data["max_demand_current_l3"] = _decode_u32(b2[40], b2[41]) / 1000.0

                # -------------------------------------------------------------
                # BLOCK 3: Total Energies (0x10DC - 0x1105)
                # 42 registers = 21 variables
                # -------------------------------------------------------------
                b3 = await self._read_registers(0x10DC, 42)
                await asyncio.sleep(0.1)

                data["energy_active_consumed_total"] = _decode_u32(b3[0], b3[1])  # kWh
                data["energy_active_consumed_wh_total"] = _decode_u32(b3[2], b3[3])  # Wh
                data["energy_reactive_ind_consumed_total"] = _decode_u32(b3[4], b3[5])  # kvarh
                data["energy_reactive_cap_consumed_total"] = _decode_u32(b3[8], b3[9])  # kvarh
                data["energy_apparent_consumed_total"] = _decode_u32(b3[12], b3[13])  # kVAh
                data["co2_consumed_total"] = _decode_u32(b3[16], b3[17]) / 10.0  # kg
                data["cost_consumed_total"] = _decode_u32(b3[18], b3[19]) / 10.0

                data["energy_active_generated_total"] = _decode_u32(b3[20], b3[21])  # kWh
                data["energy_active_generated_wh_total"] = _decode_u32(b3[22], b3[23])  # Wh
                data["energy_reactive_ind_generated_total"] = _decode_u32(b3[24], b3[25])  # kvarh
                data["energy_reactive_cap_generated_total"] = _decode_u32(b3[28], b3[29])  # kvarh
                data["energy_apparent_generated_total"] = _decode_u32(b3[32], b3[33])  # kVAh
                data["co2_generated_total"] = _decode_u32(b3[36], b3[37]) / 10.0  # kg
                data["cost_generated_total"] = _decode_u32(b3[38], b3[39]) / 10.0
                data["operating_hours_total"] = _decode_u32(b3[40], b3[41]) / 3600.0  # converted to hours

                # -------------------------------------------------------------
                # BLOCK 4: Status and Digital I/O
                # -------------------------------------------------------------
                try:
                    status_regs = await self._read_registers(REG_POWER_STATUS, 5)
                    await asyncio.sleep(0.05)
                    # 0x07D1: Power quadrant
                    quad_raw = status_regs[0]
                    data["quadrant_consumed"] = bool(quad_raw & 0x01)
                    data["quadrant_generated"] = bool(quad_raw & 0x02)
                    data["quadrant_inductive"] = bool(quad_raw & 0x04)
                    data["quadrant_capacitive"] = bool(quad_raw & 0x08)

                    # 0x07D5 is offset +4
                    data["phase_rotation_error"] = bool(status_regs[4] == 1)
                except Exception as err:
                    _LOGGER.debug("Could not read power status registers: %s", err)

                try:
                    io_regs = await self._read_registers(REG_DIGITAL_INPUT_STATE, 7)
                    # 0x4E20: Digital Input
                    data["digital_input"] = bool(io_regs[0] & 0x01)
                    # 0x4E21: Digital Output
                    data["digital_output"] = bool(io_regs[1] & 0x01)
                    # 0x4E23 - 0x4E26: Pulse counter (Uint64)
                    data["pulse_counter"] = _decode_u64(io_regs[3], io_regs[4], io_regs[5], io_regs[6])
                except Exception as err:
                    _LOGGER.debug("Could not read digital I/O registers: %s", err)

                return data

            except ModbusException as ex:
                raise UpdateFailed(f"Modbus communication error: {ex}") from ex
            except Exception as ex:
                raise UpdateFailed(f"Unexpected error updating CVM-E3-MINI: {ex}") from ex

    async def async_close(self) -> None:
        """Close connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
