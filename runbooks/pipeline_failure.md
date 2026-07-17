# Pipeline failure runbook

1. Confirm the trigger fired and inspect the ADF run ID and failed activity.
2. For source copy failures, validate the self-hosted Integration Runtime health, network path, and Key Vault secret access.
3. For notebook failures, inspect the failed input partition and the Databricks job logs; rerun only the affected hour because loads are idempotent by `scan_id`.
4. For DQ failures, keep SQL publication blocked, inspect `dq_incidents`, correct the transform or source issue, then rerun the affected interval.
5. Record the cause, impact, and recovery time in the incident ticket.
