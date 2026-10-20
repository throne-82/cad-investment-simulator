# Five-minute evaluation walkthrough

1. Open the public URL from README. Show CAD 1,000 initial principal, CAD 100/month,
   zero annual interest and two years: contributions/final balance CAD 3,400,
   interest CAD 0, annual balances CAD 2,200 and CAD 3,400. Explain month-end
   contributions and the effective annual-to-monthly conversion. Show a nonzero
   rate and the annual table. The browser sends a fraction to the authoritative API.
2. Show the two Dockerfiles and Compose. Nginx serves static files and proxies
   `/api/*`; both containers run as non-root. Only the frontend publishes a local port.
3. Show the latest successful CI and Deploy Actions. PRs test; main builds separate
   amd64 images, pushes SHA tags, resolves digests and deploys through Terraform.
   There is no develop branch or manually maintained application image override.
4. Show bootstrap versus application Terraform, separate Blob state and the role
   table in operations.md. Explain exact main OIDC trust, short-lived credentials,
   Contributor versus RBAC assignment, and managed-identity ACR pulls.
5. Show a structured log in Log Analytics, the response correlation header, the
   k6 summary and the timestamped replica timeline. Explain what was actually
   observed, threshold outcomes and why four replicas do not imply four times
   the throughput. Show the local failure/recovery record and image scan findings.
6. Close with costs, open limitations and teardown order. History is intentionally
   deferred. Production work would include vulnerability remediation, pinned
   Action commit SHAs, branch protection, calibrated load/SLOs and cost notifications.

## Concise decision explanations

- FastAPI/Pydantic bounds inputs and computation; Decimal avoids repeated float
  rounding. Monetary outputs round once to cents and include the initial principal.
- Separate frontend/backend images allow independent deployment and scaling.
- Container Apps handles HTTPS, service discovery and replica management without
  requiring Kubernetes operations for this small service.
- The bootstrap identity performs privileged setup once. CI gets resource deployment,
  registry push and application-state permissions, not subscription-wide Owner.
- A low concurrency target demonstrates scaling for a fast endpoint; production
  sizing requires a representative workload and measurements.
- No database avoids an unnecessary cost and persistence/security design in the MVP.

AI assistance was permitted. The candidate implemented the application and reviewed
the decisions; the assistant supplied explanations, review, diagnostic commands,
load execution and documentation assistance. Commits and PRs reflect actual progress.
