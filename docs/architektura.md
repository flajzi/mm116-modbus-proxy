# Architektura addonu

## Problém

MM-116 má Modbus TCP server, který podporuje **pouze jedno simultánní spojení**. HASS i další klienti se nemohou připojit zároveň.

## Řešení: Modbus TCP proxy/multiplexer

Addon se připojí k MM-116 jako **jediný klient**, periodicky čte všechny registry do cache a poskytuje je přes vlastní Modbus TCP server libovolnému počtu klientů.

```
┌─────────────────────────────────────────┐
│            Home Assistant               │
│                                         │
│  ┌──────────────┐    ┌───────────────┐  │
│  │  HASS Modbus │    │ Jiný klient   │  │
│  │  integrace   │    │ (např. Node-  │  │
│  └──────┬───────┘    │  RED, apod.)  │  │
│         │            └───────┬───────┘  │
│         └────────────────────┘          │
│                    │ Modbus TCP          │
│                    ▼ (port 5020)        │
│         ┌──────────────────────┐        │
│         │  mm116-modbus-proxy  │        │
│         │                      │        │
│         │  cache registrů      │        │
│         │  poll každou 1s      │        │
│         └──────────┬───────────┘        │
└────────────────────│────────────────────┘
                     │ Modbus RTU over TCP
                     ▼ (192.168.2.15:10001)
              ┌──────────────┐
              │    MM-116    │
              │ (1 spojení)  │
              └──────────────┘
```

## Komponenty

### modbus_proxy.py
Hlavní Python aplikace (asyncio):
- **Upstream klient** — `AsyncModbusTcpClient` s `Framer.RTU` (MM-116 používá Modbus RTU over TCP)
- **WriteThruDataBlock** — `ModbusSparseDataBlock` s write-through logikou
- **Downstream server** — `StartAsyncTcpServer` (standardní Modbus TCP)
- **Polling smyčky** — dva asyncio tasky (fast + config)

### Polling strategie

| Smyčka | Interval | Registry | Bloky |
|--------|----------|----------|-------|
| fast | 1 s | 0x00–0x5F (96 reg.) | Identifikace, Čas/status, Statistika, Buffer, Periody |
| config | 10 s | 0x80–0xAF (48 reg.) | Převodní konstanty, Parametry regulace |

Bloky se čtou kontiguózně (jeden Modbus request na smyčku) — vyžaduje to PDF: *"Registry lze vyčítat pouze po celých blocích nebo více bloků po sobě"*.

### Write-through

Zápisy od downstream klientů do R/W registrů se přeposílají na MM-116:
1. Cache se aktualizuje okamžitě (optimisticky)
2. Upstream zápis proběhne jako asyncio task (fire-and-forget)
3. Další poll cyklus hodnotu ověří
