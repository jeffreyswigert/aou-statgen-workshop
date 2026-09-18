# Source from the package root. This file defines workshop settings.
export DATA_MODE=synthetic
export INPUT_PREFIX=data/toy
export PHENO_FILE=data/phenotypes.tsv
export COVAR_FILE=data/covariates.tsv
export PROVENANCE_FILE=data/provenance.json
export PLINK2="${PLINK2:-plink2}"
export THREADS=2
export MEMORY_MB=1024
# Instructor fills these from the selected AoU workspace Resources tab.
# These are workshop variables, NOT promised Workbench environment variables.
# WORKSHOP_BUCKET falls back to WORKSPACE_BUCKET when that is set, so the same
# scripts run unchanged inside the local AoU sandbox (source its env.sh first)
# and against a real authorized bucket. Verify the value before an AoU save.
export WORKSHOP_BUCKET="${WORKSHOP_BUCKET:-${WORKSPACE_BUCKET:-}}"
export BILLING_PROJECT="${BILLING_PROJECT:-}"
export CDR_DATASET="${CDR_DATASET:-}"
