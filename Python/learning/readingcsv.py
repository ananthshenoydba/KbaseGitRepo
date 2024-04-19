import os
import pandas as pd


folder_path = '/app'  # Replace with the actual folder path
column_name = 'HourlyDryBulbTemperature'  # Replace with the name of the column you want to find the maximum value from

max_value = float('-inf')

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path, low_memory=False)
        if column_name in df.columns:
            column_values = df[column_name].apply(pd.to_numeric, downcast='integer', errors='coerce').dropna().values
            #print(column_values)
            max_value = max(column_values)
            print(f"The maximum value from column '{column_name}' in file '{filename}' is: {max_value}")