#!/bin/bash


mkdir -p /cctf/logs  #  create logs directory if not already created.

/usr/bin/mongod &
cd /cctf/server && npm start
#cd /cctf && python /cctf/bin/manager.py >> dtanm.log &
/cctf/scorer_server/main.py >> /cctf/logs/dtanm.out &

tail -f /cctf/logs/dtanm.out


