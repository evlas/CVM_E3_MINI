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
    CONF_WIRING_SYSTEM,
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
    WIRING_3P4W,
    WIRING_3P3W,
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


def _decode_30_vars(b: list[int], suffix: str, data: dict[str, Any]) -> None:
    """Decode 30 variables block (60 registers) for Max or Min."""
    data[f"voltage_l1_{suffix}"] = _decode_u32(b[0], b[1]) / 10.0
    data[f"current_l1_{suffix}"] = _decode_u32(b[2], b[3]) / 1000.0
    data[f"power_active_l1_{suffix}"] = _decode_s32(b[4], b[5])
    data[f"power_reactive_ind_l1_{suffix}"] = _decode_s32(b[6], b[7])
    data[f"power_reactive_cap_l1_{suffix}"] = _decode_s32(b[8], b[9])
    data[f"power_apparent_l1_{suffix}"] = _decode_u32(b[10], b[11])
    data[f"power_factor_l1_{suffix}"] = _decode_s32(b[12], b[13]) / 100.0
    data[f"cos_phi_l1_{suffix}"] = _decode_s32(b[14], b[15]) / 100.0

    data[f"voltage_l2_{suffix}"] = _decode_u32(b[16], b[17]) / 10.0
    data[f"current_l2_{suffix}"] = _decode_u32(b[18], b[19]) / 1000.0
    data[f"power_active_l2_{suffix}"] = _decode_s32(b[20], b[21])
    data[f"power_reactive_ind_l2_{suffix}"] = _decode_s32(b[22], b[23])
    data[f"power_reactive_cap_l2_{suffix}"] = _decode_s32(b[24], b[25])
    data[f"power_apparent_l2_{suffix}"] = _decode_u32(b[26], b[27])
    data[f"power_factor_l2_{suffix}"] = _decode_s32(b[28], b[29]) / 100.0
    data[f"cos_phi_l2_{suffix}"] = _decode_s32(b[30], b[31]) / 100.0

    data[f"voltage_l3_{suffix}"] = _decode_u32(b[32], b[33]) / 10.0
    data[f"current_l3_{suffix}"] = _decode_u32(b[34], b[35]) / 1000.0
    data[f"power_active_l3_{suffix}"] = _decode_s32(b[36], b[37])
    data[f"power_reactive_ind_l3_{suffix}"] = _decode_s32(b[38], b[39])
    data[f"power_reactive_cap_l3_{suffix}"] = _decode_s32(b[40], b[41])
    data[f"power_apparent_l3_{suffix}"] = _decode_u32(b[42], b[43])
    data[f"power_factor_l3_{suffix}"] = _decode_s32(b[44], b[45]) / 100.0
    data[f"cos_phi_l3_{suffix}"] = _decode_s32(b[46], b[47]) / 100.0

    data[f"power_active_total_{suffix}"] = _decode_s32(b[48], b[49])
    data[f"power_reactive_ind_total_{suffix}"] = _decode_s32(b[50], b[51])
    data[f"power_reactive_cap_total_{suffix}"] = _decode_s32(b[52], b[53])
    data[f"power_apparent_total_{suffix}"] = _decode_u32(b[54], b[55])
    data[f"power_factor_total_{suffix}"] = _decode_s32(b[56], b[57]) / 100.0
    data[f"cos_phi_total_{suffix}"] = _decode_s32(b[58], b[59]) / 100.0


def _decode_11_vars(b: list[int], suffix: str, data: dict[str, Any]) -> None:
    """Decode 11 variables block (22 registers) for Max or Min."""
    data[f"frequency_{suffix}"] = _decode_u32(b[0], b[1]) / 100.0
    data[f"voltage_l1_l2_{suffix}"] = _decode_u32(b[2], b[3]) / 10.0
    data[f"voltage_l2_l3_{suffix}"] = _decode_u32(b[4], b[5]) / 10.0
    data[f"voltage_l3_l1_{suffix}"] = _decode_u32(b[6], b[7]) / 10.0
    data[f"current_neutral_{suffix}"] = _decode_u32(b[8], b[9]) / 1000.0
    data[f"thd_voltage_l1_{suffix}"] = _decode_u32(b[10], b[11]) / 10.0
    data[f"thd_voltage_l2_{suffix}"] = _decode_u32(b[12], b[13]) / 10.0
    data[f"thd_voltage_l3_{suffix}"] = _decode_u32(b[14], b[15]) / 10.0
    data[f"thd_current_l1_{suffix}"] = _decode_u32(b[16], b[17]) / 10.0
    data[f"thd_current_l2_{suffix}"] = _decode_u32(b[18], b[19]) / 10.0
    data[f"thd_current_l3_{suffix}"] = _decode_u32(b[20], b[21]) / 10.0


