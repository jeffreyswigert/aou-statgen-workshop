#!/usr/bin/env python3
"""Generate the fictitious teaching dataset. Python standard library only.

Run via 01_prepare_synthetic.sh; the lab does not need it (data/ ships ready).
Everything is seeded, so every rebuild is byte-identical. Reading this file
answers "what did QC actually find?": it plants a causal variant (effect 0.9
per ALT copy at SIMV001201), two sampling strata with different allele
frequencies, twelve high-missingness people, forty high-missingness sites,
twenty very rare sites, and ten LowQual site flags.
"""
import csv, json, random
from pathlib import Path
r = random.Random(20260918)
out = Path('data'); out.mkdir(exist_ok=True)
n, m = 600, 2400
ids = [f'SIM{i+1:04d}' for i in range(n)]
group = [i % 2 for i in range(n)]
age = [r.uniform(25, 75) for _ in ids]
sex = [r.randrange(2) for _ in ids]  # simulated binary covariate, no biological inference
G = []
for j in range(m):
    p = r.uniform(.12, .45)
    if j < 20: p = .003
    row = []
    for i in range(n):
        q = min(.9, max(.02, p + (.18 if group[i] else -.08))) if 100 <= j < 700 else p
        row.append(int(r.random() < q) + int(r.random() < q))
    G.append(row)
# Planted effect at a fictitious locus. Trait units are arbitrary.
y = [0.9 * G[1200][i] + 1.2 * group[i] + .02 * (age[i]-50) + .3 * sex[i] + r.gauss(0, 1) for i in range(n)]
with (out/'toy.vcf').open('w') as f:
    f.write('##fileformat=VCFv4.2\n##source=entirely_synthetic_workshop\n')
    f.write('##contig=<ID=22,length=50818468>\n##FILTER=<ID=LowQual,Description="Simulated site failure">\n')
    f.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
    f.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t'+'\t'.join(ids)+'\n')
    for j,row in enumerate(G):
        calls=[]
        for i,g in enumerate(row):
            missing = r.random() < (.25 if i < 12 else .001)
            if 20 <= j < 60: missing = missing or r.random() < .18
            calls.append('./.' if missing else ['0/0','0/1','1/1'][g])
        filt = 'LowQual' if 60 <= j < 70 else 'PASS'
        f.write(f'22\t{1000000+j*1000}\tSIMV{j+1:06d}\tA\tG\t.\t{filt}\t.\tGT\t'+'\t'.join(calls)+'\n')
for name, header, rows in [
    ('phenotypes.tsv',['#IID','trait'],[[ids[i],f'{y[i]:.8f}'] for i in range(n)]),
    ('base_covariates.tsv',['#IID','age','sex'],[[ids[i],f'{age[i]:.8f}',sex[i]] for i in range(n)])]:
    with (out/name).open('w') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(header);w.writerows(rows)
(out/'provenance.json').write_text(json.dumps({'data_mode':'synthetic','seed':20260918,'samples':n,'variants':m,'causal_variant':'SIMV001201','effect_per_ALT':0.9,'build':'fictitious positions on chr22; no biological interpretation','relatedness':'independently sampled; no pedigrees','PCs':'estimated from the synthetic genotypes during preparation'},indent=2)+'\n')
print('Created 600 fictitious samples and 2,400 variants. No AoU participant data.')
