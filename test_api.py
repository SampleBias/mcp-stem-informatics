#!/usr/bin/env python3
import requests
import json

# Try a simple API request
base_url = "https://api.stemformatics.org"

# Try various endpoints to see which ones work
endpoints = [
    "/datasets/2000/metadata",
    "/search/datasets",
    "/search/datasets?query_string=*",
    "/search/samples?limit=5"
]

print("Testing Stemformatics API connectivity...")
for endpoint in endpoints:
    try:
        url = f"{base_url}{endpoint}"
        print(f"\nTrying: {url}")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"SUCCESS: Status code {response.status_code}")
            # Print a small preview of the response
            if response.headers.get('content-type') == 'application/json':
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"First item preview: {json.dumps(data[0], indent=2)[:500]}...")
                else:
                    print(f"Response preview: {json.dumps(data, indent=2)[:500]}...")
            else:
                print(f"Response type: {response.headers.get('content-type')}")
                print(f"Response preview: {response.text[:200]}...")
        else:
            print(f"ERROR: Status code {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")

print("\nAPI testing complete.") 