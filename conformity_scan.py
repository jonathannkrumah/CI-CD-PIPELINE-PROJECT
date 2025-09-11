#!/usr/bin/env python3
import os
import sys
import json
import requests
import yaml

# Read inputs
if len(sys.argv) != 2:
    print("Usage: python conformity_scan.py <template-file>")
    sys.exit(1)

template_file = sys.argv[1]

with open(template_file, "r") as f:
    template_contents = f.read()

# Environment variables (from GitHub secrets)
API_KEY = os.getenv("CONFORMITY_API_KEY")
REGION = os.getenv("CONFORMITY_REGION", "us-west-2")  # default to us-west-2

if not API_KEY:
    print("❌ Missing CONFORMITY_API_KEY in environment")
    sys.exit(1)

# API Endpoint
url = f"https://{REGION}-api.cloudconformity.com/v1/template-scanner/scan"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"ApiKey {API_KEY}",
}

payload = {
    "data": {
        "type": "template-scan",
        "attributes": {
            "type": "cloudformation-template",
            "contents": template_contents
        }
    }
}

print(f"🔎 Using Conformity API endpoint: {url}")

# Call API
response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code != 200:
    print(f"❌ Scan failed: {response.status_code} {response.text}")
    sys.exit(1)

data = response.json().get("data", [])

if not data:
    print("✅ No issues found in the template!")
    sys.exit(0)

# Parse results
failures = []
print("\n🔍 Scan Results:")
print("-" * 80)
for check in data:
    attributes = check.get("attributes", {})
    rule_title = attributes.get("rule-title", "Unknown Rule")
    risk = attributes.get("pretty-risk-level", "Unknown")
    status = attributes.get("status", "Unknown")
    message = attributes.get("message", "")
    resolution = attributes.get("resolution-page-url", "")

    print(f"{'❌' if status == 'FAILURE' else '✅'} {rule_title}")
    print(f"   - Risk: {risk}")
    print(f"   - Message: {message}")
    if resolution:
        print(f"   - Fix: {resolution}")
    print("")

    # Fail pipeline if risk level is High/Very High
    if status == "FAILURE" and risk in ["High", "Very High"]:
        failures.append(rule_title)

print("-" * 80)

if failures:
    print(f"❌ Build failed due to high-risk issues: {', '.join(failures)}")
    sys.exit(1)
else:
    print("✅ No High/Very High risk issues found")
    sys.exit(0)
