# MM-116 Modbus Proxy

Home Assistant addon pro zařízení MM-116, které podporuje pouze jedno Modbus TCP spojení. Addon funguje jako proxy/multiplexer — připojí se k zařízení jako jediný klient a poskytuje data libovolnému počtu dalších klientů přes vlastní Modbus TCP server.

## Funkce

- Periodické čtení všech holding registrů z MM-116 (bloky 0x00–0x5F a 0x80–0xAF)
- Modbus TCP server pro více simultánních klientů
- Write-through — zápisy do R/W registrů se přeposílají na reálné zařízení
- Automatické znovupřipojení při výpadku spojení
- Podpora Modbus RTU over TCP (serial-to-Ethernet konvertory)

## Registrová mapa

| Blok | Adresy | Popis | Přístup |
|------|--------|-------|---------|
| Identifikace | 0x00–0x0F | ADR, TYPE, HW/FW verze, SN, ID, CONFIG | R |
| Čas, status, paměť | 0x10–0x1F | RTC, TICK, STATUS, INPUTS, OUTPUTS | R/W |
| Statistika komunikace | 0x20–0x2F | Chyby, CRC, počty paketů | R |
| Vstupní buffer | 0x30–0x3F | BUF1–BUF16 (impulzy v T15) | R |
| Interval mezi impulzy | 0x40–0x5F | PER1–PER16 (float32) | R |
| Převodní konstanty | 0x80–0x9F | PPU1–PPU16 (float32) | R/W |
| Parametry regulace | 0xA0–0xAF | REGMAX, KR, VZP, KZK, MZ-PR, ... | R/W |

Kompletní dokumentace registrů viz `MM116-MODBUS-REG.pdf`.

## Instalace

1. V Home Assistant přejděte do **Settings → Add-ons → Add-on Store**
2. Klikněte na **⋮** (tři tečky) → **Repositories**
3. Přidejte URL: `https://github.com/flajzi/mm116-modbus-proxy`
4. Nainstalujte addon **MM-116 Modbus Proxy**

## Konfigurace

| Parametr | Výchozí | Popis |
|----------|---------|-------|
| `mm116_host` | `192.168.2.15` | IP adresa zařízení MM-116 |
| `mm116_port` | `10001` | TCP port zařízení |
| `mm116_slave_id` | `1` | Modbus slave ID |
| `server_port` | `5020` | Port proxy serveru |
| `poll_fast_interval` | `2` | Interval čtení bloků 0–4 (sekundy) |
| `poll_config_interval` | `30` | Interval čtení bloků 5–6 (sekundy) |
| `log_level` | `INFO` | Úroveň logování (DEBUG/INFO/WARNING/ERROR) |

## Připojení klientů

Po spuštění addonu se klienti připojují na IP adresu Home Assistant a port `server_port` (výchozí 5020) pomocí standardního Modbus TCP protokolu. Adresy registrů odpovídají původní registrové mapě MM-116.

## Lokální testování

```bash
pip install pymodbus
python3 mm116-modbus-proxy/modbus_proxy.py \
  --mm116-host 192.168.2.15 \
  --mm116-port 10001 \
  --server-port 5020
```
