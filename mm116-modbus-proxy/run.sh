#!/usr/bin/with-bashio
# shellcheck shell=bash

bashio::log.info "Starting MM-116 Modbus Proxy..."

MM116_HOST=$(bashio::config 'mm116_host')
MM116_PORT=$(bashio::config 'mm116_port')
MM116_SLAVE_ID=$(bashio::config 'mm116_slave_id')
SERVER_PORT=$(bashio::config 'server_port')
POLL_FAST=$(bashio::config 'poll_fast_interval')
POLL_CONFIG=$(bashio::config 'poll_config_interval')
LOG_LEVEL=$(bashio::config 'log_level')

exec python3 /modbus_proxy.py \
  --mm116-host "$MM116_HOST" \
  --mm116-port "$MM116_PORT" \
  --mm116-slave-id "$MM116_SLAVE_ID" \
  --server-port "$SERVER_PORT" \
  --poll-fast "$POLL_FAST" \
  --poll-config "$POLL_CONFIG" \
  --log-level "$LOG_LEVEL"
