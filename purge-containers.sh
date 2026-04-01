#!/usr/bin/env bash

while IFS= read -r line; do
    docker container rm "$line"
    echo "$line"
done < "$1"
