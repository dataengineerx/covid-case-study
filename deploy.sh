#!/bin/bash

poetry run pytest test/
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Some tests failed"
    exit 1
fi

#docker build ./Dockerfile7

docker-compose build 
docker compose up &


poetry run airflow standalone &

poetry run airflow connections add fastapi_get --conn-host http://localhost --conn-port 8000 --conn-type http

poetry run airflow dags trigger store_covid_delta_dataset