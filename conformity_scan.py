import os
import sys
import requests
import json

API_KEY = os.getenv("CONFORMITY_API_KEY")
TEMPLATE_FILE = sys.argv[1]

with open(TEMPLATE_FILE, "r") as f:
    template_body = f.read()

url = "https://conformity.trendmicro.com/api/template-scanner/scan"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"ApiKey {API_KEY}"
}

payload = {
    "type": "cloudformation-template",
    "contents": template_body
}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    results = response.json()
    with open("conformity_results.json", "w") as out:
        json.dump(results, out, indent=2)
    print("✅ Scan completed. Results saved to conformity_results.json")
else:
    print("❌ Scan failed:", response.status_code, response.text)
    sys.exit(1)
