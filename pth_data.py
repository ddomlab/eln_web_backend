import os
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
