# MM-116 Modbus Proxy — instrukce pro Claude

## Problém
MM-116 má Modbus TCP server, který podporuje **pouze jedno spojení**. Je potřeba více klientů.

## Řešení
HASS addon fungující jako Modbus TCP proxy/multiplexer — čte registry z MM-116 a poskytuje je více klientům přes vlastní Modbus TCP server.

## GitHub repozitář
`git@github.com:flajzi/mm116-modbus-proxy.git`

## Dokumentace
- [Architektura](docs/architektura.md) — jak proxy funguje, diagram, komponenty
- [Registrová mapa](docs/registrova-mapa.md) — všechny Modbus registry MM-116 dle PDF
- [Konfigurace](docs/konfigurace.md) — parametry addonu, síť, testování
- [Průběh vývoje](docs/vyvoj.md) — klíčové poznatky, verze, struktura repozitáře

## Důležité technické detaily
- MM-116 používá **Modbus RTU over TCP** (port 10001) — nutný `Framer.RTU`
- Addon instaluje **pymodbus 3.6.x** — API se liší od 3.12
- Konfiguraci čte z `/data/options.json` přes `jq` (bez bashio, `init: false`)
- Registry se čtou po blocích: fast (0x00–0x5F, 1s) a config (0x80–0xAF, 10s)

## Pravidla
- S každým `git push` zvednout patch verzi v `mm116-modbus-proxy/config.yaml`
- Adresa zařízení: `192.168.2.15:10001`, slave ID: 1
