#!/usr/bin/env bash

while IFS= read -r line; do
    docker image rm "$line"
    echo "$line"
done < "$1"
