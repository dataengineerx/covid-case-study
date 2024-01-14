## Project Description

The project is based on covid case study. The source data is fetched from website using python rest api exposed using Fastapi framework.
The data is then cleaned and transformed using pandas and numpy. The data is then loaded into delta table as persistent storage.
There are few endpoints exposed which initially download covid cases data from [here](https://www.ecdc.europa.eu/en/publications-data/data-daily-new-cases-covid-19-eueea-country)


## Technologies Used
Ubuntu/Windows WSL : Liniux OS
Fastapi : FastAPI is rest api framework used to expose endpoints 
Python 3.11.7 :
docker : docker is used to containerize the application. Rancher Desktop/Docker Desktop
poetry : poetry is used to manage dependencies
airflow : airflow is used to schedule the job
Pandas : Pandas is used to clean and transform the data
Pytest : Pytest is used to write unit test cases

## Running the project locally 

    poetry install # make sure you are in project root directory with pyproject.toml
    poetry run uvicorn src.main:app --reload 

## Available endpoints

    curl -X 'GET' \
    'http://localhost:8000/<endpoint>' \
    -H 'accept: application/json'

    /download/json : This endpoint is used to download json data from http source and save it to data dir 
    /docs : This really cool shows the documentation for the API with ability to test the endpoints
    /rolling-five-days : This endpoint returns the last five days of data per Territory",
    /total-cases : This endpoint returns the total cases per Territory
    /store-data : This endpoint stores the data in delta lake



## Running the project in docker
    
    docker build . -t <imagename>:<tag>
    docker run -it  -p 8000:8000  <imagename>:<tag>

    Optionally using docker compose
    docker-compose build 
    docker compose up

## Scheduler
    #job is scheduled every monday and thursday at 00:00 UTC every week using airflow scheduler
    airflow dags list
    airflow dags trigger store_covid_delta_dataset

## Locally deployment 
    sh deploy.sh 
This scripts does following:
- Build docker image
- Execute docker compose which expose the application on port 8000 
- Run pytest to run unit test cases
- Run endpoints locally
- Run airflow scheduler to schedule the job every monday and thursday at 00:00 UTC every week

    