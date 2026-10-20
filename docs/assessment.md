# Assessment execution record

- Official start, reported by the candidate: 2026-10-19 20:50 America/Toronto (UTC-04:00).
- Delivery deadline: 2026-10-20 00:50 America/Toronto.
- Final verification, documentation and push window: 00:20-00:50.
- AI assistance is explicitly permitted. The candidate reviews and explains decisions.
- Implementation plan: GitHub issues #1-#13 and Project #2; all were read before implementation.
- Required delivery: issues #1-#12. Issue #13 is optional and outside the MVP critical path.

## Checkpoints

| Target (America/Toronto) | Checkpoint |
| --- | --- |
| 21:15 | Access checks, repository foundation and bootstrap design |
| 22:00 | Tested API, frontend and local container integration |
| 23:00 | Azure deployment through GitHub Actions OIDC |
| 00:20 | Security, recovery, observability and measured load evidence |
| 00:50 | Final documentation, public smoke test and push complete |

These are planning targets, not claims of completed work. Actual evidence is recorded as checks run.

## Scope and cost decisions

Generic CAD investment simulation; no taxes, inflation, mortgage conventions or database.
Use two images, Nginx and FastAPI, in one Azure Container Apps environment with
platform-managed networking. Prefer Canada Central, subject to actual quota and availability.
Start with Consumption replicas at 0.25 vCPU / 0.5 GiB and ACR Basic.

The initial assessment budget target was CAD 10. The candidate authorized keeping
the URL available and reported approximately CAD 280 in promotional credit, with
expiry on 2026-11-17. No finite availability end date was supplied. Credit does not
replace a retail estimate or guarantee indefinite hosting within CAD 10. See
[cost assumptions](costs.md); do not tear down while evaluator access is required.

## Initial observations

- Repository started with only README.md at commit 658120e, on a clean main branch.
- No applicable AGENTS.md was present.
- Local Python 3.13.0, Terraform 1.6.5 (darwin_arm64), Azure CLI 2.91.0 and Docker were available.
- Azure subscription 1 was selected and Enabled. Local identity permissions include resource
  creation and RBAC assignment. No credentials were printed.
- GitHub CLI authentication was established; repository write and Project #2 read access verified.
- Canada Central is advertised for Container Apps. Microsoft.App initially required registration;
  initial regional quota returned zero environments. Recheck before provisioning hosting.

## Actual delivery evidence

- The registration/quota prerequisite was resolved and the environment was deployed
  in Canada Central. Bootstrap was applied locally, then its protected local state
  was migrated to a separate Azure Blob backend.
- Local API, frontend and Docker integration were implemented progressively and
  merged through PRs. No develop branch or persisted history was added.
- Main deployments authenticate through OIDC and deploy real immutable image
  digests using application Terraform. Deploy run 39369337100 succeeded at about
  04:25 UTC, including the public smoke check.
- Two deployment failures led to concrete fixes: the exact immutable GitHub OIDC
  subject and Nginx upstream certificate verification depth. TLS verification was
  retained. Subsequent deployment succeeded.
- At 04:29–04:35 UTC, a real public k6 test issued 49,224 requests, observed backend
  scale-out from one to four and recorded p95 1,080.87 ms and three failed requests.
  The latency target failed and is reported honestly. A subsequent low-load check passed.
- Log Analytics ingestion, HTTP controls, scoped roles, image/dependency audits,
  non-root execution and local backend recovery were checked. Image vulnerabilities
  remain documented; the scan is not a claim of complete security.
- Final documentation and sanitized evidence are in [verification](verification.md)
  and [operations](operations.md). Optional issue #13 remains deferred.

## Development workflow

Use short feature branches, meaningful incremental commits and PRs into main. Run CI on PRs;
only main may deploy through OIDC. Never commit Terraform state, plans or local credentials.
