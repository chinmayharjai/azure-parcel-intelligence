# Access-pattern matrix

| Consumer and question | Store | Why it fits | Expected latency |
|---|---|---|---|
| Customer: “Where is `parcel_id` now?” | Cosmos DB | One document, point read on `/parcel_id` | under 50 ms target |
| Operations: “Which hubs have growing backlog?” | Lakehouse Gold | Large scans, history, hourly aggregate refresh | seconds |
| Finance: “What were lane SLA breaches by day?” | Azure SQL | Dimensional joins and BI-compatible reconciliation | seconds to minutes |

One pipeline publishes the same governed event history into each serving shape. Each store is intentionally chosen for an access pattern rather than being a duplicate system of record.
