from fastapi import FastAPI, HTTPException
import requests
import json
import pandas as pd
from src.Utils import read_json_file_preprocess_data, write_to_delta_lake
from typing import List
import os
import pathlib

app = FastAPI()

if not os.path.exists("./data"):
    os.makedirs("./data")


root_dir = pathlib.Path(__file__).parent.parent.absolute()
source_file = os.path.join(root_dir, "data/downloaded_data")
source_json_file = os.path.join(root_dir, "data/downloaded_data.json")
total_cases_delta_table = os.path.join(root_dir, "data/total_cases.delta")
rolling_last_five_days_delta_table = os.path.join(
    root_dir, "data/rolling_last_five_days.delta"
)


def get_countryterritoryCode(df: pd.DataFrame) -> List:

    """
    This function returns a list of valid countryterritoryCode
    param: df: pandas dataframe
    return: list of valid countryterritoryCode
    """

    valid_country_territory_Code = df["countryterritoryCode"].unique()
    return valid_country_territory_Code.tolist()

def rolling_five_days(
    df: pd.DataFrame, countryterritoryCode: str = None
) -> pd.DataFrame:
    """
    This function returns the last five days of cases data per Territory
    param: df: pandas dataframe
    param: countryterritoryCode: countryterritoryCode
    return: pandas dataframe
    """

    valid_country_territory_Code = get_countryterritoryCode(df)
    if countryterritoryCode is None:

        print("processing all data")

        df["dense_rank"] = df.groupby("countryterritoryCode")["dateRep"].rank(method="dense", ascending=False)
        df = df[df["dense_rank"] <= 5][["countryterritoryCode", "dateRep", "cases"]]
        df = df.sort_values(by="countryterritoryCode", ascending=False).reset_index(drop=True)
        return df
    else:
        print(f"processing data for {countryterritoryCode}"),
        if countryterritoryCode not in valid_country_territory_Code:
            raise HTTPException(
                status_code=404,
                detail=f"""Invalid countryterritoryCode: {countryterritoryCode}
                Please enter a valid  from the following list: {valid_country_territory_Code}""",
            )
        
        
        df = df[df["countryterritoryCode"] == countryterritoryCode]
        df["dense_rank"] = df.groupby("countryterritoryCode")["dateRep"].rank(method="dense", ascending=False)
        df = df[df["dense_rank"] <= 5][["countryterritoryCode", "dateRep", "cases"]]
        df = df.sort_values(by="dateRep", ascending=False).reset_index(drop=True)
        return df


def total_cases_per_territory(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function returns the total cases per Territory
    param: df: pandas dataframe
    return: pandas dataframe
    """

    df = (
        df.groupby("countryterritoryCode")
        .sum("cases")
        .rename(columns={"cases": "total_cases"})
    )
    df = df.reset_index()[["countryterritoryCode", "total_cases"]]
    return df



@app.get("/")
async def home()-> dict:

    return {
        "message": """Welcome to the COVID-19 API.Please use the following endpoints to access the data""",
        "endpoints": [
            "/docs : This really cool shows the documentation for the API with ability to test the endpoints",
            "/download/json or /download/csv : This endpoint downloads the data from the source and saves it to a file"
            "/rolling-five-days : This endpoint returns the last five days of data per Territory",
            "/total-cases : This endpoint returns the total cases per Territory",
            "/store-data : This endpoint stores the data in delta lake ",
        ],
    }


# Endpoint to download JSON data from a URL and save it to a file
@app.get("/download/{data_format}")
async def download_data_file(data_format: str) -> dict:
    """
    This endpoint downloads the data from the source and saves it to a file
    param: data_format: data format to download the data in. Valid values are json or csv
    return: dict
    """
    url = f"https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/{data_format}"
    global source_file

    try:
        response = requests.get(url)
        response.raise_for_status()
        if data_format == "json":
            data = response.json()
            with open(source_file + ".json", "w") as file:
                json.dump(data, file)
        elif data_format == "csv":
            data = response.text
            with open(source_file + ".csv", "w") as file:
                file.write(data)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data format: {data_format}. Please enter a valid data format: json or csv",
            )

        return {"message": f"data downloaded and saved successfully to {source_json_file}"}
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error downloading {source_file} data: {str(e)}"
        )


@app.get("/rolling-five-days/{countryterritoryCode}")
async def get_rolling_five_days(countryterritoryCode: str):
    """
    This Endpoint returns the last five days of data per Territory
    param: countryterritoryCode: countryterritoryCode
    return: dict
    """

    try:
        df = read_json_file_preprocess_data(source_json_file)
        df = rolling_five_days(df, countryterritoryCode)
        df["dateRep"] = df["dateRep"].astype(str)
        df = df.to_dict(orient="records")
        return {
            "Content-Type": "application/json",
            "status": "success",
            "message": {
                "endpoint": "rolling-five-days",
                "description": "Last five days of data per Territory",
            },
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": df,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}.")


@app.get("/total-cases/")
async def get_total_cases_territory():
    """
    This Endpoint returns the total cases per Territory
    return: dict
    """

    try:
        df = read_json_file_preprocess_data(source_json_file)
        df = total_cases_per_territory(df)
        df = df.to_dict(orient="records")

        return {
            "Content-Type": "application/json",
            "status": "success",
            "message": {
                "endpoint": "total-cases",
                "description": "total cases per Territory",
            },
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": df,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing data from file : {source_file}: {str(e)} ",
        )


# Endpoint to store the data in SQLALCHEMY
@app.get("/store-data/")
async def store_data():
    """
    This endpoint stores the data in delta lake
    return: dict
    """
    try:
        df = read_json_file_preprocess_data(source_json_file)
        total_cases_df = total_cases_per_territory(df)
        rolling_last_five_days_df = rolling_five_days(df)
        write_to_delta_lake(df=total_cases_df, target_table=total_cases_delta_table)
        write_to_delta_lake(
            df=rolling_last_five_days_df,
            target_table=rolling_last_five_days_delta_table,
        )
        return {"status": "success", "message": "Data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")


# execute the main function
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
