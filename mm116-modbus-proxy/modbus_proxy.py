#!/usr/bin/env python3
"""MM-116 Modbus TCP Proxy/Multiplexer.

Connects to an MM-116 device (single-connection Modbus TCP server),
periodically reads all holding register blocks into a local cache,
and serves them via its own Modbus TCP server to multiple clients.
Writes to R/W registers are forwarded to the real device (write-through).
"""

import argparse
import asyncio
import logging
import signal
from dataclasses import dataclass

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.datastore import (
    ModbusServerContext,
    ModbusSlaveContext,
    ModbusSparseDataBlock,
)
from pymodbus.framer import Framer
from pymodbus.server import StartAsyncTcpServer

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Register block definitions (from MM-116 PDF)
# ---------------------------------------------------------------------------

POLL_FAST = "fast"
POLL_CONFIG = "config"


@dataclass
class RegisterBlock:
    name: str
    start: int
    count: int
    schedule: str
    writable: bool


REGISTER_BLOCKS = [
    RegisterBlock("identifikace", 0x00, 16, POLL_FAST, writable=False),
    RegisterBlock("cas_status", 0x10, 16, POLL_FAST, writable=True),
    RegisterBlock("statistika", 0x20, 16, POLL_FAST, writable=False),
    RegisterBlock("vstupni_buffer", 0x30, 16, POLL_FAST, writable=False),
    RegisterBlock("interval_imp", 0x40, 32, POLL_FAST, writable=False),
    RegisterBlock("prevodni_konst", 0x80, 32, POLL_CONFIG, writable=True),
    RegisterBlock("param_regulace", 0xA0, 16, POLL_CONFIG, writable=True),
]

# Writable register ranges (for write-through validation)
WRITABLE_RANGES = [
    (0x0C, 0x0D),  # ID (R/W)
    (0x10, 0x12),  # RTC/YM, RTC/DH, RTC/MS
    (0x18, 0x19),  # ABEG, AEND
    (0x80, 0x9F),  # PPU1-PPU16
    (0xA0, 0xAF),  # Regulation parameters
]


def _is_writable(address: int, count: int) -> bool:
    """Check if an address range falls within writable registers."""
    end = address + count - 1
    return any(start <= address and end <= stop for start, stop in WRITABLE_RANGES)


# ---------------------------------------------------------------------------
# Custom DataBlock with write-through
# ---------------------------------------------------------------------------


class WriteThruDataBlock(ModbusSparseDataBlock):
    """Holding register data block that forwards writes to the real MM-116."""

    def __init__(self, upstream_client: AsyncModbusTcpClient, slave_id: int):
        # Pre-populate address space 0x00-0xAF with zeros
        values = {addr: 0 for addr in range(0x00, 0xB0)}
        super().__init__(values)
        self._upstream = upstream_client
        self._slave_id = slave_id
        self._loop: asyncio.AbstractEventLoop | None = None

    def update_from_device(self, modbus_address: int, registers: list[int]):
        """Update cache from polled device data (no write-through)."""
        super().setValues(modbus_address, registers)

    def setValues(self, address, values):
        """Called by pymodbus server when a downstream client writes registers."""
        if not _is_writable(address, len(values)):
            log.warning("Write rejected: 0x%02X (%d regs) is read-only", address, len(values))
            return

        # Update local cache immediately (optimistic)
        super().setValues(address, values)

        # Schedule write-through to real device
        if self._loop and self._loop.is_running():
            self._loop.create_task(self._write_through(address, values))

    async def _write_through(self, address: int, values: list[int]):
        """Forward the write to the real MM-116 device."""
        try:
            result = await self._upstream.write_registers(
                address, values, slave=self._slave_id
            )
            if result.isError():
                log.error("Write-through failed at 0x%02X: %s", address, result)
            else:
                log.info("Write-through OK at 0x%02X, %d regs", address, len(values))
        except Exception as e:
            log.error("Write-through exception at 0x%02X: %s", address, e)


# ---------------------------------------------------------------------------
# Main proxy application
# ---------------------------------------------------------------------------


