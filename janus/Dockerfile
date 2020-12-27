FROM canyan/janus-gateway:latest

ENV JANUS_PORT_HTTP 8088
ENV JANUS_PORT_STREAMING_START 10000

ENV LIVE555_PORT_STREAMING_START 20000

ENV STREAMING_DIR_PATH /opt/streaming
ENV STREAMING_CFG_PATH ${STREAMING_DIR_PATH}/streaming.yml

ENV RECORDINGS_DIR_PATH /opt/static/recordings

RUN apt-get -y update && apt-get -y install \
    python3 \
    python3-pip \
    ffmpeg \
    nginx \
    mediainfo \
    wget \
    && python3 -m pip install pyyaml jinja2 flask gunicorn supervisor pymediainfo

# patch liveProxy code to increase it's buffer so it does not have any problems with big streams
# add port reuse flag
RUN wget https://download.videolan.org/pub/contrib/live555/live.2020.11.22.tar.gz -O live555.tar.gz \
    && mkdir live && tar -xf live555.tar.gz -C live --strip-components 1 \
    && chmod -R +w live && cd live \
    && sed -i '/OutPacketBuffer::maxSize = 100000;/c \ \ OutPacketBuffer::maxSize = 10000000;' proxyServer/live555ProxyServer.cpp \
    && sed -i 's/80/0/g' proxyServer/live555ProxyServer.cpp \
    && sed -i '/^COMPILE_OPTS/ s/$/ -DALLOW_RTSP_SERVER_PORT_REUSE=1/' config.linux-64bit \
    && apt-get -y install \
        libssl-dev \
    && ./genMakefiles linux-64bit && make \
    && mkdir /opt/live555 \
    && cp proxyServer/live555ProxyServer /opt/live555/ \
    && cp testProgs/openRTSP /opt/live555

COPY etc/ /etc/
COPY opt/ /opt/

VOLUME ["${STREAMING_DIR_PATH}", "${RECORDINGS_DIR_PATH}"]

CMD ["sh", "-c", "exec sh /opt/scripts/start.sh"]
