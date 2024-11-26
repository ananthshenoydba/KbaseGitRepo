import requests
import json
import os
from datetime import datetime
import math

class GraphQLClient:
    def __init__(self, url):

        self.url = 'https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql'
        self.headers = {
            'Content-Type': 'application/json',
            "X_API_KEY": "3ece09ac19cbd5a9cf31f06920ecfd79e483dea77bce7a794c3fd501f13a90b7"
        }
    
    def execute_query(self, query, variables=None):
    
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        response = requests.post(self.url, json=payload, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Query failed with status code {response.status_code}")

def write_to_jsonlines(data, filename=None):
    
    if not data:
        print("No data to write to JSONLines file.")
        return

    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ingredients_export_{timestamp}.jsonl"
    
    # Get the absolute path of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, filename)
    
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as jsonl_file:
            for ingredient in data:
                # Write each ingredient as a separate JSON line
                json.dump(ingredient, jsonl_file, ensure_ascii=False)
                jsonl_file.write('\n')
        
        print(f"JSONLines file successfully written to: {full_path}")
        print(f"Total records written: {len(data)}")
        
        # Verify file exists and check its size
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"File size: {file_size} bytes")
        else:
            print("File was not created successfully.")
    
    except Exception as e:
        print(f"An error occurred while writing JSONLines file: {e}")

def fetch_ingredients_data(client, total_count):

    query = '''
    query($first: Int!, $after: String) {
      ingredients(first: $first, after: $after) {
        edges {
          node {
            id
            component_id
            inci_name
            cas_number
            exact_concentration
            range_concentration
            poisonous
            used_for_multiple_shades
            minimum_concentration
            maximum_concentration
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
    
    all_ingredients = []
    after_cursor = None
    page_size = 1000  # Fetch 100 records at a time
    
    # Calculate the number of pages needed
    num_pages = math.ceil(total_count / page_size)
    
    print(f"Total ingredients count: {total_count}")
    print(f"Fetching ingredients in batches of {page_size}")
    print(f"Total pages: {num_pages}")
    
    try:
        for page in range(num_pages):
            variables = {
                'first': page_size,
                'after': after_cursor
            }
            
            result = client.execute_query(query, variables)
            ingredients_page = result['data']['ingredients']
            
            # Extract nodes and add to all_ingredients
            page_ingredients = [edge['node'] for edge in ingredients_page['edges']]
            all_ingredients.extend(page_ingredients)
            
            # Print progress
            print(f"Fetched {len(all_ingredients)}/{total_count} ingredients")
            
            # Update cursor for next iteration
            if ingredients_page['pageInfo']['hasNextPage']:
                after_cursor = ingredients_page['pageInfo']['endCursor']
            else:
                break
        
        # Ensure we don't exceed the total count
        all_ingredients = all_ingredients[:total_count]
        
        print(f"Final ingredients count: {len(all_ingredients)}")
    
    except Exception as e:
        print(f"An error occurred during fetching: {e}")
        raise
    
    return all_ingredients

def get_total_ingredients_count(client):

    query = '''
    query {
      total_ingredients_count
    }
    '''
    
    result = client.execute_query(query)
    return result['data']['total_ingredients_count']

def main():
    url = 'https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql'
    
    try:
        client = GraphQLClient(url)
        
        total_count = get_total_ingredients_count(client)
        
        ingredients_data = fetch_ingredients_data(client, total_count)
        
        write_to_jsonlines(ingredients_data)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()