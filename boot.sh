#!/bin/sh

while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - main:app
