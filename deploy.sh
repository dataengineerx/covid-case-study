#docker build ./Dockerfile

docker build . -t covid-case-study:0.1

docker run -it  -p 80:80  covid-case-study:0.1 

poetry run pytest test/
if [ $? -eq 0 ]; then
    echo "All tests passed"
else
    echo "Some tests failed"
    exit 1
fi

#docker build ./Dockerfile

docker build . -t covid-case-study:0.1

docker run -it  -p 80:80  covid-case-study:0.1 

curl -X 'GET' \
  'http://localhost/download/json' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost/rolling-five-days/c' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost/total-cases/' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost/store-data/' \
  -H 'accept: application/json'

container_id=$(docker ps -a | grep covid-case-study | awk '{print $1}' | head -n 1)
docker cp $container_id:/app/data data