# Deployment and operations

## Architecture and ownership

The browser reaches the public Nginx frontend through platform HTTPS. Nginx serves
static files and forwards `/api/*` to the backend's internal HTTPS FQDN in the same
Container Apps environment. Platform-managed networking avoids a custom VNet for
this assessment. Ingress terminates TLS before the container's HTTP listener.
Nginx verifies the upstream certificate and allows a verification depth of three
for Azure's intermediate certificate chain. Certificate verification stays enabled.

Terraform owns resources, identities, federation, RBAC and deployed image digests.
GitHub Actions builds and pushes images; it does not independently update Container
App images. Single-revision mode sends traffic to the latest ready revision.
Canada Central, Consumption, 0.25 vCPU and 0.5 GiB per replica are used. The frontend
has min 1/max 2; the backend min 1/max 4, with HTTP concurrency target 2 for the demo.
The target is an autoscaling signal, not an admission limit or production sizing.

## Prerequisites and local verification

Use Python 3.13, Docker Compose, Terraform 1.6.5 and an authenticated Azure CLI.
The provider lock files pin AzureRM 4.81.0. The deployment builds `linux/amd64`
images explicitly because local development uses Apple Silicon.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements-dev.txt
python -m ruff check backend scripts
PYTHONPATH=backend python -m pytest backend/tests -q
python -m pip_audit -r backend/requirements.txt --no-deps --disable-pip
docker compose config --quiet
docker compose up --build -d --wait
python scripts/smoke_test.py http://127.0.0.1:8080
terraform fmt -check -recursive infra
terraform -chdir=infra/bootstrap init -backend=false -input=false
terraform -chdir=infra/bootstrap validate
terraform -chdir=infra/application init -backend=false -input=false
terraform -chdir=infra/application validate
```

Use backend-free init only in a clean validation directory; an existing local
Terraform directory may remember its remote backend. It is not a deployment step.

## First bootstrap on a new subscription

1. Run `az login`, select the intended subscription with `az account set`, and
   verify it with `az account show --query '{name:name,state:state}'`. Set
   `export ARM_SUBSCRIPTION_ID="$(az account show --query id -o tsv)"` for AzureRM 4.
   Do not print tokens.
2. Register Microsoft.App, Microsoft.ContainerRegistry, Microsoft.OperationalInsights,
   Microsoft.ManagedIdentity and Microsoft.Storage, then verify regional quota.
   Provider auto-registration is disabled deliberately; registration requires the local identity.
3. Protect local state: `umask 077; mkdir -p .local/bootstrap; chmod 700 .local`.
   Before the **first** bootstrap, temporarily replace the backend block in
   `infra/bootstrap/backend.tf` with the following local backend. Never do this
   against an existing remote deployment without an intentional state migration.

   ```hcl
   terraform {
     backend "local" {
       path = "../../.local/bootstrap/terraform.tfstate"
     }
   }
   ```

4. Review the federated subject in `infra/bootstrap/identity.tf` for the actual
   repository. This repository uses the immutable owner/repository ID form:
   `repo:throne-82@91632987/cad-investment-simulator@1425861975:ref:refs/heads/main`.
   A fork must use its own subject; substituting a repository name alone is insufficient.
5. Run `terraform -chdir=infra/bootstrap init`, `plan -out=../../.local/bootstrap.tfplan`,
   review the plan, then `apply ../../.local/bootstrap.tfplan`. Bootstrap creates
   resource groups, state storage, ACR, identities and role assignments before any apps.
6. Save `terraform -chdir=infra/bootstrap output -json configuration > .local/azure.json`.
   These identifiers are configuration, not an Azure password. Keep local files ignored.
7. Create `.local/bootstrap.backend.hcl` using the output's state resource group
   and storage account, `container_name = "bootstrap"`, `key = "bootstrap.tfstate"`
   and `use_azuread_auth = true`. Restore the committed `azurerm` backend block.
   Run `terraform -chdir=infra/bootstrap init -migrate-state
   -backend-config=../../.local/bootstrap.backend.hcl` and confirm migration.
   Verify `terraform -chdir=infra/bootstrap state list` and the Blob before removing
   any protected local backup. Never commit state or a saved plan.
8. A local application backend config uses the same resource group/storage settings
   but `container_name = "application"` and `key = "application.tfstate"`.
   Configure GitHub repository variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`,
   `AZURE_SUBSCRIPTION_ID` and `AZURE_CONFIG` (the JSON configuration output).
   Use `gh variable set AZURE_CONFIG < .local/azure.json` for the JSON value.
   No client secret or ACR admin password is required.
9. Merge a reviewed feature PR into main. Actions authenticates, builds and pushes
   both real images, resolves their immutable digests, then applies application
   Terraform and verifies the public URL. No placeholder images or target applies
   are needed. Bootstrap and application use separate containers/state keys.

The first bootstrap requires an identity allowed to create RBAC assignments.
Contributor cannot grant roles. Routine CI never applies the privileged bootstrap.

## Authentication and authorization

GitHub's job requests a short-lived OIDC assertion with `id-token: write`.
Azure trusts only the configured issuer, audience and exact main subject, then
issues a short-lived Azure credential for the deployment managed identity.
PR jobs have no deployment OIDC permission. No long-lived Azure secret is stored.
The deployment workflow also checks `github.ref == 'refs/heads/main'`.

