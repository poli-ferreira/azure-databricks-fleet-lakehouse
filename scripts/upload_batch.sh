#!/usr/bin/env bash
# Upload batch dimension CSVs to the landing container.
# Prereq: az login; run from the repo root after generate_batch_data.py.
set -euo pipefail

ACCOUNT=$(cd terraform/azure && terraform output -raw storage_account_name)

for f in vehicles drivers; do
  az storage fs file upload \
    --account-name "$ACCOUNT" \
    --file-system landing \
    --source "data/out/${f}.csv" \
    --path "${f}/${f}.csv" \
    --auth-mode login \
    --overwrite
  echo "uploaded ${f}.csv"
done
