FROM debian:buster-slim
#FROM buildpack-deps:focal

#TODO different user

ENV TZ=Europe/Bucharest
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && apt-get install -y \
    glusterfs-server

VOLUME ["/var/lib/glusterd", "/var/log/glusterfs", "/data"]

EXPOSE 24007 24008
EXPOSE 49152-49160

ENV LOG_LEVEL=INFO

CMD exec /usr/sbin/glusterd -N --log-level ${LOG_LEVEL}
