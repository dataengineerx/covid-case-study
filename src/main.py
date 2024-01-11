from fastapi import FastAPI, HTTPException
import requests
import json
import pandas as pd
from .Utils import read_and_process_data


app = FastAPI()


# Endpoint to download JSON data from a URL and save it to a file
@app.get("/download-json/")
async def download_json():
    url = "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/json"
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Assuming the content is JSON, you can modify this logic accordingly
        data = response.json()

        # Save the JSON data to a file
        with open("downloaded_data.json", "w") as file:
            json.dump(data, file)

        return {"message": "JSON data downloaded and saved successfully"}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error downloading JSON data: {str(e)}")



    
@app.get("/rolling-five-days/{countryterritoryCode}")
async def rolling_five_days(countryterritoryCode: str):

    #throw error if countryterritoryCode is None
    if countryterritoryCode is None:
        raise HTTPException(status_code=404, detail=f"Invalid countryterritoryCode: {countryterritoryCode}")

    try:
        df = read_and_process_data("downloaded_data.json")
        valid_country_territory_Code = df["countryterritoryCode"].unique()
        if countryterritoryCode not in valid_country_territory_Code:
            raise HTTPException(status_code=404, detail=f"Invalid countryterritoryCode: {countryterritoryCode}")
        df = df[df["countryterritoryCode"] == countryterritoryCode]
        df = df.sort_values(by="dateRep", ascending=False)
        df = df.head(5)
        df = df.to_dict(orient="records")

        return {"status": "success", 
                "message": {"endpoint" :  "rolling-five-days", "description" : "Last five days of data per Territory"}, 
                "timestamp": pd.Timestamp.now(), "data": df
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}. Please select Territory from the list: {(valid_country_territory_Code)}")
    

@app.get("/total-cases/")
async def total_cases():
    try:
        df = read_and_process_data("downloaded_data.json")
        #grouping by countryterritoryCode and summing the cases
        df = df.groupby("countryterritoryCode").sum("cases")
        #remove countryterritoryCode from index and select only the cases and countryterritoryCode column
        df = df.reset_index()[[ "countryterritoryCode", "cases"]]
        df = df.to_dict(orient="records")
        # return data in application-json format with status, message,timestamp,data
        return {"status": "success",
                "message": {"endpoint" :  "total-cases", "description" : "total cases per Territory"},
                "timestamp": pd.Timestamp.now(), "data": df}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}") 
    



