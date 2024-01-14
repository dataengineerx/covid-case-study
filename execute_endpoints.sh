#!/bin/bash

#check argument countryterritoryCode 
if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    echo "Usage execute_endpoint.sh  countryterritoryCode"
    exit 1
fi

curl -X 'GET' \
  'http://localhost:8000/download/json' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/rolling-five-days/' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/total-cases/' \
  -H 'accept: application/json'

curl -X 'GET' \
  'http://localhost:8000/store-data/' \
  -H 'accept: application/json'
