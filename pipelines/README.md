# Pipeline source

Three files, one medallion layer each. Create the pipeline in the workspace UI
(Jobs & Pipelines → Create → ETL pipeline) with:

- **Source code**: a Git folder pointing at this repo, include `pipelines/*.py`
- **Target catalog**: `fleet` (default schema `bronze` — tables carry explicit
  `schema.table` names, so all three schemas are used)
- **Compute**: serverless if available in your region; otherwise smallest cluster
- **Mode**: triggered while developing (continuous mode burns credit)
- **Configuration**: set `storage_account` = the value of
  `terraform output -raw storage_account_name` (used by Auto Loader paths)

Prerequisites before the first run: `scripts/setup_secrets.sh` (Event Hubs
connection in the `fleet` secret scope) and `scripts/upload_batch.sh` (dimension
CSVs in the landing container). Then start the generator and trigger the pipeline.

Note: `dbutils` and `spark` are provided by the pipeline runtime — the `# noqa`
comments keep local linters quiet about them.
