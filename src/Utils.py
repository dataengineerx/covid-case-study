import pandas as pd 

def read_and_process_data(source_file:str) -> pd.DataFrame:
    """
    This function reads the json file and returns a pandas dataframe
    """
    try:
        df = pd.read_json(source_file)
        #flattening the data from records column into sub columns 
        df = pd.json_normalize(df["records"])
        #filter cases column with value greater than 0 
        df = df[df["cases"] > 0]
        #cast cases column to int
        df["cases"] = df["cases"].astype(int)
        #cast dateRep column to datetime
        df["dateRep"] = pd.to_datetime(df["dateRep"],dayfirst=True)
        return df
    except Exception as e:
        raise Exception(f"Error processing data: {str(e)}")
