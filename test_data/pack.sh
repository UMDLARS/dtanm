#!/bin/bash

for d in */
do
    echo "Packing... '$d'"
    tar czf "${d%/}.tar.gz" $d
done
