from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.orm import sessionmaker
import pandas as pd
from requests import Session
from typing import List

app = FastAPI()

# SQLite database setup
DATABASE_URL = "sqlite:///./covid_database.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define a table structure
covid_table = Table(
    "covid_data",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("date", String),
    Column("country", String),
    Column("cases", Integer),
)

# Create the table
metadata.create_all(engine)

# Load the dataset from CSV
dataset_path = "/home/cyborg15/projects/covid-case-study/data/downloaded_data.csv"
df = pd.read_csv(dataset_path)

# Insert data into the SQLite database
df.to_sql("covid_data", con=engine, if_exists="replace", index=False)

# Create a session to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/rolling-five-days/{country_code}')
def rolling_five_days(country_code: str, db: Session = Depends(get_db)):
    # Implement logic to retrieve the past 5 days of data for the specified country
    # For demonstration purposes, assuming the dataset has columns like 'date', 'cases', 'country'
    result = df[(df['country'] == country_code)].tail(5).to_dict(orient='records')
    
    # Store the result in the database (optional, based on your use case)
    db.execute(
        covid_table.insert().values(
            date=result[0]['date'],
            country=result[0]['country'],
            cases=result[0]['cases'],
        )
    )

    return result


@app.get('/total-data')
def total_data(db: Session = Depends(get_db)):
    # Implement logic to calculate the total number of cases for each country
    # For demonstration purposes, assuming the dataset has columns like 'cases', 'country'
    result = df.groupby('country')['cases'].sum().to_dict()

    # Store the result in the database (optional, based on your use case)
    for country, total_cases in result.items():
        db.execute(
            covid_table.insert().values(
                country=country,
                cases=total_cases,
            )
        )

    return result
