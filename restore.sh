#!/bin/bash

backup_dir="$(pwd)/backup"

docker-compose down
docker volume rm dtanm_cctf
docker volume rm dtanm_db_data

docker volume create dtanm_cctf
docker run --rm -v dtanm_cctf:/recover -v "$backup_dir:/backup" ubuntu bash -c "cd /recover && tar xvf /backup/cctf.tar"
docker-compose up -d
cat "$backup_dir/dump.sql" | docker exec -i dtanm_db_1 psql -U postgres

