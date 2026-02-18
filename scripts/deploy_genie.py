import os, requests, json

SPACE_ID = "01f107d4952d17669242a64d98ef35dd" 
HOST = "https://dbc-bdfbc88e-5cf4.cloud.databricks.com"
TOKEN = os.getenv('DATABRICKS_TOKEN')
PROD_WH_ID = "2b8d2aaac020286b"

headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def deploy():
    # 1. Load the JSON exported from your Notebook
    with open('spaces/genie_space.json', 'r') as f:
        master_config = json.load(f)

    # 2. Construct the payload exactly as per Databricks documentation
    # Note: 'serialized_space' must be a JSON-encoded string
    payload = {
        "title": master_config.get("title") + f"_from_ci_cd",
        "description": master_config.get("description"),
        "warehouse_id": PROD_WH_ID,
        "serialized_space": json.dumps(master_config.get("serialized_space"))
    }

    # 3. Check for existing space to decide between Create (POST) or Update (PUT)
    # The GET response also uses 'title'
    all_spaces = requests.get(f"{HOST}/api/2.0/genie/spaces", headers=headers).json().get('spaces', [])
    existing = next((s for s in all_spaces if s.get('title') == payload['title']), None)

    print(f"existing: {existing}")

    if existing:
        space_id = existing['space_id']
        print(f"Updating existing Space: {space_id}")
        url = f"{HOST}/api/2.0/genie/spaces/{space_id}"
        # Update API uses the same payload structure
        response = requests.patch(url, headers=headers, json=payload)
    else:
        print("Creating New Space in Production...")
        url = f"{HOST}/api/2.0/genie/spaces"
        # Create API uses the parameters you identified
        response = requests.post(url, headers=headers, json=payload)

    # Log the result
    if response.status_code in [200, 201]:
        print(f"Deployment Successful! Status Code: {response.status_code}")
    else:
        print(f"Deployment Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    deploy()