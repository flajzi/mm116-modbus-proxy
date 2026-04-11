#!/bin/sh

echo "Starting MM-116 Modbus Proxy..."

CONFIG=/data/options.json

MM116_HOST=$(jq -r '.mm116_host' "$CONFIG")
MM116_PORT=$(jq -r '.mm116_port' "$CONFIG")
MM116_SLAVE_ID=$(jq -r '.mm116_slave_id' "$CONFIG")
SERVER_PORT=$(jq -r '.server_port' "$CONFIG")
POLL_FAST=$(jq -r '.poll_fast_interval' "$CONFIG")
POLL_CONFIG=$(jq -r '.poll_config_interval' "$CONFIG")
LOG_LEVEL=$(jq -r '.log_level' "$CONFIG")

exec python3 /modbus_proxy.py \
  --mm116-host "$MM116_HOST" \
  --mm116-port "$MM116_PORT" \
  --mm116-slave-id "$MM116_SLAVE_ID" \
  --server-port "$SERVER_PORT" \
  --poll-fast "$POLL_FAST" \
  --poll-config "$POLL_CONFIG" \
  --log-level "$LOG_LEVEL"
