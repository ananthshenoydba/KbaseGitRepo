import requests
import csv
import json
import os
from datetime import datetime

class GraphQLClient:
    def __init__(self, url):
        """
        Initialize GraphQL client with endpoint URL
        
        Args:
        url (str): GraphQL endpoint URL
        """
        self.url = 'https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql'
        self.headers = {
            'Content-Type': 'application/json',
            "X_API_KEY": "3ece09ac19cbd5a9cf31f06920ecfd79e483dea77bce7a794c3fd501f13a90b7"
        }
    
    def execute_query(self, query, variables=None):
        """
        Execute a GraphQL query
        
        Args:
        query (str): GraphQL query string
        variables (dict, optional): Variables for the query
        
        Returns:
        dict: Response data
        """
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        response = requests.post(self.url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed with status code {response.status_code}")

def get_total_cmr_count(client):
    """
    Get total number of CMRs in the table
    
    Args:
    client (GraphQLClient): GraphQL client instance
    
    Returns:
    int: Total number of CMRs
    """
    query = '''
    query {
      total_cmr_count
    }
    '''
    
    result = client.execute_query(query)
    return result['data']['total_cmr_count']

def fetch_cmrs_data(client, total_count):
    """
    Fetch all CMRs using cursor-based pagination
    
    Args:
    client (GraphQLClient): GraphQL client instance
    total_count (int): Total number of CMRs
    
    Returns:
    list: List of all CMR dictionaries
    """
    query = '''
    query($first: Int!, $after: String) {
      cmrs(first: $first, after: $after) {
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
          endCursor
        }
      }
    }
    '''
    
    all_cmrs = []
    after_cursor = None
    page_size = 100  # Fetch 100 records at a time
    
    print(f"Total CMR count: {total_count}")
    print(f"Fetching CMRs in batches of {page_size}")
    
    while True:
        variables = {
            'first': page_size,
            'after': after_cursor
        }
        
        result = client.execute_query(query, variables)
        cmrs_page = result['data']['cmrs']
        
        # Extract nodes and add to all_cmrs
        page_cmrs = [edge['node'] for edge in cmrs_page['edges']]
        all_cmrs.extend(page_cmrs)
        
        # Print progress
        print(f"Fetched {len(all_cmrs)}/{total_count} CMRs")
        
        # Check if there are more pages
        if not cmrs_page['pageInfo']['hasNextPage']:
            break
        
        # Update cursor for next iteration
        after_cursor = cmrs_page['pageInfo']['endCursor']
    
    return all_cmrs

def write_to_csv(data, filename=None):
    """
    Write CMRs data to a CSV file
    
    Args:
    data (list): List of CMR dictionaries
    filename (str, optional): Output CSV filename
    """
    if not data:
        print("No data to write to CSV.")
        return

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cmrs_export_{timestamp}.csv"
    
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filename)
    
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        columns = [
            'id', 'name', 'cas_number', 'ec_number', 
            'component_id', 'created_at', 'updated_at'
        ]
        
        with open(full_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for row in data:
                writer.writerow(row)
        
        print(f"CSV file successfully written to: {full_path}")
        print(f"Total records written: {len(data)}")
        
        # Verify file exists and check its size
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"File size: {file_size} bytes")
        else:
            print("File was not created successfully.")
    
    except Exception as e:
        print(f"An error occurred while writing CSV: {e}")

def main():
    # Replace with your actual GraphQL endpoint
    url = 'YOUR_GRAPHQL_ENDPOINT_URL'
    
    try:
        # Initialize GraphQL client
        client = GraphQLClient(url)
        
        # Get total CMR count
        total_count = get_total_cmr_count(client)
        
        # Fetch all CMRs using pagination
        cmrs_data = fetch_cmrs_data(client, total_count)
        
        # Write to CSV
        write_to_csv(cmrs_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()