FROM python:3.8-alpine

RUN adduser -D essarch

WORKDIR /ESSArch

COPY config config

RUN chown -R essarch:essarch ./

USER essarch

VOLUME /ESSArch/config

ENTRYPOINT /bin/bash