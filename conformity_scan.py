import os
import sys
import json
import requests
import yaml

# Load environment variables
api_key = os.getenv("CONFORMITY_API_KEY")
region = os.getenv("CONFORMITY_REGION", "us-west-2")

if not api_key:
    print("❌ Missing CONFORMITY_API_KEY in environment")
    sys.exit(1)

# API endpoint
url = f"https://{region}-api.cloudconformity.com/v1/template-scanner/scan"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"ApiKey {api_key}"
}

# Get template path from CLI
if len(sys.argv) < 2:
    print("❌ Usage: python conformity_scan.py <template.yaml>")
    sys.exit(1)

template_file = sys.argv[1]

try:
    with open(template_file, "r") as f:
        template_contents = f.read()
except Exception as e:
    print(f"❌ Failed to read template: {e}")
    sys.exit(1)

# Build payload
payload = {
    "data": {
        "type": "template-scan",
        "attributes": {
            "type": "cloudformation-template",
            "contents": template_contents
        }
    }
}

# Send request
print(f"🔎 Using Conformity API endpoint: {url}")
response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code != 200:
    print(f"❌ Scan failed: {response.status_code} {response.text}")
    sys.exit(1)

result = response.json()
print("✅ Scan completed successfully")

# Normalize result to always be a list
data = result.get("data", [])
if isinstance(data, dict):
    data = [data]  # wrap single object into a list

violations_found = False
for item in data:
    attrs = item.get("attributes", {})
    violations = attrs.get("violations", [])
    if violations:
        violations_found = True
        print("❌ Violations detected:")
        for v in violations:
            print(f"- {v}")

if violations_found:
    sys.exit(1)
else:
    print("✅ No violations found")
