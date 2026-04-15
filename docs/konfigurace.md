# Konfigurace addonu

## Parametry (config.yaml)

| Parametr | Výchozí | Popis |
|----------|---------|-------|
| `mm116_host` | `192.168.2.15` | IP adresa zařízení MM-116 |
| `mm116_port` | `10001` | TCP port (serial-to-Ethernet konvertor) |
| `mm116_slave_id` | `1` | Modbus slave ID |
| `server_port` | `5020` | Port proxy serveru (pro klienty) |
| `poll_fast_interval` | `1` | Interval čtení bloků 0–4 v sekundách |
| `poll_config_interval` | `10` | Interval čtení bloků 5–6 v sekundách |
| `log_level` | `INFO` | Úroveň logování: DEBUG / INFO / WARNING / ERROR |

## Poznámky k síťovému přístupu

Addon používá `host_network: true` — proxy server je dostupný přímo na IP adrese HASS hostu na portu `server_port`.

## Modbus TCP vs RTU over TCP

MM-116 je připojen přes serial-to-Ethernet konvertor (port 10001) — komunikuje pomocí **Modbus RTU over TCP** (raw TCP, ne standardní Modbus TCP s MBAP hlavičkou). Addon proto používá `Framer.RTU` pro upstream spojení s MM-116 a standardní Modbus TCP pro downstream klienty.

## Lokální testování

```bash
pip install 'pymodbus==3.6.*'
python3 mm116-modbus-proxy/modbus_proxy.py \
  --mm116-host 192.168.2.15 \
  --mm116-port 10001 \
  --server-port 5020 \
  --poll-fast 1 \
  --poll-config 10 \
  --log-level DEBUG
```
