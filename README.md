# Circutor CVM-E3-MINI - Home Assistant Integration

<p align="center">
  <img src="custom_components/cvm_e3_mini/brand/icon.png" alt="Circutor CVM-E3-MINI" width="130">
</p>

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/CVM_E3_MINI?color=blue&style=flat-square)](https://github.com/evlas/CVM_E3_MINI/releases)
[![Hassfest](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

🌐 *English | [Versione in italiano](README.it.md)*

Professional **Home Assistant** integration for the **Circutor CVM-E3-MINI** three-phase power analyzer (including WiEth / ITF / MC / FLEX models) via **Modbus** protocol (RTU over RS-485 or TCP over Ethernet/Wi-Fi/Gateway).

Designed according to the official **Circutor M170B01-01** instruction manual specifications.

---

## 🚀 Key Features

- **100% WebUI Configuration (Config Flow)**: Easy setup directly from *Settings -> Devices & Services -> Add Integration*.
- **Native Multi-Language Support (Home Assistant Entity Translations)**:
  - Adheres to modern Home Assistant standards with consistent, standardized entity IDs (e.g. `sensor.circutor_cvm_e3_mini_voltage_l1`).
  - Entity friendly names dynamically display in the user's interface language (English and Italian included out of the box).
- **Modbus TCP & Modbus RTU Support**:
  - **Modbus TCP**: Natively compatible with **CVM-E3-MINI-xxx-WiEth** models (Wi-Fi / Ethernet port 502) and serial-to-Ethernet gateways (e.g., Waveshare, USR-TCP232, Elfin EW11). Supports standard Modbus TCP or Modbus RTU over TCP.
  - **Modbus RTU**: Direct RS-485 serial connection (e.g. `/dev/ttyUSB0` or `/dev/serial/by-id/...`).
- **Respects Circutor Hardware Constraints**:
  - Implements block reading (maximum 30 variables / 60 registers per frame, as specified on page 87 of the manual).
  - Enforces $\ge 100\text{ ms}$ inter-frame delay and adaptive timeouts for stability with firmware $\ge \text{v}2.xx$.
- **Native Home Assistant Energy Dashboard Integration**:
  - Active energy consumed (import) and generated (export/PV) counters equipped with `device_class: energy` and `state_class: total_increasing`.
  - High-resolution energy counters with single Wh precision (3 decimal places for kWh, kvarh, kVAh) combining the kilo register and fractional Wh/varh/VAh remainder register.
- **Comprehensive Electrical Monitoring**:
  - Phase-to-Neutral voltages ($V_{L1}, V_{L2}, V_{L3}$) and Phase-to-Phase voltages ($V_{12}, V_{23}, V_{31}$).
  - Line currents ($I_{L1}, I_{L2}, I_{L3}$) and Neutral current ($I_N$).
  - Active, reactive (inductive/capacitive), and apparent powers (total and per-phase) with signed values supporting generation/export.
  - Power factor ($PF$) and $\cos \varphi$ (total and per-phase).
  - Grid frequency ($Hz$).
  - Total Harmonic Distortion (% THD for Voltage and Current on all phases).
  - Internal device temperature (°C).
  - Operating hours counter.
- **Full Harmonic Spectrum (2nd to 31st Harmonics)**:
  - Fundamental and 2nd to 31st harmonic breakdown for Voltage and Current on L1, L2, L3 (% relative to fundamental, disabled by default to save resources).
- **Binary Sensors & Diagnostics**:
  - **Phase sequence error detection** (`binary_sensor` with `problem` device class, register `0x07D5`).
  - 4-quadrant operational state (Import/Export, Inductive/Capacitive, register `0x07D1`).
  - Hardware Serial Number readout from register `0x05AA`.
- **Control & Reset directly from WebUI**:
  - **Buttons**:
    - 🔄 *Reset Three-Phase Energy Counters*
    - 🔄 *Reset All Energy Counters (Phases + Three-Phase)*
    - 🔄 *Reset All Parameters*
  - **Select Entities**:
    - 💡 *Display Backlight*: Always On / Timed
- **Dedicated Automation Services**: Native Home Assistant services for automated resets and configuration.

---

## 📦 Installation

### Method 1: Via HACS (Recommended)

1. Open **HACS** in Home Assistant.
2. Go to **Integrations** -> Click the three dots menu in the top right corner -> **Custom repositories**.
3. Paste this repository URL, select the category **Integration**, and click **Add**.
4. Search for **Circutor CVM-E3-MINI** and click **Download**.
5. Restart Home Assistant.

### Method 2: Manual Installation

1. Download the `custom_components/cvm_e3_mini` directory.
2. Copy it into the `custom_components/` folder of your Home Assistant installation:
   ```
   /config/custom_components/cvm_e3_mini/
   ```
3. Restart Home Assistant.

---

## ⚙️ Configuration

1. In the Home Assistant WebUI, navigate to **Settings** -> **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **Circutor CVM-E3-MINI**.
4. Select your connection type:
   - **Modbus TCP**:
     - *Host*: IP address of the analyzer or gateway (e.g., `192.168.1.150`).
     - *Port*: `502` (standard Modbus TCP).
     - *Slave ID*: Modbus device slave address (default `1`, range 1-255).
     - *TCP Protocol / Gateway Type*: Standard Modbus TCP (for WiEth models or gateways translating Modbus TCP) or Modbus RTU over TCP (for transparent RS485-TCP gateways like Waveshare/USR).
     - *System Wiring Type*: Three-phase 4-wire (3P+N), Three-phase 3-wire (3P), or Single-phase.
     - *Scan Interval*: default `10` seconds.
     - *Timeout*: default `3.0` seconds.
   - **Modbus RTU (RS-485)**:
     - *Serial Port*: e.g. `/dev/ttyUSB0` or `/dev/serial/by-id/...`
     - *Baudrate*: default `19200` (or `9600`, `38400`, `57600`, `115200`).
     - *Parity*: `None`, `Even`, `Odd` (default `None`).
     - *Stop Bits*: `1` (or `2`).
     - *Slave ID*: default `1`.

---

## 📊 Energy Dashboard Integration

To add the CVM-E3-MINI to Home Assistant's official **Energy Dashboard**:

1. Go to **Settings** -> **Dashboards** -> **Energy**.
2. Under **Electricity grid** -> **Grid consumption**, click *Add consumption* and select:
   - `sensor.circutor_cvm_e3_mini_total_active_energy_consumed`
3. If you have a solar photovoltaic system or generator exporting power to the grid:
   - Under **Return to grid**, click *Add return* and select:
   - `sensor.circutor_cvm_e3_mini_total_active_energy_generated`

---

## 🎛️ Lovelace Card Example

You can set up a dashboard card by copying [`lovelace_card_example.yaml`](lovelace_card_example.yaml) into the Lovelace card editor.

Compact example:

```yaml
type: vertical-stack
title: Circutor CVM-E3-MINI Analyzer
cards:
  - type: glance
    entities:
      - entity: sensor.circutor_cvm_e3_mini_voltage_l1
        name: Voltage L1
      - entity: sensor.circutor_cvm_e3_mini_current_l1
        name: Current L1
      - entity: sensor.circutor_cvm_e3_mini_total_active_power
        name: Active Power
      - entity: sensor.circutor_cvm_e3_mini_grid_frequency
        name: Frequency
  - type: entities
    title: Controls & Reset
    entities:
      - entity: select.circutor_cvm_e3_mini_display_backlight
      - entity: button.circutor_cvm_e3_mini_reset_three_phase_energy_counters
      - entity: button.circutor_cvm_e3_mini_reset_all_energy_counters
      - entity: button.circutor_cvm_e3_mini_reset_all_parameters
```

---

## 🛠️ Alternative Without Custom Component: Native YAML Package

If you prefer not to use custom components and configure Home Assistant's native `modbus:` component instead, ready-to-use packages are provided:
- 🇬🇧 **English package**: [`cvm_e3_mini_modbus_package.yaml`](cvm_e3_mini_modbus_package.yaml) (or [`cvm_e3_mini_modbus_package.en.yaml`](cvm_e3_mini_modbus_package.en.yaml))
- 🇮🇹 **Italian package**: [`cvm_e3_mini_modbus_package.it.yaml`](cvm_e3_mini_modbus_package.it.yaml)

Simply place the chosen file into your Home Assistant `config/packages/` directory.

---

## 📑 Modbus Register Map (Summary from Circutor Manual)

The integration uses the manufacturer's recommended **MAPA 2**:

| Parameter | Hex Register | Dec Register | Data Type | Units / Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Voltage L1** | `0x1000` | 4096 | Uint32 | V $\times 10$ |
| **Current L1** | `0x1002` | 4098 | Uint32 | mA |
| **Active Power L1** | `0x1004` | 4100 | Int32 | W (negative = generation) |
| **Apparent Power L1** | `0x100A` | 4106 | Int32 | VA (negative = generation) |
| **Voltage L2** | `0x1010` | 4112 | Uint32 | V $\times 10$ |
| **Current L2** | `0x1012` | 4114 | Uint32 | mA |
| **Active Power L2** | `0x1014` | 4116 | Int32 | W |
| **Apparent Power L2** | `0x101A` | 4122 | Int32 | VA |
| **Voltage L3** | `0x1020` | 4128 | Uint32 | V $\times 10$ |
| **Current L3** | `0x1022` | 4130 | Uint32 | mA |
| **Active Power L3** | `0x1024` | 4132 | Int32 | W |
| **Apparent Power L3** | `0x102A` | 4138 | Int32 | VA |
| **Total Active Power** | `0x1030` | 4144 | Int32 | W (negative = generation) |
| **Total Apparent Power** | `0x1036` | 4150 | Int32 | VA (negative = generation) |
| **Frequency** | `0x103C` | 4156 | Uint32 | Hz $\times 100$ |
| **Active Energy Consumed (kWh)** | `0x10DC` | 4316 | Uint32 | kWh integer |
| **Active Energy Consumed (Wh)** | `0x10DE` | 4318 | Uint32 | Wh remainder (0..999) |
| **Active Energy Generated (kWh)** | `0x10F0` | 4336 | Uint32 | kWh integer |
| **Active Energy Generated (Wh)** | `0x10F2` | 4338 | Uint32 | Wh remainder (0..999) |
| **Reset Three-Phase Energy (Coil)**| `0x0834` | 2100 | Coil (Fn 0x05) | Write 0xFF00 |
| **Reset All Energy (Coil)**| `0x0874` | 2164 | Coil (Fn 0x05) | Write 0xFF00 |
| **Reset All Parameters (Coil)**| `0x0898` | 2200 | Coil (Fn 0x05) | Write 0xFF00 |

---

## 📄 License

Distributed under the GNU General Public License v3.0 (GPLv3). See [LICENSE](LICENSE) for details.
