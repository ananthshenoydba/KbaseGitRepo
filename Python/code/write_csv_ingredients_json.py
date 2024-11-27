import requests
import json
import os
import math
from datetime import datetime

class GraphQLClient:
    def __init__(self, url, token=None):
        """
        Initialize GraphQL client with endpoint URL and optional authentication
        
        Args:
        url (str): GraphQL endpoint URL
        token (str, optional): Authentication token
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

def initialize_progress_file(total_count, filename='ingredients_progress.json'):
    """
    Initialize a progress file for the first run
    
    Args:
    total_count (int): Total number of ingredients
    filename (str): Filename to save initial progress
    """
    initial_progress = {
        'data': [],
        'total_count': total_count,
        'last_cursor': None,
        'last_page': -1,
        'timestamp': datetime.now().isoformat(),
        'current_records': 0
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(initial_progress, f, indent=2, ensure_ascii=False)
        
        print(f"Initialized progress file for {total_count} ingredients")
    except Exception as e:
        print(f"Error initializing progress file: {e}")

def cleanup_progress_file(filename='ingredients_progress.json'):
    """
    Remove the progress file after successful completion
    
    Args:
    filename (str): Filename of the progress file
    """
    try:
        os.remove(filename)
        print("Progress file cleaned up successfully")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error cleaning up progress file: {e}")

def save_progress(data, total_count, last_cursor, last_page, filename='ingredients_progress.json'):
    """
    Save the current progress to a JSON file
    
    Args:
    data (list): List of already fetched ingredients
    total_count (int): Total number of ingredients
    last_cursor (str): Last processed cursor
    last_page (int): Last processed page
    filename (str): Filename to save progress
    """
    progress = {
        'data': data,
        'total_count': total_count,
        'last_cursor': last_cursor,
        'last_page': last_page,
        'timestamp': datetime.now().isoformat(),
        'current_records': len(data)
    }
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
        
        print(f"Progress saved. Records: {len(data)}/{total_count}, Last Page: {last_page}, Last Cursor: {last_cursor}")
    except Exception as e:
        print(f"Error saving progress: {e}")

def load_progress(total_count, filename='ingredients_progress.json'):
    """
    Load previously saved progress from JSON file
    
    Args:
    total_count (int): Total number of ingredients for validation
    filename (str): Filename to load progress from
    
    Returns:
    tuple: (previously fetched data, total count, last cursor, last page)
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            progress = json.load(f)
        
        # Validate total count
        if progress.get('total_count') != total_count:
            print("Total ingredient count mismatch. Reinitializing progress.")
            initialize_progress_file(total_count, filename)
            return [], total_count, None, -1
        
        # Defensive parsing with fallback values
        data = progress.get('data', [])
        last_cursor = progress.get('last_cursor')
        last_page = progress.get('last_page', -1)
        timestamp = progress.get('timestamp', 'N/A')
        
        print("Previous progress found:")
        print(f"Timestamp: {timestamp}")
        print(f"Saved Records: {len(data)}/{total_count}")
        print(f"Last Page: {last_page}")
        print(f"Last Cursor: {last_cursor}")
        
        return data, total_count, last_cursor, last_page
    
    except (FileNotFoundError, json.JSONDecodeError):
        # If no progress file exists or it's invalid, initialize it
        print("No valid progress file found. Initializing progress.")
        initialize_progress_file(total_count, filename)
        return [], total_count, None, -1

def fetch_ingredients_data(client, total_count):
    """
    Fetch ingredients using cursor-based pagination with resume capability
    
    Args:
    client (GraphQLClient): GraphQL client instance
    total_count (int): Total number of ingredients
    
    Returns:
    list: List of ingredient dictionaries
    """
    # Load or initialize progress
    all_ingredients, total_count, after_cursor, start_page = load_progress(total_count)
    
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
    
    page_size = 100  # Fetch 100 records at a time
    num_pages = math.ceil(total_count / page_size)
    
    print(f"Total ingredients count: {total_count}")
    print(f"Fetching ingredients in batches of {page_size}")
    print(f"Total pages: {num_pages}")
    print(f"Starting from page: {start_page + 1}")
    
    try:
        for page in range(start_page + 1, num_pages):
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
            
            # Save progress periodically
            if len(all_ingredients) % 1000 == 0:
                save_progress(
                    all_ingredients, 
                    total_count, 
                    ingredients_page['pageInfo']['endCursor'], 
                    page
                )
            
            # Update cursor for next iteration
            if ingredients_page['pageInfo']['hasNextPage']:
                after_cursor = ingredients_page['pageInfo']['endCursor']
            else:
                break
        
        # Final progress save
        save_progress(
            all_ingredients, 
            total_count, 
            after_cursor, 
            page
        )
        
        # Ensure we don't exceed the total count
        all_ingredients = all_ingredients[:total_count]
        
        print(f"Final ingredients count: {len(all_ingredients)}")
    
    except Exception as e:
        # Save progress in case of any error
        save_progress(
            all_ingredients, 
            total_count, 
            after_cursor, 
            page
        )
        raise
    
    return all_ingredients

def get_total_ingredients_count(client):
    """
    Get total number of ingredients in the table
    
    Args:
    client (GraphQLClient): GraphQL client instance
    
    Returns:
    int: Total number of ingredients
    """
    query = '''
    query {
      total_ingredients_count
    }
    '''
    
    result = client.execute_query(query)
    total_count = result['data']['total_ingredients_count']
    
    # Explicitly print the total count
    print(f"Total ingredients count retrieved: {total_count}")
    
    return total_count

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

def main():
    # Replace with your actual GraphQL endpoint
    url = 'https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql'
    
    try:
        # Initialize GraphQL client
        client = GraphQLClient(url)
        
        # Get total ingredients count
        total_count = get_total_ingredients_count(client)
        
        # Fetch ingredients with resume capability
        ingredients_data = fetch_ingredients_data(client, total_count)
        
        # Write to JSONLines
        write_to_jsonlines(ingredients_data)
        
        # Cleanup progress file after successful completion
        cleanup_progress_file()
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()