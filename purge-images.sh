#!/usr/bin/env bash

CONT="$(docker image ls -a | tail -n +2)"

while IFS= read -r line; do
    docker image rm $(echo "$line" | cut -d ' ' -f 1)
done <<< "$CONT"
