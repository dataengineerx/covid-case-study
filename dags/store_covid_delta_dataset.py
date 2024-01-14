from airflow.models import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from datetime import datetime
import json

def check(response):
    """
    This function checks if the response is valid
    :param response: response from the API
    """
    if response.status_code == 200:
        print("Returning True")
        print(response.json())
        return True
    else:
        print("Returning False")
        return False

  
with DAG(
    dag_id="store_covid_delta_dataset",
    schedule_interval= "0 0 * * 1,4" , 
    start_date=datetime(2024, 1, 13),
    catchup=False,
) as dag:
    
    # define the sensor
    is_api_available = HttpSensor(
        task_id="is_api_available",
        http_conn_id="fastapi_get",
        endpoint="/",
        response_check=lambda response: True if check(response) is True else False,
        poke_interval=1,
        timeout=5,
    )

    #download source data 
    download_data_file = SimpleHttpOperator(
        task_id="download_data_file",
        http_conn_id="fastapi_get",
        endpoint="download/json",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )

    # define the operator
    get_data = SimpleHttpOperator(
        task_id="get_data",
        http_conn_id="fastapi_get",
        endpoint="store-data",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )

    # define the order of the tasks
    is_api_available >> download_data_file >> get_data
