"""Constants for the Circutor CVM-E3-MINI integration."""

DOMAIN = "cvm_e3_mini"

# Connection types
CONN_TYPE_TCP = "tcp"
CONN_TYPE_RTU = "rtu"

CONF_CONNECTION_TYPE = "connection_type"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SLAVE_ID = "slave_id"
CONF_SERIAL_PORT = "serial_port"
CONF_BAUDRATE = "baudrate"
CONF_PARITY = "parity"
CONF_STOPBITS = "stopbits"
CONF_BYTESIZE = "bytesize"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_TIMEOUT = "timeout"
CONF_WIRING_SYSTEM = "wiring_system"
CONF_FRAMER = "framer"
CONF_ENABLE_HARMONICS = "enable_harmonics"

# Defaults
DEFAULT_NAME = "Circutor CVM-E3-MINI"
DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 1
DEFAULT_BAUDRATE = 19200
DEFAULT_PARITY = "none"
DEFAULT_STOPBITS = 1
DEFAULT_BYTESIZE = 8
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_TIMEOUT = 3.0
DEFAULT_ENABLE_HARMONICS = False
FRAMER_SOCKET = "socket"
FRAMER_RTU = "rtu"
DEFAULT_FRAMER = FRAMER_SOCKET

# Wiring systems
WIRING_3P4W = "3p4w"  # Trifase 4 fili (3 fasi + neutro)
WIRING_3P3W = "3p3w"  # Trifase 3 fili (senza neutro)
WIRING_1P2W = "1p2w"  # Monofase

# Modbus Function Codes
FUNCTION_READ_HOLDING = 0x03
FUNCTION_READ_INPUT = 0x04
FUNCTION_WRITE_COIL = 0x05
FUNCTION_WRITE_REGISTERS = 0x10

# Coil Addresses for Commands (Function 0x05, value 0xFF00)
COIL_RESET_MAXIMUMS = 0x0849
COIL_RESET_MINIMUMS = 0x084A
COIL_RESET_MAX_DEMAND = 0x0852
COIL_RESET_ENERGY_THREEPHASE = 0x0834
COIL_RESET_ENERGY_ALL = 0x0874
COIL_RESET_PULSE_COUNTER = 0x0884
COIL_RESET_ALL_PARAMETERS = 0x0898
COIL_RESET_HOURS_T1 = 0x0837
COIL_RESET_HOURS_T2 = 0x083A

# Configuration Registers (Holding Registers)
REG_BACKLIGHT = 0x271B  # 0: always on, 1: timed
REG_TARIFF_SELECT = 0x2B66  # 0: tariff 1, 1: tariff 2

# Status and System Registers
REG_POWER_STATUS = 0x07D1  # 1 register (Bit 0: Consumed, Bit 1: Generated, Bit 2: Inductive, Bit 3: Capacitive)
REG_PHASE_ROTATION_ERROR = 0x07D5  # 1 register (0: OK, 1: Error)
REG_SERIAL_NUMBER_START = 0x05AA  # 7 registers (0x5AA - 0x5B0)
REG_DIGITAL_INPUT_STATE = 0x4E20  # 1 register (Bit 0: 0=OFF, 1=ON)
REG_DIGITAL_OUTPUT_STATE = 0x4E21  # 1 register (Bit 0: 0=OFF, 1=ON)
REG_PULSE_COUNTER_START = 0x4E23  # 4 registers (Uint64)

# Service Names
SERVICE_RESET_MAXIMUMS = "reset_maximums"
SERVICE_RESET_MINIMUMS = "reset_minimums"
SERVICE_RESET_MAX_DEMAND = "reset_max_demand"
SERVICE_RESET_ENERGY_COUNTERS = "reset_energy_counters"
SERVICE_RESET_PULSE_COUNTER = "reset_pulse_counter"
SERVICE_RESET_ALL = "reset_all"
SERVICE_SET_TARIFF = "set_tariff"
SERVICE_SET_BACKLIGHT = "set_backlight"
