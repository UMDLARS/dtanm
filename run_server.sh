#!/bin/bash

/usr/bin/mongod &
cd /cctf/server && npm start
#cd /cctf && python /cctf/bin/manager.py >> dtanm.log &
cd /cctf && python /cctf/bin/main.py >> /cctf/server/dtanm.out &

tail -f /cctf/server/dtanm.out


