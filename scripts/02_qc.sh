#!/usr/bin/env bash
# 02_qc.sh -- quality control in explicit, auditable stages.
#
# One deliberate design choice to notice: this could be a single plink2
# command, but separate stages mean each exclusion gets its own log and its
# own before/after counts -- you can NARRATE the funnel ("600 in, 588 out,
# because...") to a collaborator or a reviewer. That narration is the product.
# After running, open results/qc_counts.tsv and any of the .log files.
source "$(dirname "$0")/common.sh"

# Stage 0: measure everything BEFORE excluding anything.
#   --freq    allele frequencies        -> results/raw.afreq
#   --missing missingness per sample    -> results/raw.smiss  (s = sample)
#             and per variant           -> results/raw.vmiss  (v = variant)
p2 --pfile "$INPUT_PREFIX" --freq --missing --out results/raw

# Stage 1: keep eligible SITES. Autosomes only; simple A/C/G/T SNPs with at
# most two alleles; and --var-filter drops variants whose FILTER column names
# an upstream failure (our synthetic data plants ten "LowQual" sites).
# --make-pgen writes a new, smaller fileset rather than modifying the input.
p2 --pfile "$INPUT_PREFIX" --autosome --snps-only just-acgt --max-alleles 2 --var-filter --make-pgen --out results/sites

# Stage 2: remove poorly measured SAMPLES. --mind 0.05 drops any person
# missing more than 5% of their genotype calls.
p2 --pfile results/sites --mind 0.05 --make-pgen --out results/samples

# Stage 3: only AFTER the samples are settled, filter VARIANTS -- removing
# people changes every variant's statistics, so this order is deliberate.
#   --geno 0.02  drop variants missing in >2% of remaining people
#   --maf 0.05   minimum minor-allele FREQUENCY (a proportion)
#   --mac 20     minimum minor-allele COUNT (how many copies support a test)
p2 --pfile results/samples --geno 0.02 --maf 0.05 --mac 20 --make-pgen --out results/qc

# Re-measure the cleaned data, for before/after comparison.
p2 --pfile results/qc --freq --missing --out results/clean

# Write the funnel table: samples and variants remaining at each stage.
python3 scripts/qc_counts.py

# These thresholds are EXERCISE settings, not a protocol. A real AoU analysis
# takes QC from the release documentation and your study design.
#
# TRY IT (after the lab): loosen the frequency filter and compare funnels.
#   Copy the whole workshop folder first, so your baseline survives:
#       cp -r ../aou_cli_workshop ../aou_cli_workshop_maf01
#   then in the copy change --maf 0.05 to --maf 0.01, re-run this script, and
#   diff the two results/qc_counts.tsv files. On this synthetic data the
#   change may keep the same variants -- a null result that tells you about
#   the allele-frequency distribution. Then try tightening --mind to 0.02 and
#   explain the funnel you get.
