#!/bin/bash

STOP=0
trap 'STOP=1' SIGINT SIGTERM

TARGET_DIR=/data

while (( STOP != 1 ))
do
  if ! findmnt "${TARGET_DIR}" | grep -q "${VOLUME_URL}"; then
    mount --make-rshared -t glusterfs -o backup-volfile-servers="${BACKUP_VOLUME_SERVERS}" "${VOLUME_URL}" "${TARGET_DIR}"
  fi

  sleep 1
done

umount "${TARGET_DIR}" || umount -fl "${TARGET_DIR}"
