# Registrová mapa MM-116

Zdroj: `MM116-MODBUS-REG.pdf` (FW-V1/2016-02-19)

> **Důležité:** Registry lze vyčítat pouze po celých blocích nebo více bloků po sobě — ne jednotlivé registry!

## Blok 0 — Identifikace (0x00–0x0F)

| Adresa | Název | Popis | Přístup | Typ |
|--------|-------|-------|---------|-----|
| 0x00 | ADR | Adresa na sběrnici (LSB) | R | 1x uchar |
| 0x01–0x04 | TYPE | Typové označení (string 8 znaků) | R | ASCII |
| 0x05 | HW/NM | Verze HW (MSB), modifikace (LSB) | R | 2x uchar |
| 0x06 | FW/NY | Verze FW (MSB) a rok (LSB) | R | 2x uchar |
| 0x07 | FW/MD | Datum FW – měsíc, den | R | 2x uchar |
| 0x08–0x09 | MXC | Kompatibilní verze MaxComm | R | ulong |
| 0x0A–0x0B | SN | Výrobní číslo | R | ulong |
| 0x0C–0x0D | ID | Identifikační číslo | **R/W** | ulong |
| 0x0E | CONFIG | Konfigurace (DIP) | R | bin |
| 0x0F | BRES | Návratový kód bootloaderu | R | uint |

## Blok 1 — Čas, status, paměť (0x10–0x1F)

| Adresa | Název | Popis | Přístup | Typ |
|--------|-------|-------|---------|-----|
| 0x10 | RTC/YM | Reálný čas / rok(MSB), měsíc | **R/W** | 2x uchar |
| 0x11 | RTC/DH | Reálný čas / den(MSB), hodina | **R/W** | 2x uchar |
| 0x12 | RTC/MS | Reálný čas / minuta(MSB), sekunda | **R/W** | 2x uchar |
| 0x13–0x14 | TICK | Systime – počet tiků od startu (10 ms) | R | ulong |
| 0x15 | T15 | Čas 1/4h intervalu měření (0.1 s) | R | uint |
| 0x16 | STATUS | Stav a diagnostika | R | bin |
| 0x17 | ACAP | Max počet záznamů v paměti + 1 | R | uint |
| 0x18 | ABEG | Index prvního záznamu v paměti | **R/W** | uint |
| 0x19 | AEND | Index posledního záznamu v paměti | **R/W** | uint |
| 0x1A | INPUTS | Binární (0/1) stav všech vstupů | R | bin |
| 0x1B | OUTPUTS | Binární (0/1) stav všech výstupů | R | bin |
| 0x1C | REGSTAT | Stav regulace (LSB) | R | uchar |

## Blok 2 — Statistika komunikace (0x20–0x2F)

| Adresa | Název | Popis | Přístup | Typ |
|--------|-------|-------|---------|-----|
| 0x20 | UE/PAR | Počet chyb rámce znaku a parity | R | uint |
| 0x21 | UE/OV-CH | Počet nezpracovaných znaků | R | uint |
| 0x22 | UE/OV-B | Počet přetečení vstupního bufferu | R | uint |
| 0x23 | MBE/FR | Počet fragmentů paketu < 5 znaků | R | uint |
| 0x24 | MBE/LEN | Počet paketů s neočekávanou délkou | R | uint |
| 0x25 | MBE/CRC | Počet paketů s neplatným CRC | R | uint |
| 0x26 | MBE/UNK | Počet paketů s neznámým kódem funkce | R | uint |
| 0x27 | MBE/CNT | Počet chybových paketů (FC+0x80) | R | uint |
| 0x28 | MBTXCNT | Počet odeslaných paketů | R | uint |
| 0x29 | LBITS | Kontrolní a řídicí bity | R | bin (8 bit) |
| 0x2A | FBITS | Kontrolní a řídicí bity | R | bin |

## Blok 3 — Vstupní buffer (0x30–0x3F)

Počet impulzů v T15 intervalu pro každý vstup.

| Adresa | Název | Vstup | Přístup | Typ |
|--------|-------|-------|---------|-----|
| 0x30 | BUF1 | Vstup 1 | R | uint |
| 0x31 | BUF2 | Vstup 2 | R | uint |
| … | … | … | R | uint |
| 0x3F | BUF16 | Vstup 16 | R | uint |

## Blok 4 — Průměrný interval mezi impulzy (0x40–0x5F)

Float32 hodnoty (word swap), jednotka ms.

| Adresa | Název | Vstup | Přístup | Typ |
|--------|-------|-------|---------|-----|
| 0x40–0x41 | PER1 | Vstup 1 | R | float |
| 0x42–0x43 | PER2 | Vstup 2 | R | float |
| … | … | … | R | float |
| 0x5E–0x5F | PER16 | Vstup 16 | R | float |

## Blok 5 — Převodní konstanty PPU (0x80–0x9F)

Převod impulzů na jednotky pro každý vstup. Float32 (word swap).

| Adresa | Název | Vstup | Přístup | Typ |
|--------|-------|-------|---------|-----|
| 0x80–0x81 | PPU1 | Vstup 1 | **R/W** | float |
| 0x82–0x83 | PPU2 | Vstup 2 | **R/W** | float |
| … | … | … | **R/W** | float |
| 0x9E–0x9F | PPU16 | Vstup 16 | **R/W** | float |

## Blok 6 — Parametry regulace (0xA0–0xAF)

| Adresa | Název | Popis | Přístup | Typ | Rozsah |
|--------|-------|-------|---------|-----|--------|
| 0xA0 | REGMAX | Regulované maximum | **R/W** | uint | |
| 0xA1 | KR | Krok regulace | **R/W** | uint | 1–300 s |
| 0xA2 | VZP | Vypínací/zapínací přímka (H/L) | **R/W** | 2x uchar | 0–99 % |
| 0xA3 | KZK | Klid na začátku/konci (H/L) | **R/W** | 2x uchar | 0–99 % |
| 0xA4 | MZ-PR | Mez zapínání / začátek predikce (H/L) | **R/W** | 2x uchar | 0–99 % |
| 0xA5 | MANUAL | Výstupy ručně: stav/maska (H/L) | **R/W** | bin | 8+8 bit |
| 0xA6 | HL-INV | Hladina vypínání / inverz. logika (H/L) | **R/W** | 2x uchar | 0–99 % |
| 0xA7 | ON-INT | Zapnuto OD / DO (H/L) | **R/W** | 2x uchar | 0–95 |
| 0xA8 | OFF-INT | Vypnuto OD / DO (H/L) | **R/W** | 2x uchar | 0–95 |
| 0xA9 | MN-ONOFF | Minimální doba vypnutí/provozu (H/L) | **R/W** | 2x uchar | 0–59 min |
| 0xAA | MAX-OFF | Maximální doba vypnutí (LSB) | **R/W** | 1x uchar | 0–59 min |