| Identity | Role | Scope |
| --- | --- | --- |
| Deployment identity | Contributor | Application resource group |
| Deployment identity | AcrPush | One registry |
| Deployment identity | Storage Blob Data Contributor | Application state container |
| Image-pull identity | AcrPull | One registry |
| Local bootstrap user | Storage Blob Data Contributor | State storage account |

Container Apps uses the pull identity to obtain images from private ACR.
This identity does not authenticate public application users, encrypt application
traffic by itself, or provide authorization between internal services. Internal
ingress reduces exposure to the environment; the calculator intentionally has no
user account system or persistence. See the [OIDC subject change announcement](https://github.blog/changelog/2026-04-23-immutable-subject-claims-for-GitHub-actions-oidc-tokens/).

State uses Entra data-plane authentication, HTTPS, private containers, disabled
shared keys, versioning and seven-day deletion retention. The storage endpoint
is publicly reachable with authorization; it is not a private-endpoint design.
Blob state locking and workflow concurrency serialize routine deployment.

## Logs and metrics

The backend logs JSON containing route, status, elapsed milliseconds and correlation
ID. It does not log request bodies, credentials or authorization headers. Nginx
passes a generated request ID; the backend returns `X-Request-ID` for investigation.
Health requests skip custom JSON logging, although server access logs still exist.
Log Analytics retention is 30 days with a modest 0.1 GB daily ingestion quota.
The quota can interrupt observability and is not a hard spending cap.

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "cad-backend"
| extend entry = parse_json(Log_s)
| where tostring(entry.event) == "http_request"
| extend status = toint(entry.status), duration_ms = todouble(entry.duration_ms)
| summarize requests=count(), errors=countif(status >= 500),
    p95_ms=percentile(duration_ms, 95) by bin(TimeGenerated, 1m)
```

For one failed request, filter `tostring(entry.request_id)` to the response header
value and correlate with `ContainerAppSystemLogs_CL` and revision/probe events.
Use Azure Monitor `Replicas`, `Requests`, `UsageNanoCores` and `WorkingSetBytes`
metrics with one-minute intervals. Backend log duration excludes client/network
time; it should not be confused with k6 end-to-end latency.

## Reproduce the load test

```sh
mkdir -p .local/load
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$PWD/load:/scripts:ro" -v "$PWD/.local/load:/results" \
  -e BASE_URL=https://cad-frontend.greenmushroom-f0d12a6f.canadacentral.azurecontainerapps.io \
  grafana/k6:2.3.0 run --summary-export=/results/summary.json /scripts/simulation.js
```

The 5m30s closed-loop test has baseline, ramp, sustained and recovery stages, up to
100 VUs, using varied valid inputs through the public Nginx API path. Thresholds
were set beforehand: errors below 1%, p95 below 500 ms, checks above 99%. No
artificial delays were added. Sample both apps' replica counts every 15–20 seconds
with `az containerapp replica list`, continue through cooldown, and record the
actual maximum and return to baseline. Closed-loop VUs do not guarantee a fixed
arrival rate; the client, frontend, networking and backend can each limit throughput.

## Recovery and rollback

For local failure verification, stop only the backend with `docker compose stop
backend`, check that the frontend still serves `/` and `/api/simulate` fails,
then run `docker compose up -d --wait backend` and repeat the smoke test.
An HTTP 502 or 504 from the proxy can occur during backend unavailability. The browser
handles a failed fetch with a controlled message. Do not stop the public demo to
reproduce this test during evaluator access.

To roll back application code, revert the faulty commit through a short PR to main;
CI tests it and deploys images built from the known-good code. For an exact image
rollback, obtain both previous `@sha256` references from a successful deployment,
place them in `.local/application.tfvars.json` with the bootstrap `config`, initialize
the application backend with `.local/application.backend.hcl`, then run:

```sh
terraform -chdir=infra/application plan -var-file=../../.local/application.tfvars.json -out=../../.local/rollback.tfplan
terraform -chdir=infra/application apply ../../.local/rollback.tfplan
python scripts/smoke_test.py https://cad-frontend.greenmushroom-f0d12a6f.canadacentral.azurecontainerapps.io
```

Use local Azure authentication for this manual procedure. Reconcile main through
a revert PR so the next automatic deployment does not restore bad code. Avoid
`az containerapp update --image`, which would change Terraform-owned configuration.
The exact-digest rollback procedure is documented; it was not exercised during the assessment.

## Teardown after evaluator access

Do not run these steps until the evaluator no longer needs the URL. Preserve code,
the selected image identifiers and sanitized evidence first. Cancel/disable deploys
so a new push cannot race cleanup. Using the local Azure identity:

1. Initialize application remote state and supply the current application tfvars.
   Run `terraform -chdir=infra/application plan -destroy
   -var-file=../../.local/application.tfvars.json -out=../../.local/destroy-app.tfplan`,
   review, then `apply ../../.local/destroy-app.tfplan`.
2. Back up bootstrap state to protected local storage with `terraform state pull`.
   Migrate its backend to the protected local path above using `init -migrate-state`
   **before deleting the storage that contains its remote state**.
3. Remove `prevent_destroy` from the storage resource only as an intentional cleanup
   change. Review a bootstrap destroy plan and apply it with the privileged local
   identity. This removes ACR, identities, federation, RBAC, state storage and groups.
4. Verify both resource groups are absent and review Cost Management for remaining
   charges. Delete protected local state/backups only when no longer required.

Keep the repository and committed evidence. Never delete the resource group first
and leave Terraform unable to read its state.
