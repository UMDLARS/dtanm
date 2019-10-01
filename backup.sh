#!/bin/bash

backup_dir="$(pwd)/backup"

mkdir -p "$backup_dir"

docker run --rm --volumes-from dtanm_worker_1 -v "$backup_dir:/backup" ubuntu bash -c "cd /cctf && tar cvf /backup/cctf.tar ."
docker exec -t dtanm_db_1 pg_dumpall -c -U postgres > "$backup_dir/dump.sql"
