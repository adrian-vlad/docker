#!/bin/bash

STOP=0
trap 'STOP=1' SIGINT SIGTERM

TARGET_DIR=/data/share

mkdir -p "${TARGET_DIR}"

while (( STOP != 1 ))
do
  if ! mountpoint -q "${TARGET_DIR}"; then
    mount --make-rshared -t glusterfs "${VOLUME_URL}" "${TARGET_DIR}"
  fi

  sleep 1
done

umount "${TARGET_DIR}" || umount -fl "${TARGET_DIR}"