def _decode_harmonics_voltage(b: list[int], phase: str, data: dict[str, Any]) -> None:
    """Decode voltage harmonics (fundamental + 2nd..31st)."""
    data[f"voltage_fundamental_{phase}"] = _decode_u32(b[0], b[1]) / 10.0
    for h in range(2, 32):
        # Index in buffer is h (h=2 is at index 2, h=31 is at index 31)
        data[f"harmonic_v_{phase}_h{h}"] = b[h] / 10.0


def _decode_harmonics_current(b: list[int], phase: str, data: dict[str, Any]) -> None:
    """Decode current harmonics (fundamental + 2nd..31st)."""
    data[f"current_fundamental_{phase}"] = _decode_u32(b[0], b[1]) / 1000.0
    for h in range(2, 32):
        data[f"harmonic_i_{phase}_h{h}"] = b[h] / 10.0


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
            kwargs: dict[str, Any] = {
                "host": host,
                "port": port,
                "timeout": self.timeout,
            }
            if framer_type == FRAMER_RTU and ModbusRtuFramer is not None:
                kwargs["framer"] = ModbusRtuFramer
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

        # 2. PyModbus 3.0 - 3.8 (slave)
        try:
            return await client_method(*args, slave=self.slave_id, **kwargs)
        except TypeError:
            pass
        except Exception as ex:
            _LOGGER.debug("%s with slave error: %s", method_name, ex)

        # 3. Legacy PyModbus 2.x (unit)
        try:
            return await client_method(*args, unit=self.slave_id, **kwargs)
        except TypeError:
            pass
        except Exception as ex:
            _LOGGER.debug("%s with unit error: %s", method_name, ex)

        # 4. Fallback without target device identifier
        try:
            return await client_method(*args, **kwargs)
        except Exception as ex:
            _LOGGER.debug("%s fallback error: %s", method_name, ex)
            return None

    async def _exec_read_holding(self, address: int, count: int) -> Any:
        """Attempt reading holding registers (0x03)."""
        return await self._call_client_method("read_holding_registers", address, count=count)

    async def _exec_read_input(self, address: int, count: int) -> Any:
        """Attempt reading input registers (0x04)."""
        return await self._call_client_method("read_input_registers", address, count=count)

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
                # BLOCK 2b: Reactive Max Demands (0x1200 - 0x1203)
                # -------------------------------------------------------------
                try:
                    b2b = await self._read_registers(0x1200, 4)
                    await asyncio.sleep(0.05)
                    data["max_demand_reactive_ind_power"] = _decode_s32(b2b[0], b2b[1])
                    data["max_demand_reactive_cap_power"] = _decode_s32(b2b[2], b2b[3])
                except Exception as err:
                    _LOGGER.debug("Could not read reactive max demand registers: %s", err)

                # -------------------------------------------------------------
                # BLOCK 3: Total Energies (0x10DC - 0x1105)
                # 42 registers = 21 variables
                # -------------------------------------------------------------
                b3 = await self._read_registers(0x10DC, 42)
                await asyncio.sleep(0.1)

                data["energy_active_consumed_total"] = _decode_u32(b3[0], b3[1])  # kWh
                data["energy_active_consumed_wh_total"] = _decode_u32(b3[2], b3[3])  # Wh
                data["energy_reactive_ind_consumed_total"] = _decode_u32(b3[4], b3[5])  # kvarh
                data["energy_reactive_ind_consumed_varh_total"] = _decode_u32(b3[6], b3[7])  # varh
                data["energy_reactive_cap_consumed_total"] = _decode_u32(b3[8], b3[9])  # kvarh
                data["energy_reactive_cap_consumed_varh_total"] = _decode_u32(b3[10], b3[11])  # varh
                data["energy_apparent_consumed_total"] = _decode_u32(b3[12], b3[13])  # kVAh
                data["energy_apparent_consumed_vah_total"] = _decode_u32(b3[14], b3[15])  # VAh
                data["co2_consumed_total"] = _decode_u32(b3[16], b3[17]) / 10.0  # kg
                data["cost_consumed_total"] = _decode_u32(b3[18], b3[19]) / 10.0

                data["energy_active_generated_total"] = _decode_u32(b3[20], b3[21])  # kWh
                data["energy_active_generated_wh_total"] = _decode_u32(b3[22], b3[23])  # Wh
                data["energy_reactive_ind_generated_total"] = _decode_u32(b3[24], b3[25])  # kvarh
                data["energy_reactive_ind_generated_varh_total"] = _decode_u32(b3[26], b3[27])  # varh
                data["energy_reactive_cap_generated_total"] = _decode_u32(b3[28], b3[29])  # kvarh
                data["energy_reactive_cap_generated_varh_total"] = _decode_u32(b3[30], b3[31])  # varh
                data["energy_apparent_generated_total"] = _decode_u32(b3[32], b3[33])  # kVAh
                data["energy_apparent_generated_vah_total"] = _decode_u32(b3[34], b3[35])  # VAh
                data["co2_generated_total"] = _decode_u32(b3[36], b3[37]) / 10.0  # kg
                data["cost_generated_total"] = _decode_u32(b3[38], b3[39]) / 10.0
                data["operating_hours_total"] = _decode_u32(b3[40], b3[41]) / 3600.0  # converted to hours

                # -------------------------------------------------------------
                # BLOCK 4: Maxima (0x1106 - 0x1163, 0x1204 - 0x1207)
                # -------------------------------------------------------------
                try:
                    b_max1 = await self._read_registers(0x1106, 60)
                    _decode_30_vars(b_max1, "max", data)
                    await asyncio.sleep(0.05)

                    b_max2 = await self._read_registers(0x1142, 34)
                    _decode_11_vars(b_max2[:22], "max", data)
                    data["max_demand_active_power_max"] = _decode_s32(b_max2[22], b_max2[23])
                    data["max_demand_apparent_power_max"] = _decode_u32(b_max2[24], b_max2[25])
                    data["max_demand_current_l1_max"] = _decode_u32(b_max2[28], b_max2[29]) / 1000.0
                    data["max_demand_current_l2_max"] = _decode_u32(b_max2[30], b_max2[31]) / 1000.0
                    data["max_demand_current_l3_max"] = _decode_u32(b_max2[32], b_max2[33]) / 1000.0
                    await asyncio.sleep(0.05)

                    b_max3 = await self._read_registers(0x1204, 4)
                    data["max_demand_reactive_ind_power_max"] = _decode_s32(b_max3[0], b_max3[1])
                    data["max_demand_reactive_cap_power_max"] = _decode_s32(b_max3[2], b_max3[3])
                    await asyncio.sleep(0.05)
                except Exception as err:
                    _LOGGER.debug("Could not read maximum values: %s", err)

                # -------------------------------------------------------------
                # BLOCK 5: Minima (0x1164 - 0x11B5)
                # -------------------------------------------------------------
                try:
                    b_min1 = await self._read_registers(0x1164, 60)
                    _decode_30_vars(b_min1, "min", data)
                    await asyncio.sleep(0.05)

                    b_min2 = await self._read_registers(0x11A0, 22)
                    _decode_11_vars(b_min2, "min", data)
                    await asyncio.sleep(0.05)
                except Exception as err:
                    _LOGGER.debug("Could not read minimum values: %s", err)

                # -------------------------------------------------------------
                # BLOCK 6: Harmonics (0x1A28 - 0x1AE7)
                # -------------------------------------------------------------
                try:
                    wiring = self.entry_data.get(CONF_WIRING_SYSTEM, WIRING_3P4W)
                    # L1 Harmonics (32 registers each)
                    b_vh1 = await self._read_registers(0x1A28, 32)
                    _decode_harmonics_voltage(b_vh1, "l1", data)
                    await asyncio.sleep(0.05)

                    b_ih1 = await self._read_registers(0x1A88, 32)
                    _decode_harmonics_current(b_ih1, "l1", data)
                    await asyncio.sleep(0.05)

                    if wiring in (WIRING_3P4W, WIRING_3P3W):
                        # L2 Harmonics
                        b_vh2 = await self._read_registers(0x1A48, 32)
                        _decode_harmonics_voltage(b_vh2, "l2", data)
                        await asyncio.sleep(0.05)

                        b_ih2 = await self._read_registers(0x1AA8, 32)
                        _decode_harmonics_current(b_ih2, "l2", data)
                        await asyncio.sleep(0.05)

                        # L3 Harmonics
                        b_vh3 = await self._read_registers(0x1A68, 32)
                        _decode_harmonics_voltage(b_vh3, "l3", data)
                        await asyncio.sleep(0.05)

                        b_ih3 = await self._read_registers(0x1AC8, 32)
                        _decode_harmonics_current(b_ih3, "l3", data)
                        await asyncio.sleep(0.05)
                except Exception as err:
                    _LOGGER.debug("Could not read harmonic registers: %s", err)

                # -------------------------------------------------------------
                # Internal Temperature (M1 0x0050, 0x00B0, 0x0110)
                # -------------------------------------------------------------
                try:
                    temp_inst = await self._read_registers(0x0050, 2)
                    data["internal_temperature"] = _decode_s32(temp_inst[0], temp_inst[1]) / 10.0
                    temp_max = await self._read_registers(0x00B0, 2)
                    data["internal_temperature_max"] = _decode_s32(temp_max[0], temp_max[1]) / 10.0
                    temp_min = await self._read_registers(0x0110, 2)
                    data["internal_temperature_min"] = _decode_s32(temp_min[0], temp_min[1]) / 10.0
                    await asyncio.sleep(0.05)
                except Exception as err:
                    _LOGGER.debug("Could not read internal temperature registers: %s", err)

                # -------------------------------------------------------------
                # BLOCK 7: Status and Digital I/O
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
