#!/usr/bin/env python3
"""Construct the paper's seven *categorical labels* from existing annotations.

This is an independently curated reference-definition helper, NOT a claim of
identical historical original QA generation. Input CSV must already contain
DSSP-derived structural fractions and ProtParam-calculated properties.
"""
import argparse
from pathlib import Path
import pandas as pd

QUESTIONS = (
    'Does this protein contain alpha-helix?',
    'Does this protein contain beta-sheet?',
    'Does this protein contain coil?',
    'Which secondary structure is most prevalent?',
    'Is the protein predicted to be stable (instability index ≤ 40)?',
    'Is the protein hydrophobic (GRAVY > 0)?',
    'Is the protein acidic (pI < 7) or basic (pI > 7)?',
)
COLS=['protein_name','alpha_frac','beta_frac','coil_frac','instability_index','gravy','isoelectric_point']
def build(row):
    alpha,beta,coil=(float(row[c]) for c in ['alpha_frac','beta_frac','coil_frac'])
    vals=[alpha,beta,coil]
    # Ties favor alpha-helix, then beta-sheet, then coil.
    prevalent=['alpha-helix','beta-sheet','coil'][max(range(3),key=lambda i: vals[i])]
    pi=float(row['isoelectric_point'])
    return [
        'Yes' if alpha>0 else 'No',
        'Yes' if beta>0 else 'No',
        'Yes' if coil>0 else 'No',
        prevalent,
        'Yes' if float(row['instability_index'])<=40 else 'No',
        'Yes' if float(row['gravy'])>0 else 'No',
        'Acidic' if pi<7 else 'Basic' if pi>7 else 'Neutral',
    ]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    d=pd.read_csv(args.input)
    if not set(COLS).issubset(d):raise ValueError('Missing required columns: '+str(sorted(set(COLS)-set(d))))
    records=[]
    for _,r in d.iterrows():
        for q,ans in zip(QUESTIONS,build(r)):
            records.append({'protein_name':r['protein_name'],'question':q,'gold':ans})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(records).to_csv(args.output,index=False)
    print('Wrote',len(records),'QA records')
if __name__=='__main__':main()