class MM116ModbusProxy:
    def __init__(self, args: argparse.Namespace):
        self.mm116_host = args.mm116_host
        self.mm116_port = args.mm116_port
        self.slave_id = args.mm116_slave_id
        self.server_port = args.server_port
        self.poll_fast = args.poll_fast
        self.poll_config = args.poll_config
        self.client: AsyncModbusTcpClient | None = None
        self.datablock: WriteThruDataBlock | None = None
        self._running = True

    # -- connection ---------------------------------------------------------

    async def _connect(self):
        """Connect the upstream Modbus TCP client to MM-116."""
        self.client = AsyncModbusTcpClient(
            host=self.mm116_host,
            port=self.mm116_port,
            framer=Framer.RTU,
            timeout=5,
            retries=3,
            reconnect_delay=2,
            reconnect_delay_max=30,
        )
        connected = await self.client.connect()
        if connected:
            log.info("Connected to MM-116 at %s:%d", self.mm116_host, self.mm116_port)
        else:
            log.error("Failed to connect to MM-116 at %s:%d", self.mm116_host, self.mm116_port)
        return connected

    async def _reconnect(self):
        """Reconnect to MM-116 with exponential backoff."""
        log.warning("Connection lost, reconnecting...")
        try:
            self.client.close()
        except Exception:
            pass
        for attempt in range(1, 11):
            delay = min(2**attempt, 30)
            await asyncio.sleep(delay)
            try:
                connected = await self.client.connect()
                if connected:
                    log.info("Reconnected to MM-116 (attempt %d)", attempt)
                    return
            except Exception as e:
                log.warning("Reconnect attempt %d failed: %s", attempt, e)
        log.critical("Could not reconnect after 10 attempts")

    # -- polling ------------------------------------------------------------

    async def _poll_registers(self, start: int, count: int, label: str):
        """Read a contiguous block of holding registers and update cache."""
        try:
            result = await self.client.read_holding_registers(
                address=start, count=count, slave=self.slave_id
            )
            if result.isError():
                log.error("Poll %s failed: %s", label, result)
                return False
            # Update cache directly (bypasses write-through)
            self.datablock.update_from_device(start, result.registers)
            log.debug("Poll %s OK, %d regs", label, len(result.registers))
            return True
        except Exception as e:
            log.error("Poll %s exception: %s", label, e)
            await self._reconnect()
            return False

    async def _poll_loop_fast(self):
        """Poll blocks 0-4 (0x00-0x5F, 96 registers) at fast interval."""
        while self._running:
            await asyncio.sleep(self.poll_fast)
            await self._poll_registers(0x00, 96, "0x00-0x5F")

    async def _poll_loop_config(self):
        """Poll blocks 5-6 (0x80-0xAF, 48 registers) at config interval."""
        while self._running:
            await asyncio.sleep(self.poll_config)
            await self._poll_registers(0x80, 48, "0x80-0xAF")

    # -- main ---------------------------------------------------------------

    async def run(self):
        """Start the proxy: connect, do initial read, start server + polling."""
        # 1. Connect to MM-116
        if not await self._connect():
            log.error("Initial connection failed, retrying...")
            await self._reconnect()

        # 2. Initial read to populate cache
        self.datablock = WriteThruDataBlock(self.client, self.slave_id)
        self.datablock._loop = asyncio.get_running_loop()

        await self._poll_registers(0x00, 96, "0x00-0x5F (initial)")
        await self._poll_registers(0x80, 48, "0x80-0xAF (initial)")

        # 3. Build Modbus server context
        slave_ctx = ModbusSlaveContext(
            hr=self.datablock,  # holding registers (FC 3/6/16)
            ir=self.datablock,  # input registers (FC 4) — same data
            zero_mode=True,
        )
        server_ctx = ModbusServerContext(
            slaves={self.slave_id: slave_ctx},
            single=False,
        )

        log.info("Starting Modbus TCP server on 0.0.0.0:%d", self.server_port)

        # 4. Run server + polling concurrently
        await asyncio.gather(
            StartAsyncTcpServer(
                context=server_ctx,
                address=("0.0.0.0", self.server_port),
            ),
            self._poll_loop_fast(),
            self._poll_loop_config(),
        )

    async def shutdown(self):
        """Graceful shutdown."""
        log.info("Shutting down...")
        self._running = False
        if self.client:
            self.client.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="MM-116 Modbus TCP Proxy")
    p.add_argument("--mm116-host", required=True, help="MM-116 device IP address")
    p.add_argument("--mm116-port", type=int, default=10001, help="MM-116 device port")
    p.add_argument("--mm116-slave-id", type=int, default=1, help="Modbus slave ID")
    p.add_argument("--server-port", type=int, default=5020, help="Proxy server port")
    p.add_argument("--poll-fast", type=int, default=2, help="Fast poll interval (seconds)")
    p.add_argument("--poll-config", type=int, default=30, help="Config poll interval (seconds)")
    p.add_argument("--log-level", default="INFO", help="Logging level")
    return p.parse_args()


async def main():
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    proxy = MM116ModbusProxy(args)

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(proxy.shutdown()))

    await proxy.run()


if __name__ == "__main__":
    asyncio.run(main())
