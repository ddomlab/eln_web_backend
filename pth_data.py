import os
from datetime import datetime
import pandas as pd
import csv

def save_as_csv(path, data: dict) -> bool:
    """ Store data from http request as a csv file, adding rows if the file already exists."""
   # Create file with headers if it doesn't exist
    file_exists = os.path.isfile(path)
    with open(path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)
    return True
def get_csv_data(path:str) -> list[dict]:
    """ Read data from a csv file and return as a list of dictionaries."""
    if not os.path.isfile(path):
        return []
    with open(path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data
def get_closest_time(path:str, target_time: str | int) -> dict | None:
    """ Get the row from the csv file with the closest time to the target_time. """
    if not os.path.isfile(path):
        return None
    
    data = pd.DataFrame(get_csv_data(path)) # data['time'] is int, epoch time integer

    # if target_time is a string, convert it to epoch time integer
    if isinstance(target_time, str):
        target_time = int(datetime.fromisoformat(target_time).timestamp())
    
    # Find closest data['time'] value to target_time and return that row as a dictionary
    data['time'] = data['time'].astype(int)
    closest_index = (data['time'] - target_time).abs().idxmin()
    # idxmin() returns the index label; use .loc to select by label (handles int or str labels)
    return data.loc[closest_index].to_dict()
    