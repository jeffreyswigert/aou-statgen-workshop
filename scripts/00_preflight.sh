#!/usr/bin/env bash
# 00_preflight.sh -- check the environment BEFORE any analysis, so a missing
# tool or file fails here, with a clear message, rather than five commands in.
# Run it at the start of every session; it changes nothing and takes a second.
source "$(dirname "$0")/common.sh"

printf 'Working directory: %s\nData mode: %s\n' "$PWD" "$DATA_MODE"

# Are the programs we need actually available? "command -v X" succeeds only
# if X can be run from this shell.
command -v python3 >/dev/null
command -v "$PLINK2" >/dev/null || { echo 'PLINK 2 missing: ask instructor to finish setup.' >&2; exit 1; }
"$PLINK2" --version
python3 --version

# If a local fileset is already present (the optional synthetic track ships
# one), check that it is whole and that its IDs join. In the live-data lab
# no genotypes exist yet -- script 10 stages them from the cloud -- so an
# absent fileset here is expected, not an error.
# ("test -s FILE" fails if FILE is missing or empty.)
if [[ -s "$INPUT_PREFIX.pgen" ]]; then
  # A plink fileset is one prefix + three files; losing any one breaks the set.
  for ext in pgen pvar psam; do test -s "$INPUT_PREFIX.$ext"; done
  # The most important check: do the phenotype and covariate tables actually
  # match the genotype samples BY ID? A join by row order can "work" and
  # attach the wrong person's outcome to every genotype. Read check_ids.py.
  python3 scripts/check_ids.py "$INPUT_PREFIX.psam" "$PHENO_FILE" "$COVAR_FILE"
  printf 'Local fileset present and consistent:\n'
  ls -lh "$INPUT_PREFIX.pgen" "$INPUT_PREFIX.pvar" "$INPUT_PREFIX.psam"
else
  echo 'No local genotype fileset yet -- the live lab stages one in step 10.'
fi

# Enough disk for results? (This exercise needs very little.)
df -h .

# gcloud fetches the cloud files; bq queries the CDR. Both live on AoU VMs.
if command -v gcloud >/dev/null; then echo 'gcloud available'; else echo 'gcloud missing: cloud fetches and saves need the AoU VM.'; fi
if command -v bq >/dev/null; then echo 'bq available'; else echo 'bq missing: the phenotype query needs the AoU VM.'; fi

printf 'Preflight passed.\n'

# TRY IT: break something on purpose and watch this script catch it --
#   PLINK2=/does/not/exist bash scripts/00_preflight.sh
# A pipeline you have seen fail LOUDLY is one you can trust more.
