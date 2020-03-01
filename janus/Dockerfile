FROM buildpack-deps:disco

ENV JANUS_PORT_HTTP 8088
ENV JANUS_PORT_STREAMING_START 10000

ENV JANUS_INSTALL_DIR /opt/janus
ENV JANUS_CFG_DIR ${JANUS_INSTALL_DIR}/etc/janus
ENV JANUS_BIN_PATH ${JANUS_INSTALL_DIR}/bin/janus

ENV STREAMING_DIR_PATH /opt/streaming
ENV STREAMING_CFG_PATH ${STREAMING_DIR_PATH}/streaming.yml

ENV SCRIPTS_DIR_PATH /opt/app
ENV SCRIPTS_START_PATH ${SCRIPTS_DIR_PATH}/start.sh

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
    && git checkout 0.1.16 \
    && bash autogen.sh \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && rm -rf /tmp/libnice \
    && mkdir /tmp/janus && cd /tmp/janus \
    && git clone https://github.com/meetecho/janus-gateway.git \
    && cd janus-gateway \
    && sh autogen.sh \
    && ./configure --disable-docs --disable-all-plugins --disable-all-transports --enable-plugin-streaming --enable-rest --enable-sample-event-handler --prefix=${JANUS_INSTALL_DIR} \
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
    && python3 -m pip install pyyaml

COPY etc/* ${JANUS_CFG_DIR}/

COPY scripts/* ${SCRIPTS_DIR_PATH}/

VOLUME ["${STREAMING_DIR_PATH}"]

CMD ["sh", "-c", "exec sh ${SCRIPTS_START_PATH}"]

# CMD ffmpeg -loglevel error -i rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov -an -c:v copy -flags global_header -bsf dump_extra -f rtp rtp://192.168.111.16:10001
