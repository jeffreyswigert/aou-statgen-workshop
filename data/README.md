# Synthetic teaching data

All records are computer-generated. No All of Us participant data are included.

600 independent samples, 2,400 biallelic sites with fictitious chromosome-22 coordinates, one quantitative phenotype in arbitrary units. `make_synthetic.py` uses seed 20260918. Two artificial sampling strata create structure. A planted additive effect of 0.9 per G copy occurs at SIMV001201. Twelve people have high missingness, forty sites have high missingness, twenty sites are very rare, and ten sites carry a LowQual flag. Those mechanisms are distinct in this generated example.

`toy.pgen`, `toy.pvar`, and `toy.psam` are a PLINK 2 file set. `phenotypes.tsv` and `covariates.tsv` join by IID. PCs were computed before class using a QC-selected, LD-pruned marker panel on the full synthetic sample. Their signs can vary with numerical libraries without changing the regression adjustment. The binary simulated covariate is named sex; its coding is 0/1 and it is not an AoU demographic field.

Raw VCF can be regenerated using the supplied script; it is omitted from the distribution to keep the bundle small. Its alleles and positions are not biological annotations.
