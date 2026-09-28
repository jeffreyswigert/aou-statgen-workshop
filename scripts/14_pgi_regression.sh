#!/usr/bin/env bash
# 14_pgi_regression.sh (lab step 4) -- a basic regression that incorporates
# the PGI: standardized height on the standardized PGI, adjusting for age,
# sex, and five genetic PCs. Read scripts/aou_pgi_regression.py -- the model,
# and every data decision feeding it, live there.
source "$(dirname "$0")/common.sh"
[[ -s results/aou_pgi.sscore ]] || { echo 'No PGI yet. Run: bash scripts/13_score_real_pgi.sh' >&2; exit 1; }
[[ -s results/aou_pheno.tsv ]] || { echo 'No phenotype. Run: bash scripts/11_build_phenotype.sh' >&2; exit 1; }
python3 -c 'import numpy' 2>/dev/null || { echo 'Needs python3 with numpy (preinstalled on the AoU VM).' >&2; exit 1; }
python3 scripts/aou_pgi_regression.py
