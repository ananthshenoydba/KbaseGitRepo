import requests
import csv
import json
import os
from datetime import datetime

def fetch_cmrs_data():
    """
    Fetch CMRs data using GraphQL query
    
    Returns:
    list: List of CMR dictionaries
    """
    url = 'https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql'
    
    query = '''
    query {
      cmrs(first: 10) {
        edges {
          node {
            id
            name
            cas_number
            ec_number
            component_id
            created_at
            updated_at
          }
          cursor
        }
        pageInfo {
          hasNextPage
          hasPreviousPage
          startCursor
          endCursor
        }
      }
    }
    '''
    
    headers = {
        'Content-Type': 'application/json',
        "X_API_KEY": "3ece09ac19cbd5a9cf31f06920ecfd79e483dea77bce7a794c3fd501f13a90b7"
    }
    
    response = requests.post(url, json={'query': query}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return [edge['node'] for edge in data['data']['cmrs']['edges']]
    else:
        raise Exception(f"Query failed with status code {response.status_code}")

def write_to_csv(data, filename=None):
    """
    Write CMRs data to a CSV file with detailed logging
    
    Args:
    data (list): List of CMR dictionaries
    filename (str, optional): Output CSV filename. Defaults to timestamped filename.
    """
    if not data:
        print("No data to write to CSV.")
        return

    if not filename:
        # Create a filename with current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cmrs_export_{timestamp}.csv"
    
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filename)
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Define the CSV columns based on the GraphQL query fields
        columns = [
            'id', 'name', 'cas_number', 'ec_number', 
            'component_id', 'created_at', 'updated_at'
        ]
        
        with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
            # Create a CSV writer object
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for row in data:
                writer.writerow(row)
        
        print(f"CSV file successfully written to: {full_path}")
        
        # Verify file exists and check its size
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"File size: {file_size} bytes")
        else:
            print("File was not created successfully.")
    
    except Exception as e:
        print(f"An error occurred while writing CSV: {e}")
        # Print current working directory and script directory for debugging
        print(f"Current Working Directory: {os.getcwd()}")
        print(f"Script Directory: {script_dir}")

def main():
    try:
        # Fetch CMRs data
        cmrs_data = fetch_cmrs_data()
        
        # Verify data
        print(f"Number of records retrieved: {len(cmrs_data)}")
        
        # Write to CSV
        write_to_csv(cmrs_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()