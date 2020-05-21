#!/bin/bash
if [ "$DATABASE" == "postgres" ]
then
    echo "waiting for postgres..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.5
    done

    echo "PostgreSQL started"
fi

python manage.py migrate --noinput

exec "$@"
