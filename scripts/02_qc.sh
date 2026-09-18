#!/usr/bin/env bash
source "$(dirname "$0")/common.sh"
# Separate calls make the QC sequence explicit and each stage auditable.
p2 --pfile "$INPUT_PREFIX" --freq --missing --out results/raw
p2 --pfile "$INPUT_PREFIX" --autosome --snps-only just-acgt --max-alleles 2 --var-filter --make-pgen --out results/sites
p2 --pfile results/sites --mind 0.05 --make-pgen --out results/samples
p2 --pfile results/samples --geno 0.02 --maf 0.05 --mac 20 --make-pgen --out results/qc
p2 --pfile results/qc --freq --missing --out results/clean
python3 scripts/qc_counts.py
