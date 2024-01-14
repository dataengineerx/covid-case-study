from src.main import *
from fastapi.testclient import TestClient
from pandas.testing import assert_frame_equal
import tempfile
import pytest

client = TestClient(app)

@pytest.fixture
def temp_dir(tmpdir):
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_download_data_endpoint():
    response = client.get("/download/json")
    assert response.status_code == 200
    output_json = response.json()
    assert output_json["message"] == f"data downloaded and saved successfully to {source_json_file}"
    assert os.path.exists(source_json_file)

def test_rolling_five_days_per_territory():
    input_data = [
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-06",
            "cases": 34,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-10",
            "cases": 56,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-09",
            "cases": 34,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-09",
            "cases": 44,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-07",
            "cases": 23,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-11",
            "cases": 66,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-05",
            "cases": 34,
        },
    ]

    expected_data = [
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-11",
            "cases": 66,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-10",
            "cases": 56,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-09",
            "cases": 34,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-09",
            "cases": 44,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-07",
            "cases": 23,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-06",
            "cases": 34,
        },
    ]

    output_df = rolling_five_days(pd.DataFrame(input_data), "AUT")

    expected_df = pd.DataFrame(expected_data)

    assert_frame_equal(output_df, expected_df,check_like=False)

def test_rolling_five_days_all_territories():
    input_data = [
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-06",
            "cases": 34,
        },
        {
            "countryterritoryCode": "LUX",
            "dateRep": "2020-04-10",
            "cases": 56,
        },
        {
            "countryterritoryCode": "DEU",
            "dateRep": "2020-04-09",
            "cases": 34,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-09",
            "cases": 44,
        },
        {
            "countryterritoryCode": "DEU",
            "dateRep": "2020-04-07",
            "cases": 23,
        },
        {
            "countryterritoryCode": "GRC",
            "dateRep": "2020-04-11",
            "cases": 66,
        },
        {
            "countryterritoryCode": "EST",
            "dateRep": "2020-04-05",
            "cases": 34,
        },
    ]

    expected_data = [
       
        {
            "countryterritoryCode": "LUX",
            "dateRep": "2020-04-10",
            "cases": 56,
        },
        {
            "countryterritoryCode": "GRC",
            "dateRep": "2020-04-11",
            "cases": 66,
        },
        {
            "countryterritoryCode": "EST",
            "dateRep": "2020-04-05",
            "cases": 34,
        },
        {
            "countryterritoryCode": "DEU",
            "dateRep": "2020-04-09",
            "cases": 34,
        },
        {
            "countryterritoryCode": "DEU",
            "dateRep": "2020-04-07",
            "cases": 23,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-06",
            "cases": 34,
        },
        
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-09",
            "cases": 44,
        },
        
        
    ]

    output_df = rolling_five_days(pd.DataFrame(input_data))

    expected_df = pd.DataFrame(expected_data)

    assert_frame_equal(output_df, expected_df,check_like=False)


    #create unit tests for total_cases_per_territory 

def test_total_cases_per_territory():
    input_data = [
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-06",
            "total_cases": 34,
        },
        {
            "countryterritoryCode": "AUT",
            "dateRep": "2020-04-10",
            "total_cases": 56,
        },

        {
            "countryterritoryCode": "LUX",
            "dateRep": "2020-04-05",
            "total_cases": 34,
        },
    ]

    expected_data = [
        {
            "countryterritoryCode": "AUT",
            "total_cases": 90,
        },
         {
            "countryterritoryCode": "LUX",
            "total_cases": 34,
        },
    ]
    

    output_df = total_cases_per_territory(pd.DataFrame(input_data))

    expected_df = pd.DataFrame(expected_data)

    assert_frame_equal(output_df, expected_df,check_like=False)


#write test for /rolling-five-days endpoint
def test_rolling_five_days_endpoint():
    response = client.get("/rolling-five-days/AUT")
    output_json = response.json()
    assert response.status_code == 200
    assert output_json["Content-Type"] == "application/json"
    assert output_json["status"] == "success"
    assert output_json["message"]["endpoint"] == "rolling-five-days"
    assert output_json["message"]["description"] == "Last five days of data per Territory"
    

#test for /total-cases endpoint
def test_total_cases_endpoint():
    response = client.get("/total-cases")
    assert response.status_code == 200
    output_json = response.json()
    assert output_json["status"] == "success"
    assert output_json["message"]["endpoint"] == "total-cases"
    assert output_json["message"]["description"] == "total cases per Territory"


def test_store_data_endpoint():
    response = client.get("/store-data")
    assert response.status_code == 200
    output_json = response.json()
    assert output_json["status"] == "success"
    assert output_json["message"] == "Data stored successfully"
    assert os.path.exists(total_cases_delta_table)
    assert os.path.exists(rolling_last_five_days_delta_table)