ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache python3 py3-pip jq && \
    pip3 install --no-cache-dir --break-system-packages pymodbus==3.6.*

COPY run.sh /
COPY modbus_proxy.py /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
