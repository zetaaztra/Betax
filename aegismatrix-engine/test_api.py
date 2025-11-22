"""Test direct Yahoo Finance API connectivity"""
import urllib.request
import json

print("=== Direct Yahoo Finance API Test ===")
try:
    url = "https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1d&range=1mo"
    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read())
        if "chart" in data and "result" in data["chart"] and len(data["chart"]["result"]) > 0:
            result = data["chart"]["result"][0]
            print(f"✓ SUCCESS - Got data")
            print(f"  Timestamps: {len(result.get('timestamp', []))} rows")
        else:
            print("✗ Empty response")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {str(e)[:100]}")
