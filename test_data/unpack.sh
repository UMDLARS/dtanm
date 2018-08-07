#!/bin/bash

for f in *.tar.gz
do
    echo "Unpacking '$f'"
    tar xf "$f"
done
