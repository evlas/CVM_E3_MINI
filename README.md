# Circutor CVM-E3-MINI - Integrazione Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/evlas/CVM_E3_MINI?color=blue&style=flat-square)](https://github.com/evlas/CVM_E3_MINI/releases)
[![Hassfest](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hassfest.yml/badge.svg)](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hassfest.yml)
[![HACS Action](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hacs.yml/badge.svg)](https://github.com/evlas/CVM_E3_MINI/actions/workflows/hacs.yml)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.8%2B-blue.svg)](https://www.home-assistant.io/)

Integrazione professionale per **Home Assistant** per l'analizzatore di rete trifase **Circutor CVM-E3-MINI** (e versioni WiEth / ITF / MC / FLEX) tramite protocollo **Modbus** (RTU su RS-485 o TCP su Ethernet/Wi-Fi/Gateway).

Basata sulle specifiche ufficiali del manuale d'istruzioni **Circutor M170B01-01**.

---

## 🚀 Caratteristiche Principali

- **Configurazione 100% da WebUI (Config Flow)**: Aggiunta guidata da *Impostazioni -> Dispositivi e Servizi -> Aggiungi Integrazione*.
- **Supporto Modbus TCP e Modbus RTU**:
  - **Modbus TCP**: Compatibile sia nativamente con i modelli **CVM-E3-MINI-xxx-WiEth** (Wi-Fi / Ethernet porta 502) sia tramite gateway seriale/Ethernet (es. Waveshare, USR-TCP232, Elfin EW11).
  - **Modbus RTU**: Connessione diretta seriale RS-485 (porta `/dev/ttyUSB0`, convertitore USB-RS485).
- **Rispettoso dei vincoli hardware Circutor**:
  - Implementa la lettura a blocchi (massimo 30 variabili / 60 registri per trama, come specificato a pag. 87 del manuale).
  - Cadenza inter-frame $\ge 100\text{ ms}$ e timeout per garantire stabilità con firmware $\ge \text{v}2.xx$.
- **Integrazione nativa con la Dashboard Energia di Home Assistant**:
  - Contatori di energia attiva consumata (prelievo) e generata (immissione/fotovoltaico) con `device_class: energy` e `state_class: total_increasing`.
  - Risoluzione standard (kWh, kvarh, kVAh) e ad alta risoluzione (Wh, varh, VAh) sia per energia consumata che generata.
- **Monitoraggio Completo (Istantanei, Massimi e Minimi)**:
  - Tensioni di fase ($V_{L1}, V_{L2}, V_{L3}$) e concatenate ($V_{12}, V_{23}, V_{31}$) con relativi valori Minimi e Massimi.
  - Correnti di linea ($I_{L1}, I_{L2}, I_{L3}$) e corrente di Neutro ($I_N$) con Minimi e Massimi.
  - Potenze attive, reattive (induttiva e capacitiva) e apparenti (totali e per singola fase) con Minimi e Massimi.
  - Fattore di potenza ($PF$) e $\cos \varphi$ con Minimi e Massimi.
  - Frequenza di rete ($Hz$) con Minimo e Massimo.
  - Distorsione armonica totale (% THD Tensione e Corrente per ogni fase) con Minimi e Massimi.
  - Picchi di massima richiesta (Max Demand kW, kVA, kvarL, kvarC, Correnti L1/L2/L3) con relativi picchi storici massimi.
  - Temperatura interna dello strumento (°C) con Minimo e Massimo.
  - Ore di funzionamento, emissioni di $\text{CO}_2$ e costi/valori economici stimati.
- **Spettro Armonico Completo (Armoniche 2°..31°)**:
  - Tensione Fondamentale e armoniche dalla 2ª alla 31ª per L1, L2, L3 (% rispetto alla fondamentale).
  - Corrente Fondamentale e armoniche dalla 2ª alla 31ª per L1, L2, L3 (% rispetto alla fondamentale).
- **Sensori Binari di Stato e Diagnostica**:
  - Stato dell'ingresso digitale (Input logico) e contatore impulsi (Uint64).
  - Stato dell'uscita digitale (Relè / Allarme).
  - **Rilevamento errore sequenza fasi** (`binary_sensor` con classe `problem`, registro `0x07D5`).
  - Quadrante operativo di lavoro a 4 quadranti (Consumo/Generazione, Induttivo/Capacitivo, registro `0x07D1`).
  - Lettura matricola / numero di serie hardware univoco da registro `0x05AA`.
- **Controllo e Reset direttamente dalla WebUI**:
  - **Pulsanti (Button entities)**:
    - 🔄 *Azzera Valori Massimi*
    - 🔄 *Azzera Valori Minimi*
    - 🔄 *Azzera Massima Richiesta (Max Demand)*
    - 🔄 *Azzera Contatori Energia Trifase*
    - 🔄 *Azzera Tutti i Contatori Energia (Fasi + Trifase)*
    - 🔄 *Azzera Contatore Impulsi*
    - 🔄 *Azzera Ore Tariffa 1 / Tariffa 2*
    - 🔄 *Azzera Tutti i Parametri*
  - **Selettori (Select entities)**:
    - ⚙️ *Selezione Tariffa*: Tariffa 1 / Tariffa 2
    - 💡 *Retroilluminazione Display*: Sempre Acceso / Temporizzato
- **Servizi dedicati per Automazioni**: Tutti i comandi di azzeramento e controllo sono invocabili via servizio Home Assistant.

---

## 📦 Installazione

### Metodo 1: Tramite HACS (Consigliato)

1. Apri **HACS** in Home Assistant.
2. Vai su **Integrazioni** -> Menu tre puntini in alto a destra -> **Repository personalizzati**.
3. Incolla l'URL di questo repository, seleziona la categoria **Integrazione** e clicca **Aggiungi**.
4. Cerca **Circutor CVM-E3-MINI** e clicca su **Scarica**.
5. Riavvia Home Assistant.

### Metodo 2: Installazione Manuale

1. Scarica la cartella `custom_components/cvm_e3_mini`.
2. Copiala nella directory `custom_components/` della tua installazione di Home Assistant:
   ```
   /config/custom_components/cvm_e3_mini/
   ```
3. Riavvia Home Assistant.

---

## ⚙️ Configurazione

1. Nella WebUI di Home Assistant, vai su **Impostazioni** -> **Dispositivi e Servizi**.
2. Clicca su **Aggiungi Integrazione** in basso a destra.
3. Cerca **Circutor CVM-E3-MINI**.
4. Scegli la tipologia di connessione:
   - **Modbus TCP**:
     - *Host*: Indirizzo IP dell'analizzatore (es. `192.168.1.150`).
     - *Porta*: `502` (standard Modbus TCP).
     - *Slave ID*: Numero periferico Modbus numerico (default `1`, campo numerico 1-255).
     - *Tipo di protocollo TCP / Gateway*: Modbus TCP standard (per modelli WiEth o gateway che traducono Modbus TCP) oppure Modbus RTU over TCP (per gateway seriali trasparenti RS485-TCP come Waveshare/USR).
     - *Tipo di impianto*: Trifase 4 fili (3P+N), Trifase 3 fili (3P), o Monofase.
     - *Intervallo di scansione*: default `10` secondi.
     - *Timeout di risposta*: default `3.0` secondi.
   - **Modbus RTU (RS-485)**:
     - *Porta seriale*: es. `/dev/ttyUSB0` o `/dev/serial/by-id/...`
     - *Baudrate*: default `19200` (o `9600`, `38400`, `57600`, `115200`).
     - *Parità*: `Nessuna (None)`, `Pari (Even)`, `Dispari (Odd)` (default `None`).
     - *Bit di stop*: `1` (o `2`).
     - *Slave ID*: default `1`.

---

## 📊 Dashboard Energia (Energy Dashboard)

Per aggiungere il CVM-E3-MINI alla **Dashboard Energia** ufficiale di Home Assistant:

1. Vai su **Impostazioni** -> **Dashboard** -> **Energia**.
2. Sotto **Rete elettrica** -> **Consumo dalla rete**, clicca *Aggiungi consumo* e seleziona:
   - `sensor.circutor_cvm_e3_mini_energia_attiva_consumata_totale`
3. Se hai un impianto fotovoltaico o generatore con immissione in rete:
   - Sotto **Immissione in rete**, clicca *Aggiungi immissione* e seleziona:
   - `sensor.circutor_cvm_e3_mini_energia_attiva_generata_totale`

---

## 🎛️ Esempio Scheda Lovelace (WebUI)

Puoi importare la dashboard completa copiando il file [`lovelace_card_example.yaml`](lovelace_card_example.yaml) direttamente nell'editor delle schede di Lovelace.

Ecco un esempio compatto:

```yaml
type: vertical-stack
title: Analizzatore Circutor CVM-E3-MINI
cards:
  - type: glance
    entities:
      - entity: sensor.circutor_cvm_e3_mini_tensione_l1
        name: Tensione L1
      - entity: sensor.circutor_cvm_e3_mini_corrente_l1
        name: Corrente L1
      - entity: sensor.circutor_cvm_e3_mini_potenza_attiva_totale
        name: Potenza Attiva
      - entity: sensor.circutor_cvm_e3_mini_frequenza_di_rete
        name: Frequenza
  - type: entities
    title: Comandi e Reset
    entities:
      - entity: select.circutor_cvm_e3_mini_selezione_tariffa
      - entity: select.circutor_cvm_e3_mini_retroilluminazione_display
      - entity: button.circutor_cvm_e3_mini_azzera_valori_massimi
      - entity: button.circutor_cvm_e3_mini_azzera_massima_richiesta
      - entity: button.circutor_cvm_e3_mini_azzera_contatori_energia_trifase
```

---

## 🛠️ Alternativa Senza Custom Component: Pacchetto YAML Nativo

Se preferisci non usare Custom Component e configurare direttamente il componente nativo `modbus:` di Home Assistant, è fornito il file pronto all'uso:
👉 [`cvm_e3_mini_modbus_package.yaml`](cvm_e3_mini_modbus_package.yaml)

Basta posizionarlo nella cartella `config/packages/` del proprio Home Assistant.

---

## 📑 Mappa Registri Modbus (Sintesi dal Manuale Circutor)

L'integrazione utilizza il **MAPA 2** raccomandato dal produttore:

| Parametro | Registro Hex | Registro Dec | Tipo Dati | Unità |
| :--- | :--- | :--- | :--- | :--- |
| **Tensione L1** | `0x1000` | 4096 | Uint32 | V $\times 10$ |
| **Corrente L1** | `0x1002` | 4098 | Uint32 | mA |
| **Potenza Attiva L1** | `0x1004` | 4100 | Int32 | W (segno negativo = gen) |
| **Tensione L2** | `0x1010` | 4112 | Uint32 | V $\times 10$ |
| **Corrente L2** | `0x1012` | 4114 | Uint32 | mA |
| **Potenza Attiva L2** | `0x1014` | 4116 | Int32 | W |
| **Tensione L3** | `0x1020` | 4128 | Uint32 | V $\times 10$ |
| **Corrente L3** | `0x1022` | 4130 | Uint32 | mA |
| **Potenza Attiva L3** | `0x1024` | 4132 | Int32 | W |
| **Potenza Attiva Totale** | `0x1030` | 4144 | Int32 | W |
| **Frequenza** | `0x103C` | 4156 | Uint32 | Hz $\times 100$ |
| **Energia Attiva Consumata Totale** | `0x10DC` | 4316 | Uint32 | kWh |
| **Energia Attiva Generata Totale** | `0x10F0` | 4336 | Uint32 | kWh |
| **Reset Massimi (Coil)** | `0x0849` | 2121 | Coil (Fn 0x05) | Scrittura 0xFF00 |
| **Reset Minimi (Coil)** | `0x084A` | 2122 | Coil (Fn 0x05) | Scrittura 0xFF00 |
| **Reset Max Demand (Coil)** | `0x0852` | 2130 | Coil (Fn 0x05) | Scrittura 0xFF00 |
| **Reset Energie Trifase (Coil)**| `0x0834` | 2100 | Coil (Fn 0x05) | Scrittura 0xFF00 |
| **Reset Tutte le Energie (Coil)**| `0x0874` | 2164 | Coil (Fn 0x05) | Scrittura 0xFF00 |
| **Reset Impulsi (Coil)** | `0x0884` | 2180 | Coil (Fn 0x05) | Scrittura 0xFF00 |

---

## 📄 Licenza

Distribuito sotto licenza GNU General Public License v3.0 (GPLv3). Consulta il file [LICENSE](LICENSE) per maggiori informazioni.
