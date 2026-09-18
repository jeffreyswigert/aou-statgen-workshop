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

# Do all three genotype files exist and have content? A plink fileset is one
# prefix + three files; losing any one of them breaks the set.
# ("test -s FILE" fails if FILE is missing or empty.)
for ext in pgen pvar psam; do test -s "$INPUT_PREFIX.$ext"; done

# The most important check: do the phenotype and covariate tables actually
# match the genotype samples BY ID? A join by row order can "work" and attach
# the wrong person's outcome to every genotype. Read scripts/check_ids.py.
python3 scripts/check_ids.py "$INPUT_PREFIX.psam" "$PHENO_FILE" "$COVAR_FILE"

# Enough disk for results? (This exercise needs very little.)
df -h .

# gcloud is only needed for the cloud-save step at the end.
if command -v gcloud >/dev/null; then echo 'gcloud available'; else echo 'Cloud save requires gcloud on the AoU VM.'; fi

printf 'Preflight passed. Input sizes:\n'
ls -lh "$INPUT_PREFIX.pgen" "$INPUT_PREFIX.pvar" "$INPUT_PREFIX.psam"

# TRY IT: break something on purpose and watch this script catch it --
#   PLINK2=/does/not/exist bash scripts/00_preflight.sh
# A pipeline you have seen fail LOUDLY is one you can trust more.
