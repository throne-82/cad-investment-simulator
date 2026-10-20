# Cost and availability plan

## Decision and controls

The initial assessment target was CAD 10. The candidate subsequently authorized
keeping the public URL available for evaluation and reported approximately CAD 280
of promotional credit, expiring November 17, 2026. The exact evaluator end date has
not been supplied. Credit is not a cost estimate or a spending cap; an indefinite
availability period cannot be promised within CAD 10.

Canada Central was selected for Canadian hosting and available quota, not because
it was assumed to be the cheapest region. Both apps use Consumption and start at
0.25 vCPU/0.5 GiB. The backend caps at four replicas and frontend at two. Minimum
one on each keeps the demo warm; scaled-out replicas should return to one after
the test. There is no database, custom VNet, dedicated compute or Elasticsearch.
ACR is Basic. State is Standard LRS. Logs retain 30 days with a 0.1 GB/day ingestion
quota. The quota can suspend logging and does not provide an exact currency cap.

## Planning estimate

These are planning assumptions, not a bill or a verified account-specific quote:

| Component | Assumption | Approximate CAD/day |
| --- | --- | ---: |
| ACR Basic | Canada Central retail API returned CAD 0.236/day on October 20 | 0.24 |
| Two minimum replicas | Treat both as active all day; 0.5 vCPU and 1 GiB combined | 1.94 |
| Log ingestion | Reserve CAD 0.50/day for low-volume logs; verify actual billable GB | 0.50 |
| Blob state, transactions and modest egress | Planning allowance, not a measured charge | 0.10 |
| **Planning total** | No free grants or credits deducted; low traffic, two replicas | **2.78** |

The compute estimate uses the published Central US reference rates of USD
0.000024/vCPU-second and USD 0.000003/GiB-second with a conservative **assumed**
CAD 1.50/USD conversion, not a measured exchange rate or Canada Central compute
quote: `(0.5*0.000024 + 1*0.000003)*86400*1.50 = CAD 1.944/day`.
The [Microsoft billing explanation](https://techcommunity.microsoft.com/blog/appsonazureblog/understanding-idle-usage-in-azure-container-apps/4419197)
provides the reference; the memory unit is GiB-second in the
[official pricing model](https://azure.microsoft.com/en-us/pricing/details/container-apps/).
The regional Retail Prices API returned zero-valued compute grant-tier records;
a follow-up query was throttled. Zero was deliberately not treated as a paid rate.
Regional paid compute and account-specific ingestion rates remain to be confirmed
in the Azure pricing calculator/Cost Management. Idle rates/free grants may reduce
the actual bill; additional traffic, replica-hours or ingestion can increase it.

At this planning rate, three days are approximately CAD 8.34 and four days CAD
11.12, before tax and any unusual traffic. The four-hour assessment itself is
approximately CAD 0.47 at two replicas, plus a short scaling test. This is an
illustrative finite period; the open-ended availability decision exceeds the
original budget assurance. A continuously active four-backend/two-frontend setup
would use three times the minimum compute, so this is not a maximum-spend bound.

The [subscription-level monthly grants](https://learn.microsoft.com/en-us/azure/container-apps/billing)
include 180,000 vCPU-seconds, 360,000 GiB-seconds and two million requests.
Their remaining balance was not verified and is not deducted above. HTTP proxy
traffic reaches two apps; do not assume one user interaction equals one billed
platform request. ACR, logs and storage have separate billing.

## Follow-up and cleanup

Check Azure Cost Management daily while the URL stays available; billing data can
lag. No budget notification was configured during the assessment. Add a CAD 10
budget with 50/80/100% actual-cost notifications after choosing an authorized
notification recipient; **budget alerts do not stop resources or cap spending**.
No email was sent by the assistant. Confirm the evaluation end date and perform
the [ordered teardown](operations.md#teardown-after-evaluator-access) afterward.
For a longer low-traffic period, explicitly review a Terraform change to minimum
zero and its cold-start impact. The current warm-demo settings remain in place.
