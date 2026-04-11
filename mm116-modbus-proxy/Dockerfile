ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip && \
    pip3 install --no-cache-dir --break-system-packages pymodbus==3.6.*

COPY modbus_proxy.py /
COPY run.sh /etc/services.d/mm116-proxy/run
RUN chmod a+x /etc/services.d/mm116-proxy/run
