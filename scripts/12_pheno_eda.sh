#!/usr/bin/env bash
# 12_pheno_eda.sh (Lab 1, live data) -- look at the real phenotype before any model.
# Reads results/aou_pheno.tsv; writes an aggregate summary and two figures.
# All printed numbers are aggregate, suppression- and rounding-screened.
source "$(dirname "$0")/common.sh"
[[ -s results/aou_pheno.tsv ]] || { echo 'No phenotype file. Run: bash scripts/11_build_phenotype.sh' >&2; exit 1; }
python3 -c 'import numpy, matplotlib' 2>/dev/null || {
  echo 'Needs python3 with numpy and matplotlib (preinstalled on the AoU VM).' >&2; exit 1; }
python3 scripts/aou_pheno_eda.py
