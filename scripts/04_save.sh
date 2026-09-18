#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
: "${WORKSHOP_BUCKET:?Set WORKSHOP_BUCKET to your authorized workspace gs:// bucket}"
[[ "$WORKSHOP_BUCKET" == gs://* ]] || { echo 'Expected a gs:// workspace bucket' >&2; exit 1; }
command -v gcloud >/dev/null
# Archive stays on the VM, then copies to this workspace's authorized bucket.
# Results may be sensitive in AoU mode. Do not export this archive to your laptop.
# Disclosure screen runs before anything is packaged. In AoU mode a small-count
# finding stops the save here (set -e) unless DISCLOSURE_ACK=1 records a review.
python3 scripts/check_disclosure.py results
run_id="$(date -u +%Y%m%dT%H%M%SZ)-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')"
mkdir -p runs
manifest="results/run_manifest.txt"
{
  printf 'data_mode=%s\ncdr_dataset=%s\ninput_prefix=%s\n' "$DATA_MODE" "$CDR_DATASET" "$INPUT_PREFIX"
  "$PLINK2" --version
  sha256sum "$INPUT_PREFIX.pgen" "$INPUT_PREFIX.pvar" "$INPUT_PREFIX.psam" "$PHENO_FILE" "$COVAR_FILE"
} > "$manifest"
tar -czf "runs/$run_id.tar.gz" "${WORKSHOP_CONFIG:-config.sh}" scripts results "$PROVENANCE_FILE"
cloud_flags=()
[[ -z "$BILLING_PROJECT" ]] || cloud_flags+=(--billing-project="$BILLING_PROJECT")
dest="${WORKSHOP_BUCKET%/}/statgen-workshop/$run_id.tar.gz"
gcloud "${cloud_flags[@]}" storage cp "runs/$run_id.tar.gz" "$dest"
gcloud "${cloud_flags[@]}" storage ls "$dest"
printf 'Saved. Stop the cloud app in the Workbench when finished.\n'
