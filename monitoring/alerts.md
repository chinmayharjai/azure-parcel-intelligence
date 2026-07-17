# Monitoring and alerts

- Alert when an ADF pipeline run fails, retries are exhausted, or its duration exceeds the rolling p95.
- Alert on Databricks job failure and DQ incident count above zero; do not auto-retry a failed control total without investigation.
- Monitor Cosmos `Normalized RU Consumption`, `Total Requests`, and HTTP 429 rate. Scale only after validating a non-hot partition key.
- Create an Azure Cost Management budget on the resource group with 50%, 80%, and 100% notifications before running large demos.

The local demo writes `data/demo_summary.json` and `data/quality/dq_incidents.jsonl`, which are the evidence artifacts to inspect in a recruiter walkthrough.
