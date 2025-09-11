import os
import sys
import requests
import json

API_KEY = os.getenv("CONFORMITY_API_KEY")
TEMPLATE_FILE = sys.argv[1] if len(sys.argv) > 1 else "template.yaml"

with open(TEMPLATE_FILE, "r") as f:
    template_body = f.read()

url = "https://us-east-1-api.cloudconformity.com/v1/template-scanner/scan"


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

    # Fail pipeline if critical/high issues exist
    issues = results.get("issues", [])
    critical_or_high = [i for i in issues if i["riskLevel"].lower() in ["very-high", "high"]]

    if critical_or_high:
        print("❌ Critical/High issues found:")
        for issue in critical_or_high:
            print(f"- {issue['rule']['title']} (Risk: {issue['riskLevel']})")
        sys.exit(1)
    else:
        print("🎉 No critical/high issues found.")
else:
    print("❌ Scan failed:", response.status_code, response.text)
    sys.exit(1)
