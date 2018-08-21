#!/bin/bash

pipenv run uwsgi --http 0.0.0.0:3001 --wsgi-file web.py --callable app --processes 1 --threads 1 --stats 127.0.0.1:9191
