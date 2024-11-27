import requests
import csv

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

url = "https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql"  
headers = {
    "Content-Type": "application/json",
    "X_API_KEY": "3ece09ac19cbd5a9cf31f06920ecfd79e483dea77bce7a794c3fd501f13a90b7"
}

response = requests.post(url, json={'query': query}, headers=headers)

if response.status_code == 200:
    data = response.json()
    cmrs = data.get("data", {}).get("cmrs", {}).get("edges", [])

    rows = []
    for item in cmrs:
        node = item.get("node", {})
        rows.append([
            node.get("id"),
            node.get("name"),
            node.get("cas_number"),
            node.get("ec_number"),
            node.get("component_id"),
            node.get("created_at"),
            node.get("updated_at"),
        ])
    
    # Write to a CSV file
    with open("cmrs_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(["ID", "Name", "CAS Number", "EC Number", "Component ID", "Created At", "Updated At"])
        # Write the data rows
        writer.writerows(rows)
    
    print("Data written to cmrs_data.csv successfully.")
else:
    print(f"Failed to fetch data: {response.status_code}, {response.text}")