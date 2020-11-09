FROM debian:buster-slim
#FROM buildpack-deps:focal

ENV TZ=Europe/Bucharest
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get -y update && apt-get install -y \
    glusterfs-client

COPY mount_and_monitor.sh /usr/local/bin/

VOLUME ["/data"]

# must set VOLUME_URL
CMD ["bash", "/usr/local/bin/mount_and_monitor.sh"]
