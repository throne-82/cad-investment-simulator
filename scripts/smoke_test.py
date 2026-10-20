import json
import sys
from urllib.request import Request, urlopen

base_url = sys.argv[1].rstrip("/")

for path in ("/", "/api/health"):
    with urlopen(base_url + path, timeout=15) as response:
        assert response.status == 200

payload = {
    "initial_principal": 1000,
    "monthly_contribution": 100,
    "annual_rate": 0,
    "years": 2,
}

request = Request(
    base_url + "/api/simulate",
    data=json.dumps(payload).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urlopen(request, timeout=15) as response:
    result = json.load(response)

assert result["currency"] == "CAD"
assert result["total_contributions"] == "3400.00"
assert result["interest"] == "0.00"
assert result["final_balance"] == "3400.00"
assert len(result["annual_progression"]) == 2

print(f"Public smoke test passed: {base_url}")
