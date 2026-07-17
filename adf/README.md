# Azure Data Factory deployment map

These templates are safe to import as a starting point: connection values are parameters and no secrets are included. In Azure, create Key Vault-backed linked services, then bind dataset parameters during deployment.

`pipeline_ingest.json` copies landing data to Bronze and documents the self-hosted Integration Runtime pattern for a private seller-master source. `pipeline_serve.json` invokes the DQ gate before allowing Gold-to-SQL publication, then upserts current state to Cosmos DB. Both use three retries and exponential retry intervals.

The local equivalent is `python -m scripts.run_demo`; it executes the same sequence deterministically.
