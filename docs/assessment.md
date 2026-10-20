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

The assessment budget is CAD 10. The required public availability end time is pending
candidate confirmation. Promotional credit reportedly expires on 2026-11-17; it does not
replace a retail cost estimate. Do not tear down until evaluator access is no longer required.

## Initial observations

- Repository started with only README.md at commit 658120e, on a clean main branch.
- No applicable AGENTS.md was present.
- Local Python 3.13.0, Terraform 1.6.5 (darwin_arm64), Azure CLI 2.91.0 and Docker were available.
- Azure subscription 1 was selected and Enabled. Local identity permissions include resource
  creation and RBAC assignment. No credentials were printed.
- GitHub CLI authentication was established; repository write and Project #2 read access verified.
- Canada Central is advertised for Container Apps. Microsoft.App initially required registration;
  initial regional quota returned zero environments. Recheck before provisioning hosting.

## Development workflow

Use short feature branches, meaningful incremental commits and PRs into main. Run CI on PRs;
only main may deploy through OIDC. Never commit Terraform state, plans or local credentials.
