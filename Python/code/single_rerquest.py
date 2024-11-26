import requests
import json

GRAPHQL_ENDPOINT = "https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql"  

query = """
query {
  cmr(id: 724) {
    id
    name
    cas_number
    ec_number
    component_id
    component {
      id
    }
    created_at
    updated_at
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Authorization": "3ece09ac19cbd5a9cf31f06920ecfd79e483dea77bce7a794c3fd501f13a90b7",  # Replace with your access token if needed
}

def run_graphql_query(endpoint, query, headers=None):
    payload = {
        "query": query
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()  
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

response = run_graphql_query(GRAPHQL_ENDPOINT, query, headers)

if response:
    print(json.dumps(response, indent=2))
else:
    print("Failed to fetch data from the GraphQL API.")
