import requests
import json

# GraphQL endpoint URL
url = "https://staging-submit.cosmetic-product-notifications.service.gov.uk/graphql"

# GraphQL query
query = """
query {
total_cmr_count
total_notification_count
total_component_nano_materials_count
total_components_count
total_contact_persons_count
total_deleted_notifications_count
total_image_uploads_count
total_ingredients_count
total_nano_materials_count
total_nanomaterial_notifications_count
total_notification_delete_logs_count
total_pending_responsible_person_users_count
total_responsible_person_address_logs_count
total_responsible_persons_count
total_responsible_person_users_count
total_search_histories_count
total_trigger_question_elements_count
total_trigger_questions_count
total_users_count
}
"""

# Authentication headers
headers = {
    "Content-Type": "application/json",
    "X_API_KEY": "3ece09ac19cbd5a9cf31f06920ecfd79e483dea77bce7a794c3fd501f13a90b7"
}

# Execute the GraphQL query
response = requests.post(url, json={"query": query}, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Get the data from the response
    data = response.json()["data"]
    
    # Print the results
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {response.status_code} - {response.text}")