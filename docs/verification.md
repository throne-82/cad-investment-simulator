# Verification and known limitations

All times below are UTC on October 20, 2026 (Montreal = UTC minus four hours).
The deadline is 04:50 UTC. Evidence is collected from real commands and runs;
configured settings are distinguished from observed behavior.

## Delivery and calculation

- Public frontend and proxied API: [live URL](https://cad-frontend.greenmushroom-f0d12a6f.canadacentral.azurecontainerapps.io).
- [CI on application commit 4913139](https://github.com/throne-82/cad-investment-simulator/actions/runs/39369337126)
  and [OIDC deployment](https://github.com/throne-82/cad-investment-simulator/actions/runs/39369337100)
  completed successfully. The latter completed around 04:25 and ran the public smoke check.
- A real subsequent commit after the TLS fix deployed new application digests,
  including structured request logging; this was not only an initial provisioning run.
- Ruff passed and 22 API tests passed: zero interest, zero contributions, an
  independently calculated 1% monthly example, bounds, types, non-finite values,
  malformed/missing fields and health. API zero-rate example returns CAD 3,400.
- The frontend was exercised manually during development and through CI's public
  proxy checks. A full browser/accessibility/device matrix was not executed.

## Security and failure recovery

See [HTTP observations](evidence/http-checks.json): HTTP redirects 301 to HTTPS,
public health returns 200, invalid/excessive input returns controlled 422 with no
stack trace, and an external request to the internal backend FQDN returns platform
404 rather than the API. This single probe supports, but does not replace, the
verified internal-ingress configuration.

Both local and deployed containers were inspected with `id`: backend UID 10001,
frontend UID 101. ACR admin credentials and storage shared-key authentication are
disabled. Role scopes are recorded in [operations](operations.md#authentication-and-authorization).
Terraform state, plans and local configuration are ignored and not tracked.
The application has no persisted financial data or user authentication.

The [local recovery record](evidence/recovery.json) shows baseline API 200,
frontend 200 while the backend was stopped, API 504 during unavailability,
successful health-checked restart, then API 200 at 04:31:32. This is a controlled
local recovery test, not an Azure outage experiment. Exact-image rollback was not
run; the procedure is documented in the runbook.

Runtime dependency auditing passed in CI. Trivy 0.76.0 scanned both deployed
images from deployed application revision 4913139 after the load test (the exact
digests are embedded in reports):

| Image | HIGH package findings | CRITICAL package findings |
| --- | ---: | ---: |
| [Backend](evidence/backend-image-scan.json) | 48 | 0 |
| [Frontend](evidence/frontend-image-scan.json) | 0 | 0 |

The 48 backend package findings cover 12 distinct vulnerability IDs, including
Debian base packages and Python package metadata. Several OS findings have no
fixed version in the scanner's data. Python metadata findings include msgpack,
setuptools and urllib3; their relationship to the installed runtime requirements
and potential vendored/base-image copies requires investigation. A passing
requirements audit does not invalidate image findings. Reachability was not
established and no assertion of exploitability or complete security is made.
Refresh/remediate the base image, remove unnecessary build tooling where possible,
investigate Python package origins and repeat scans before production use.
The image scan is evidence for the specified revision, not a claim that every
future image automatically passes an image-scan gate. CI audits runtime packages;
image scanning was an assessment verification step.

## Observability

[Real Log Analytics rows](evidence/log-analytics-sample.json) contain route,
status, elapsed milliseconds and correlation IDs from the deployed backend.
Rows at 04:29:45 confirm ingestion, not just local stdout. Financial request
bodies and authorization headers are absent from the structured schema. A
diagnostic check also verified they were absent for a synthetic sample request.
The runbook includes KQL for errors, latency and correlation lookup.

The [platform log sample](evidence/system-log-sample.json) records container
creation/start and a failed readiness probe during scale-out. The replica
timeline distinguishes allocated from ready replicas; all four backend replicas
were ready by 04:30:38 and both frontend replicas by 04:31:13, with zero container
restarts in those samples. Allocation alone was not counted as readiness.

Azure Monitor metrics were queried for both apps: replica count, requests,
CPU nanocores and working-set bytes. Ingestion can lag; incomplete latest buckets
must not be interpreted as a real zero-replica outage. The direct replica timeline
is the primary evidence for scale-out/scale-in timing.

## Load results

The bounded k6 run uses the public frontend `/api/simulate` path, varied valid
inputs and no artificial backend delay. Baseline 2 VUs, ramp to 20 and 100,
sustained 100, then recovery to 2; total 5m30s. Preselected thresholds are errors
below 1%, p95 below 500 ms and checks above 99%. Results include scale transitions
and warm-up; per-stage latency percentiles were not separately exported.

The run started at 04:29:26 and completed around 04:34:58. See the
[raw k6 summary](evidence/k6-summary.json) and
[human-readable threshold results](evidence/k6-summary.txt).

| Measurement | Observed result | Preselected target |
| --- | ---: | --- |
| Requests | 49,224 | Bounded 5m30s test |
| Average throughput | 149.10 requests/s | Observational |
| Failed requests | 3 / 49,224 = 0.0061% | Below 1%: passed |
| p95 latency | 1,080.87 ms | Below 500 ms: **failed** |
| Median / average latency | 130.62 / 357.82 ms | Observational |
| Maximum latency | 5,080.22 ms | Observational |
| Checks | 98,442 / 98,448 = 99.9939% | Above 99%: passed |
| Backend replicas | 1 initially, 4 allocated by 04:29:45, 4 ready by 04:30:38 | Aim 1 to 4: observed |
| Frontend replicas | 1 initially, 2 allocated by 04:30:03, 2 ready by 04:31:13 | Max 2: observed |

k6 exited **99** because the latency threshold failed. No threshold was relaxed
after seeing the result. The summary-export format uses a `true` threshold flag
for a breached threshold; the text summary removes that ambiguity. The script
did not export individual failed responses, so their exact status/cause cannot
be inferred from the three failures alone. A separate
[redacted proxy log sample](evidence/proxy-error-sample.json) confirms at least
one HTTP 504 associated with an upstream connection timeout during the load.
The sampled query is not a complete accounting of all three failed requests.

Azure Monitor's collected one-minute samples show peak backend CPU of approximately
0.235 vCPU and frontend 0.246 vCPU, close to each app's 0.25-vCPU replica request.
The frontend also reached its two-replica cap. This makes frontend capacity a
plausible contributor, alongside backend capacity and network/queue time; it is
not an isolated bottleneck proof. Working-set maxima were about 120 MiB backend
and 101 MiB frontend. See [backend metrics](evidence/backend-metrics.json) and
[frontend metrics](evidence/frontend-metrics.json). Azure aggregation is not a
per-process profile or a sum across replicas. One
[load-generator sample](evidence/load-generator-sample.json) showed 23.49% Docker
CPU and 65.26 MiB memory; this single sample cannot exclude every client bottleneck.

The representative conclusion is successful scale-out and very low error rate,
with a missed latency target under the 100-VU offered load. Production tuning
requires capacity and arrival-rate measurements; four replicas do not establish
four-times throughput. The [replica timeline](evidence/replica-timeline.json) includes the cooldown window. cad-backend had 4 replicas at the last sample (2026-10-20T04:40:29.074812+00:00); return to one was not observed in this collection window. cad-frontend had 2 replicas at the last sample (2026-10-20T04:40:29.074812+00:00); return to one was not observed in this collection window. The configured minimum remains one on each app; no manual replica reset was used.

A separate **30-second, two-VU post-load check** used the same script with CLI
override `--vus 2 --stage 30s:2`, keeping every threshold unchanged. It produced
1,684 requests at 56.08 requests/s, zero errors, p95 103.22 ms and all 3,368
checks passing (exit 0). See [its summary](evidence/k6-baseline-summary.json).
This confirms recovery at lower offered load on the warm deployment; it does
not replace the failed 100-VU result or establish one-replica baseline capacity.

The test suite emitted one Starlette/httpx deprecation warning. All 22 tests
passed; adapting the test client dependency should be handled in a reviewed update.

## Remaining production work

- Remediate and rescan image vulnerabilities; evaluate reachability and dependencies.
- Pin GitHub Actions to immutable reviewed commit SHAs and update older Action versions.
- Require CI and reviewed PRs through branch protection; the workflow itself is not protection.
- Calibrate autoscaling and latency SLOs using a representative arrival-rate test;
  concurrency target 2 is deliberately low for demonstration.
- Add cost notifications and confirm a finite evaluator availability period.
- Review health access-log volume and log sampling for larger traffic volumes.
- Exercise exact-digest rollback and expand browser/accessibility verification.
- Optional persisted history (#13) remains deferred; it needs a separate authorization,
  storage and cost design. There is no database in this MVP.
