#!/usr/bin/env bash
# Summarize one real AoU phenotype from data/pheno_menu.tsv (aggregates only).
# Requires Controlled Tier access, and CDR_DATASET + BILLING_PROJECT in config.sh.
source "$(dirname "$0")/common.sh"
command -v bq >/dev/null || [[ "${DRY_RUN:-}" == 1 ]] || {
  echo 'bq (BigQuery CLI) not found -- run this on the AoU Workbench VM.' >&2; exit 1; }
python3 scripts/pheno_summary.py "$@"
