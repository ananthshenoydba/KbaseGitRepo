import os
import json
import pandas as pd

def flatten_json(json_data, parent_key='', sep='_'):
    flattened = {}
    for key, value in json_data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            flattened.update(flatten_json(value, new_key, sep=sep))
        else:
            flattened[new_key] = value
    return flattened

def json_to_csv(json_path, csv_path):
    with open(json_path, 'r') as json_file:
        json_data = json.load(json_file)
    
    flattened_data = flatten_json(json_data)
    df = pd.DataFrame([flattened_data])
    df.to_csv(csv_path, index=False)

def convert_json_files_to_csv_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_path = os.path.join(root, file)
                csv_path = os.path.splitext(json_path)[0] + '.csv'

                json_to_csv(json_path, csv_path)
                print(f"Converted {file} to {csv_path}")

# Replace 'your_directory_path' with the path to your root directory containing JSON files
root_directory_path = 'C:/Ananth_personal/Ananth_personal/data-engineering-practice/Exercises/Exercise-4/data'
convert_json_files_to_csv_in_directory(root_directory_path)