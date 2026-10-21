#!/usr/bin/env python3
"""Score saved Cephalo protein QA predictions. CPU only; never runs a model.

This script is an extracted, CLI-friendly revision of the historical offline
six-run scorer, preserving its normalization and per-profile matching rules.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from strict_labels import LABELS, normalize_short_label

PROFILES = ('spider_only', 'general_only', 'spider_staged')
EXPECTED_RECORDS = {'spider_only': 1519, 'general_only': 4914, 'spider_staged': 1519}
EXPECTED_PROTEINS = {'spider_only': 217, 'general_only': 702, 'spider_staged': 217}
KEY = ['protein_name', 'question']


def evaluate(df, source):
    df = df.copy()
    req = {'protein_name','question','gold','pred'}
    if not req.issubset(df):
        raise ValueError(f'{source}: missing columns {sorted(req-set(df))}')
    if df.duplicated(KEY).any():
        raise ValueError(f'{source}: duplicate protein/question pair')
    unknown = set(df.question) - set(LABELS)
    if unknown:
        raise ValueError(f'{source}: unknown questions {sorted(unknown)}')
    df['canonical_gold'] = [normalize_short_label(g,q) for g,q in zip(df.gold,df.question)]
    df['canonical_pred'] = [normalize_short_label(p,q) for p,q in zip(df.pred,df.question)]
    if df.canonical_gold.isna().any():
        raise ValueError(f'{source}: invalid reference labels')
    df['format_compliant'] = df.canonical_pred.notna()
    df['categorical_correct'] = df.format_compliant & df.canonical_pred.eq(df.canonical_gold)
    return df


def compare_profile(name, input_dir, output_dir, reps, seed, strict_n, rng):
    ft = evaluate(pd.read_csv(input_dir/f'{name}_fine_tuned.csv'), f'{name}/fine_tuned')
    zs = evaluate(pd.read_csv(input_dir/f'{name}_zero_shot.csv'), f'{name}/zero_shot')
    checks=[]
    if strict_n:
        for model,frame in (('fine_tuned',ft),('zero_shot',zs)):
            if len(frame)!=EXPECTED_RECORDS[name] or frame.protein_name.nunique()!=EXPECTED_PROTEINS[name]:
                raise ValueError(f'{name}/{model}: unexpected number of QA or proteins')
    for model,frame in (('fine_tuned',ft),('zero_shot',zs)):
        if model=='fine_tuned' and 'EM' in frame:
            mismatch=int((frame.categorical_correct.astype(int)!=pd.to_numeric(frame.EM,errors='raise').astype(int)).sum())
            checks.append(dict(profile=name,check='historical_EM_mismatch',value=mismatch))
            if mismatch:raise ValueError(f'{name}: {mismatch} historical EM mismatches')
    m=ft[KEY+['canonical_gold','categorical_correct']].merge(
        zs[KEY+['canonical_gold','categorical_correct']],on=KEY,
        suffixes=('_ft','_zs'),validate='one_to_one')
    if len(m)!=len(ft) or len(m)!=len(zs):
        raise ValueError(f'{name}: unpaired QA records')
    if not m.canonical_gold_ft.eq(m.canonical_gold_zs).all():
        raise ValueError(f'{name}: inconsistent references')
    checks.append(dict(profile=name,check='paired_QA_records',value=len(m)))
    summaries=[]; tasks=[]
    for model,frame in (('fine_tuned',ft),('zero_shot',zs)):
        summaries.append(dict(profile=name,model=model,proteins=frame.protein_name.nunique(),
            qa=len(frame),correct=int(frame.categorical_correct.sum()),
            strict_accuracy=float(frame.categorical_correct.mean()),
            format_compliance=float(frame.format_compliant.mean())))
        for q,g in frame.groupby('question'):
            counts=g.canonical_gold.value_counts()
            tasks.append(dict(profile=name,model=model,question=q,n=len(g),
                accuracy=float(g.categorical_correct.mean()),
                majority_reference=float(counts.max()/len(g)),
                format_compliance=float(g.format_compliant.mean())))
    # Re-sample individual PROTEINS with replacement, maintaining paired seven-QA blocks.
    byprotein=m.groupby('protein_name',sort=True).agg(
        ft=('categorical_correct_ft','mean'),zs=('categorical_correct_zs','mean'))
    effects=(byprotein.ft-byprotein.zs).to_numpy()
    samples=np.empty(reps)
    for i in range(0,reps,250):
        k=min(250,reps-i)
        idx=rng.integers(0,len(effects),size=(k,len(effects)))
        samples[i:i+k]=effects[idx].mean(axis=1)
    lo,hi=np.quantile(samples,[0.025,0.975])
    boot=dict(profile=name,n_proteins=len(effects),n_qa=len(m),
        difference_pp=100*effects.mean(),ci95_lower_pp=100*lo,ci95_upper_pp=100*hi,
        replicates=reps,seed=seed)
    return summaries,tasks,checks,boot


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=Path('results/reproduced'))
    parser.add_argument('--bootstrap-replicates',type=int,default=10000)
    parser.add_argument('--seed',type=int,default=20261021)
    parser.add_argument('--allow-other-sample-sizes',action='store_true',help='Disable historical sample-size checks for synthetic tests')
    args=parser.parse_args()
    if args.bootstrap_replicates<100:raise ValueError('Require >=100 bootstrap replicates')
    args.out.mkdir(parents=True,exist_ok=True)
    summaries=[];tasks=[];checks=[];boots=[]
    rng=np.random.default_rng(args.seed)
    for p in PROFILES:
        x,y,z,b=compare_profile(p,args.input_dir,args.out,args.bootstrap_replicates,args.seed,not args.allow_other_sample_sizes,rng)
        summaries+=x;tasks+=y;checks+=z;boots.append(b)
    s=pd.DataFrame(summaries)
    c=[]
    for p in PROFILES:
        f=s.query('profile==@p and model=="fine_tuned"').iloc[0]
        z=s.query('profile==@p and model=="zero_shot"').iloc[0]
        c.append(dict(profile=p,n=int(f.qa),zero_shot_strict_accuracy=z.strict_accuracy,
                      fine_tuned_accuracy=f.strict_accuracy,observed_difference_pp=100*(f.strict_accuracy-z.strict_accuracy),
                      zero_shot_format_compliance=z.format_compliance,fine_tuned_format_compliance=f.format_compliance))
    files={'six_run_summary.csv':s,'six_run_per_task.csv':pd.DataFrame(tasks),
           'matched_comparison.csv':pd.DataFrame(c),
           'paired_bootstrap_effects.csv':pd.DataFrame(boots),
           'integrity_checks.csv':pd.DataFrame(checks)}
    for filename,frame in files.items():frame.to_csv(args.out/filename,index=False)
    print(pd.DataFrame(c).round(4).to_string(index=False))
    print('Saved:',args.out)

if __name__=='__main__':main()
