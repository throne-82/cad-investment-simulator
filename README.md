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
