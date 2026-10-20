# CAD Investment Simulator

A generic investment simulator in Canadian dollars, delivered as a static HTML/CSS/JavaScript
frontend served by Nginx and a Python/FastAPI calculation API.

Inputs are initial principal, monthly contribution, effective annual interest rate and duration
in years. Contributions occur at month end. The monthly equivalent rate is
`(1 + annual_rate) ** (1 / 12) - 1`. Results include contributions, interest, final balance and
annual progression. Taxes, inflation, mortgage rules and persisted history are outside the MVP.

## Architecture

```text
Browser --HTTPS--> public frontend (Nginx)
                         |
                         +-- /api/* --> internal backend (FastAPI)
                           one Azure Container Apps environment

GitHub Actions --OIDC/main--> Azure deployment identity
Terraform --> Azure resources and deployed image references
ACR Basic <--managed identity image pulls-- Container Apps
Azure Monitor / Log Analytics <-- application and platform logs
```

Bootstrap uses the local Azure identity. Bootstrap and application state are stored separately
in private Azure Blob containers with Entra authentication. Initial deployment proceeds through
base infrastructure, real image publication, then application deployment.

See [the assessment execution record](docs/assessment.md) for timing, scope and checkpoints.
Local execution, deployment and verification instructions are added alongside working features.


## Local development

Create a virtual environment with `python3 -m venv .venv` and activate it
with `source .venv/bin/activate`. Install development dependencies with
`python -m pip install -r backend/requirements-dev.txt`.

Run tests with `PYTHONPATH=backend python -m pytest backend/tests -q`.
Start both services with `docker compose up --build -d --wait`, then open
http://localhost:8080. Stop them with `docker compose down`.

## Calculation and validation

The API accepts an effective annual rate as a fraction: 0.05 means 5%.
Supported bounds are CAD 0–10,000,000 initial principal, CAD 0–100,000
monthly contribution, 0–100% annual rate, and 1–60 integer years.

Monthly interest is applied before each contribution. Calculations use
Decimal with 40-digit precision. Balances are not rounded monthly;
response amounts are strings rounded to cents using ROUND_HALF_UP.
Total contributions include the initial principal.

The backend rejects extra fields, incorrect types, non-finite numbers
and values outside the supported bounds.