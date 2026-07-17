# Cosmos hot-partition runbook

1. Confirm 429 throttles and identify the partition key consuming RU.
2. Verify the application performs point reads with both `id` and `/parcel_id`.
3. If a workload is accidentally querying by hub, move that query to the lakehouse or materialize a separate read model; do not change the tracking container’s key casually.
4. Temporarily raise RU only while the query pattern is corrected; then review costs and autoscale limits.
