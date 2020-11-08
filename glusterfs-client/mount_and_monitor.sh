#!/bin/bashs

TARGET_DIR=/data/share

mkdir -p "${TARGET_DIR}"

while true
do
  if ! mountpoint -q "${TARGET_DIR}"; then
    mount -t glusterfs "${VOLUME_URL}" "${TARGET_DIR}"
  fi

  sleep 1
done

umount "${TARGET_DIR}" || umount -fl "${TARGET_DIR}"
