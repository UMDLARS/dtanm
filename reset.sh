#!/bin/bash

docker compose down
docker volume rm dtanm_cctf
docker volume rm dtanm_db_data
docker volume rm dtanm_args
docker volume rm dtanm_pack
