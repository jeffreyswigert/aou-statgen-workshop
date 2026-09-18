#!/usr/bin/env bash
# 03_association.sh -- fit one linear regression per QC-passing variant:
#
#   trait = a + b*(allele count) + c*age + d*sex + (5 PCs) + noise
#
# plink2 fits that model separately at each of the 2,330 variants, in about a
# second. The coefficient on the allele count, per variant, is the result.
# After running, open results/top_hits.tsv and results/analysis_summary.txt.
source "$(dirname "$0")/common.sh"

# Re-check the ID joins against the POST-QC sample before modeling. Cheap
# insurance: the expensive failures in this field are silent joins.
python3 scripts/check_ids.py results/qc.psam "$PHENO_FILE" "$COVAR_FILE"

# The scan. Flag by flag:
#   --pheno / --pheno-name        the outcome column ("trait"), by name
#   --covar / --covar-name        which covariate columns enter the model
#                                 (NOTE: this list is COMMA-separated)
#   --covar-variance-standardize  rescale these covariates for numerical
#                                 stability; the OUTCOME keeps its own units,
#                                 so betas stay interpretable
#                                 (NOTE: this list is SPACE-separated -- the
#                                 comma/space difference is a classic trap)
#   --glm            one regression per variant
#     hide-covar     keep covariate rows out of the REPORT (they stay in the
#                    model) -- the output is one row per variant, not eight
#     omit-ref       always count the ALT allele, so every row's beta means
#                    the same thing ("per additional ALT copy")
#   --out            report lands at results/assoc.trait.glm.linear
p2 --pfile results/qc --pheno "$PHENO_FILE" --pheno-name trait \
  --covar "$COVAR_FILE" --covar-name age,sex,PC1,PC2,PC3,PC4,PC5 \
  --covar-variance-standardize age PC1 PC2 PC3 PC4 PC5 \
  --glm hide-covar omit-ref --out results/assoc

# Sort by p-value, keep the top rows, and write a small human-readable
# summary including the multiple-testing threshold.
python3 scripts/summarize.py

# What this model does NOT handle: related individuals (ordinary regression
# assumes independent people) and binary outcomes (those need --glm's
# logistic path and 1/2 case-control coding).
#
# TRY IT (after the lab): what do the PCs actually do? Re-run the p2 command
#   above with --covar-name age,sex and --covar-variance-standardize age and
#   --out results/assoc_nopc, then compare the planted variant's row:
#       grep SIMV001201 results/assoc.trait.glm.linear
#       grep SIMV001201 results/assoc_nopc.trait.glm.linear
#   This synthetic data has two population strata built in -- watch what
#   ignoring structure does to the estimate.
