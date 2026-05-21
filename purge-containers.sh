#!/usr/bin/env bash

CONT="$(docker container ls -a | tail -n +2)"

while IFS= read -r line; do
    docker container rm $(echo "$line" | head -c 12)
done <<< "$CONT"
