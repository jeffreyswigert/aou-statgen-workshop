#!/usr/bin/env bash
# 04_save.sh -- package the run so future-you can PROVE what was done, then
# copy the archive to the workspace bucket. A run that exists only on a VM's
# local disk is one misclick from gone.
#
# The archive holds: the code as run, the configuration, all results and
# plink logs, the provenance record, and CHECKSUMS of the inputs -- so you can
# later show exactly which data went in, even if the files move.
source "$(dirname "$0")/common.sh"

# Fail early, with a message, if no bucket is configured. ":?" is bash for
# "error out if this variable is empty".
: "${WORKSHOP_BUCKET:?Set WORKSHOP_BUCKET to your authorized workspace gs:// bucket}"
[[ "$WORKSHOP_BUCKET" == gs://* ]] || { echo 'Expected a gs:// workspace bucket' >&2; exit 1; }
command -v gcloud >/dev/null

# Archive stays on the VM, then copies to this workspace's authorized bucket.
# Results may be sensitive in AoU mode. Do not export this archive to your laptop.

# Disclosure screen runs before anything is packaged (read the script -- it is
# the compliance-by-default pattern from the slides). In AoU mode a
# small-count finding stops the save right here, because common.sh set -e
# turns its nonzero exit into a hard stop; DISCLOSURE_ACK=1 records a
# deliberate, reviewed override.
python3 scripts/check_disclosure.py results

# A unique name per run: UTC timestamp + random suffix. Never overwrite a
# previous run's archive -- disk is cheap, provenance is not.
run_id="$(date -u +%Y%m%dT%H%M%SZ)-$(python3 -c 'import uuid; print(uuid.uuid4().hex[:8])')"
mkdir -p runs

# The manifest records the settings, the plink version, and a sha256 checksum
# of every input file. Same checksum later = provably the same data.
manifest="results/run_manifest.txt"
{
  printf 'data_mode=%s\ncdr_dataset=%s\ninput_prefix=%s\n' "$DATA_MODE" "$CDR_DATASET" "$INPUT_PREFIX"
  "$PLINK2" --version
  sha256sum "$INPUT_PREFIX.pgen" "$INPUT_PREFIX.pvar" "$INPUT_PREFIX.psam" "$PHENO_FILE" "$COVAR_FILE"
} > "$manifest"

# Bundle everything into one compressed archive under runs/.
tar -czf "runs/$run_id.tar.gz" "${WORKSHOP_CONFIG:-config.sh}" scripts results "$PROVENANCE_FILE"

# Copy to the bucket, then LIST the copy -- verify the upload actually exists
# before you stop the VM. (--billing-project is only added when configured.)
cloud_flags=()
[[ -z "$BILLING_PROJECT" ]] || cloud_flags+=(--billing-project="$BILLING_PROJECT")
dest="${WORKSHOP_BUCKET%/}/statgen-workshop/$run_id.tar.gz"
gcloud "${cloud_flags[@]}" storage cp "runs/$run_id.tar.gz" "$dest"
gcloud "${cloud_flags[@]}" storage ls "$dest"
printf 'Saved. Stop the cloud app in the Workbench when finished.\n'

# TRY IT: list everything your workshop has saved so far --
#   gcloud storage ls "$WORKSHOP_BUCKET/statgen-workshop/"
# and read the disclosure report that went into the archive:
#   cat results/disclosure_report.txt
