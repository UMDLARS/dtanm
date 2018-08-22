#!/bin/bash

cd /data
tar xvf mock_root.tar.gz mock_root
rm -rf /cctf/*
cp -r /data/mock_root/cctf/* /cctf/
