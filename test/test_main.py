from src.main import *
from fastapi.testclient import TestClient
from pandas.testing import assert_frame_equal

client = TestClient(app)


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