# write airflow python code to run the http operator to get the data from the api localhost:3000/store-data

# import the required libraries
from airflow.models import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from datetime import datetime
import json


with DAG(
    dag_id="store_covid_delta_dataset",
    schedule_interval="@weekly",
    start_date=datetime(2021, 1, 1),
    catchup=False,
) as dag:
    # define the sensor
    is_api_available = HttpSensor(
        task_id="is_api_available",
        http_conn_id="store_api",
        endpoint="store-data",
        response_check=lambda response: "Store Name" in response.text,
        poke_interval=5,
        timeout=20,
    )

    # define the operator
    get_data = SimpleHttpOperator(
        task_id="get_data",
        http_conn_id="api_get",
        endpoint="store-data",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )

    # define the order of the tasks
    is_api_available >> get_data
