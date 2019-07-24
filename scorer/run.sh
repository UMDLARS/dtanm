#!/bin/bash


case "$SCORER_SERVICE" in
    web)
        # If reset is set then reset
        if [ "$RESET" = "1" ]; then
            echo "Resetting..."
            /data/reset_data.sh
        fi
        echo "Starting web..."
        #FLASK_APP=web.py FLASK_ENV=development pipenv run flask run --host=0.0.0.0
        pipenv run uwsgi --http 0.0.0.0:5000 --wsgi-file web.py --callable app --processes 1 --threads 1 --stats 127.0.0.1:9191
        ;;
    tasker)
        echo "Starting tasker..."
        pipenv run python run_tasker.py
        ;;
    worker)
        echo "Starting worker..."
        pipenv run python run_worker.py
        ;;
    *)
        echo $"Usage: $0 with SCORER_SERVICE={web|tasker|worker}"
        exit 1
esac

