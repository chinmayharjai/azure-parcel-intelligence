# Repository Guidelines

## Project Structure & Module Organization

`simulator/scan_events.py` produces partitioned JSON scan batches and a seller extract. `pipeline/transform.py` is the portable reference implementation for bronze, silver, and gold transformations; it uses JSONL so the complete data flow can run without cloud credentials. `scripts/run_demo.py` orchestrates the demo and is the best entry point for validating a change.

`databricks/` holds the corresponding Spark/Delta notebook sources, while `adf/` contains import-ready orchestration templates with parameterized connections. `serving/` contains the Cosmos document shape and Azure SQL mart, with SQLite adapters used locally. `quality/` owns publication-blocking control totals. Operational guidance lives under `monitoring/` and `runbooks/`.

## Build, Test, and Development Commands

Run the complete local pipeline with `python -m scripts.run_demo --parcels 1000 --seed 42`. It recreates ignored `data/` by default and writes `data/demo_summary.json` as evidence. Query a tracking document with `python -m serving.cosmos.lookup PAR00000001` and inspect the reporting mart with `python -m serving.azure_sql.report`.

Run the suite with `python -m pytest -q`. Use `python -m pytest tests/test_pipeline.py -q` for the single end-to-end test. The project declares Python 3.11 or higher in `pyproject.toml` and needs no runtime third-party packages.

## Coding Style & Naming Conventions

Use Python standard-library modules for the local demo unless a dependency materially improves the Azure implementation. Keep events as JSON-serializable dictionaries with snake_case field names. Preserve deterministic CLI behavior with an explicit seed. Paths are supplied as `pathlib.Path`, and runtime artifacts must remain beneath ignored `data/` or `artifacts/`.

## Testing Guidelines

The integration test asserts the complete contract: all generated parcels reach Cosmos, DQ is clean, and the serving document retains its partition key. When changing transforms, preserve idempotence by `scan_id`, PII removal from Silver, and the delivered-parcel control total that gates the mart load.
