# Průběh vývoje

## Klíčové poznatky ze session

### 1. Modbus RTU over TCP
MM-116 je připojen přes serial-to-Ethernet konvertor — nepoužívá standardní Modbus TCP (MBAP hlavičku), ale **Modbus RTU over TCP** (raw TCP). pymodbus musí být nastaven s `Framer.RTU`.

### 2. pymodbus API rozdíly mezi verzemi
Dockerfile instaluje pymodbus `3.6.x`. Lokálně byl zpočátku nainstalovaný `3.12.x`, kde se API liší:

| Věc | pymodbus 3.6 | pymodbus 3.12 |
|-----|-------------|---------------|
| Slave context | `ModbusSlaveContext` | `ModbusDeviceContext` |
| Parametr klienta | `slave=` | `device_id=` |
| Server context | `slaves=` | `devices=` |
| Framer | `Framer.RTU` | `FramerType.RTU` |
| Zero mode | `zero_mode=True` | offset +1 ručně |

### 3. s6-overlay
HASS base image používá s6-overlay jako správce procesů. Chyba `can only run as pid 1` se vyřešila nastavením `init: false` v `config.yaml` — addon pak běží bez s6 a spouští se přímo přes `CMD ["/run.sh"]`.

Zároveň byl `run.sh` přepsán z bashio na čisté sh + `jq` (čtení `/data/options.json`).

### 4. Kontinuální čtení bloků
Bloky 0–4 (0x00–0x5F) jsou kontiguózní → čtou se jedním requestem (96 registrů). Bloky 5–6 (0x80–0xAF) taktéž (48 registrů). Mezera 0x60–0x7F na zařízení neexistuje.

## Historie verzí

| Verze | Změna |
|-------|-------|
| 1.0.0 | Počáteční commit |
| 1.0.1 | Bump verze pro test update v HASS |
| 1.0.2 | Oprava s6-overlay (`init: false`, jq, CMD) |
| 1.0.3 | Oprava pymodbus API pro verzi 3.6 |
| 1.0.4 | Zkrácení intervalů: fast 1s, config 10s |

## Struktura repozitáře

```
mm-116/
  CLAUDE.md                        # Instrukce pro Claude
  README.md                        # Dokumentace pro uživatele
  repository.yaml                  # HASS addon repository manifest
  MM116-MODBUS-REG.pdf             # Registrová mapa zařízení
  MM-116.pdf                       # Kompletní dokumentace zařízení
  docs/
    architektura.md                # Popis architektury proxy
    registrova-mapa.md             # Přehled Modbus registrů
    konfigurace.md                 # Konfigurační parametry
    vyvoj.md                       # Tento soubor
  mm116-modbus-proxy/
    config.yaml                    # HASS addon manifest
    Dockerfile                     # Alpine + pymodbus 3.6
    run.sh                         # Spouštěcí skript (sh + jq)
    modbus_proxy.py                # Hlavní aplikace (~300 řádků)
```
