from fastapi import FastAPI, HTTPException
import requests
import json
import pandas as pd
from src.Utils import read_and_process_data
from typing import List
from deltalake.writer import write_deltalake

app = FastAPI()

source_file = "src/data/downloaded_data.json"

def get_countryterritoryCode(df:pd.DataFrame)-> List:
    valid_country_territory_Code = df["countryterritoryCode"].unique()
    return valid_country_territory_Code.tolist()


def rolling_five_days(countryterritoryCode:str=None)-> pd.DataFrame:

    df = read_and_process_data(source_file)
    valid_country_territory_Code = get_countryterritoryCode(df)

    if countryterritoryCode is None:
        print("processing all data")
        # apply row number window function to get the last 5 days of data per countryterritoryCode ordered by dateRep descending
        df = df.sort_values(by="dateRep", ascending=False)
        df["row_number"] = df.groupby("countryterritoryCode").cumcount() + 1
        df = df[df["row_number"] <= 5]
        return df
    else:
        print("processing data for countryterritoryCode"),
        if countryterritoryCode not in valid_country_territory_Code:
            raise HTTPException(status_code=404, detail=f"Invalid countryterritoryCode: {countryterritoryCode}. Please enter a valid countryterritoryCode from the following list: {valid_country_territory_Code}")
        df = df[df["countryterritoryCode"] == countryterritoryCode]
        df = df.sort_values(by="dateRep", ascending=False)
        df = df.head(5)
        return df

def total_cases_per_territory(source_file:str)-> pd.DataFrame:
    df = read_and_process_data(source_file)
    df = df.groupby("countryterritoryCode").sum("cases")
    df = df.reset_index()[[ "countryterritoryCode", "cases"]]
    return df


# Endpoint to download JSON data from a URL and save it to a file
@app.get("/download-json/")
async def download_json():
    url = "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/json"
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Assuming the content is JSON, you can modify this logic accordingly
        data = response.json()
        #TODO: fix dir and file name
        # Save the JSON data to a file 
        with open(source_file, "w") as file:
            json.dump(data, file)

        return {"message": "JSON data downloaded and saved successfully"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error downloading JSON data: {str(e)}")



    
@app.get("/rolling-five-days/{countryterritoryCode}")
async def get_rolling_five_days(countryterritoryCode: str):

    try:
        df = rolling_five_days(countryterritoryCode)
        df = df.to_dict(orient="records")
        return {"status": "success", 
                "message": {"endpoint" :  "rolling-five-days", "description" : "Last five days of data per Territory"}, 
                "timestamp": pd.Timestamp.now(), "data": df
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}.")

@app.get("/total-cases/")
async def get_total_cases_territory():
    try:
        df = total_cases_per_territory(source_file)
        df = df.to_dict(orient="records")
        # return data in application-json format with status, message,timestamp,data
        return {"status": "success",
                "message": {"endpoint" :  "total-cases", "description" : "total cases per Territory"},
                "timestamp": pd.Timestamp.now(), "data": df}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}") 


# Endpoint to store the data in SQLALCHEMY
@app.get("/store-data/}")
async def store_data():
    try:
        total_cases_df = total_cases_per_territory(source_file)
        total_cases_df["load_ts"] = pd.Timestamp.now()
   
        write_deltalake("src/data/total_cases.delta", total_cases_df,mode="overwrite")

        rolling_five_days_df = rolling_five_days()
        #add current date column to rolling_five_days_df
        rolling_five_days_df["load_ts"] = pd.Timestamp.now()

        write_deltalake("src/data/rolling_five_days.delta", rolling_five_days_df,mode="append")
        return {"status": "success", "message": "Data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing data: {str(e)}")

# execute the main function
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
