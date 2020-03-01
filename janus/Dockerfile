FROM buildpack-deps:disco

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
    && ./configure --enable-static --disable-websockets --disable-data-channels --disable-rabbitmq --disable-docs --prefix=/opt/janus \
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

VOLUME /etc/janus

EXPOSE 8088/tcp 8000/udp

CMD ["/opt/janus/bin/janus", "-F", "/etc/janus"]

