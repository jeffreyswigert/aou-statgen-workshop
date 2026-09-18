#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
python3 scripts/check_ids.py results/qc.psam "$PHENO_FILE" "$COVAR_FILE"
p2 --pfile results/qc --pheno "$PHENO_FILE" --pheno-name trait \
  --covar "$COVAR_FILE" --covar-name age,sex,PC1,PC2,PC3,PC4,PC5 \
  --covar-variance-standardize age PC1 PC2 PC3 PC4 PC5 \
  --glm hide-covar omit-ref --out results/assoc
python3 scripts/summarize.py
