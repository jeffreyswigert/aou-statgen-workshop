#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
printf 'Working directory: %s\nData mode: %s\n' "$PWD" "$DATA_MODE"
command -v python3 >/dev/null
command -v "$PLINK2" >/dev/null || { echo 'PLINK 2 missing: ask instructor to finish setup.' >&2; exit 1; }
"$PLINK2" --version
python3 --version
for ext in pgen pvar psam; do test -s "$INPUT_PREFIX.$ext"; done
python3 scripts/check_ids.py "$INPUT_PREFIX.psam" "$PHENO_FILE" "$COVAR_FILE"
df -h .
if command -v gcloud >/dev/null; then echo 'gcloud available'; else echo 'Cloud save requires gcloud on the AoU VM.'; fi
printf 'Preflight passed. Input sizes:\n'
ls -lh "$INPUT_PREFIX.pgen" "$INPUT_PREFIX.pvar" "$INPUT_PREFIX.psam"
