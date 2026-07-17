# Parcel Intelligence Platform on Azure

> India ships ~10 million e-commerce parcels a day. Every parcel leaves a trail of scan
> events, and three very different consumers need that trail: a customer refreshing
> ""where is my order?"" (<50ms point lookup), an ops manager (hourly hub dashboards),
> and a finance team computing SLA penalties (exact, reconciled, historical).
> No single database serves all three well. Same events, three access patterns,
> three stores — orchestrated by ADF, transformed once in the lakehouse, served everywhere.

Azure Data Factory · ADLS Gen2 · Delta Lake · Databricks · Azure SQL Database · Azure Cosmos DB

**Status:** under construction — built milestone by milestone, one PR each.

| # | Milestone | Status |
|---|-----------|--------|
| M1 | Parcel scan simulator | 🚧 |
| M2 | ADF ingestion pipelines | ⬜ |
| M3 | Lakehouse bronze + silver | ⬜ |
| M4 | Lakehouse gold (ops + SLA mart) | ⬜ |
| M5 | Serving: Azure SQL + Cosmos DB | ⬜ |
| M6 | Data quality + control totals | ⬜ |
| M7 | Monitoring + runbooks | ⬜ |
| M8 | Final README + results | ⬜ |
