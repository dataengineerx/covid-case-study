#docker build ./Dockerfile

docker-compose build 
docker compose up


poetry run pytest test/
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Some tests failed"
    exit 1
fi

curl -X 'GET' \
  'http://localhost:8000/download/json' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/rolling-five-days/c' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/total-cases/' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/store-data/' \
  -H 'accept: application/json'


poetry run airflow standalone --port 8080

airflow connections add fastapi_get --conn-host http://localhost --conn-port 8000 --conn-type http

airflow dags trigger store_covid_delta_dataset