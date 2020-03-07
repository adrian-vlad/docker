FROM buildpack-deps:disco

ENV JANUS_VERSION v0.9.0
ENV LIBNICE_VERSION 0.1.16

ENV JANUS_PORT_HTTP 8088
ENV JANUS_PORT_STREAMING_START 10000

ENV LIVE555_PORT_STREAMING_START 20000

ENV STREAMING_DIR_PATH /opt/streaming
ENV STREAMING_CFG_PATH ${STREAMING_DIR_PATH}/streaming.yml

ENV RECORDINGS_DIR_PATH /opt/static/recordings

RUN rm -rf /var/lib/apt/lists/*
RUN apt-get -y update && apt-get install -y \
    libmicrohttpd-dev \
    libjansson-dev \
    libssl-dev \
    libsrtp2-dev \
    libsofia-sip-ua-dev \
    libglib2.0-dev \
    libopus-dev \
    libogg-dev \
    libini-config-dev \
    libcollection-dev \
    libconfig-dev \
    pkg-config \
    gengetopt \
    libtool \
    automake \
    build-essential \
    git \
    cmake \
    gtk-doc-tools \
    && mkdir /tmp/libnice && cd /tmp/libnice \
    && git clone https://gitlab.freedesktop.org/libnice/libnice.git \
    && cd libnice \
    && git checkout ${LIBNICE_VERSION} \
    && bash autogen.sh \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && rm -rf /tmp/libnice \
    && mkdir /tmp/janus && cd /tmp/janus \
    && git clone https://github.com/meetecho/janus-gateway.git \
    && cd janus-gateway \
    && git checkout ${JANUS_VERSION} \
    && sh autogen.sh \
    && ./configure --disable-docs --disable-all-plugins --disable-all-transports --enable-plugin-streaming --enable-rest --enable-sample-event-handler --prefix=/opt/janus \
    && make \
    && make install \
    && make configs \
    && rm -rf /tmp/janus \
    && ldconfig \
    && apt-get -y remove --purge \
    git \
    cmake \
    automake \
    build-essential \
    pkg-config \
    gtk-doc-tools

RUN apt-get -y install \
    python3 \
    python3-pip \
    supervisor \
    ffmpeg \
    nginx \
    && python3 -m pip install pyyaml jinja2 flask gunicorn

# patch liveProxy code to increase it's buffer so it does not have any problems with big streams
# add port reuse flag
RUN wget http://www.live555.com/liveMedia/public/live555-latest.tar.gz \
    && mkdir live && tar -xf live555-latest.tar.gz -C live --strip-components 1 \
    && chmod -R +w live && cd live \
    && sed -i '/OutPacketBuffer::maxSize = 100000;/c \ \ OutPacketBuffer::maxSize = 10000000;' proxyServer/live555ProxyServer.cpp \
    && sed -i 's/80/0/g' proxyServer/live555ProxyServer.cpp \
    && sed -i '/^COMPILE_OPTS/ s/$/ -DALLOW_RTSP_SERVER_PORT_REUSE=1/' config.linux-64bit \
    && ./genMakefiles linux-64bit && make \
    && mkdir /opt/live555 \
    && cp proxyServer/live555ProxyServer /opt/live555/ \
    && cp testProgs/openRTSP /opt/live555

COPY etc/ /etc/
COPY opt/ /opt/

VOLUME ["${STREAMING_DIR_PATH}", "${RECORDINGS_DIR_PATH}"]

CMD ["sh", "-c", "exec sh /opt/scripts/start.sh"]
