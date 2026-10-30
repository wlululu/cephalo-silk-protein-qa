"""Offline audit and metrics; extraction frozen before golds are joined.
Run: python scripts/analyze.py --source /path/to/read-only/repository
"""
import argparse, hashlib, json, platform
from pathlib import Path
import numpy as np
import pandas as pd
from semantic_labels import QUESTIONS as Q, LABELS, strict, key

ROOT=Path(__file__).resolve().parents[1]
PROFILES=['spider_only','general_only','spider_staged']
EXPECTED={'spider_only':217,'general_only':702,'spider_staged':217}
SHORT=dict(zip(Q,['alpha_presence','beta_presence','coil_presence','predominant','stability','hydrophobicity','pI']))
SEED=20261030; REPS=10000

def class_stats(g,pred):
 out=[]
 for q,t in g.groupby('question',sort=False):
  for c in LABELS[q]:
   support=int(t.gold_label.eq(c).sum()); npred=int(t[pred].eq(c).sum())
   tp=int((t.gold_label.eq(c)&t[pred].eq(c)).sum()); fp=npred-tp;fn=support-tp
   out.append(dict(property=SHORT[q],label=c,support=support,predicted=npred,tp=tp,fp=fp,fn=fn,
    precision=tp/npred if npred else np.nan,recall=tp/support if support else np.nan,
    f1=2*tp/(2*tp+fp+fn) if support else np.nan))
 return pd.DataFrame(out)

def metric_row(g):
 cs=class_stats(g,'label')
 return dict(n=len(g),proteins=g.protein_name.nunique(),strict_correct=int(g.strict_correct.sum()),
  strict_accuracy=g.strict_correct.mean(),format_compliance=g.strict_label.notna().mean(),
  accuracy_format_compliant=g.loc[g.strict_label.notna(),'strict_correct'].mean(),
  strict_errors_noncompliant_fraction=(g.strict_label.isna().sum()/(~g.strict_correct).sum()) if (~g.strict_correct).sum() else np.nan,
  semantic_correct=int(g.semantic_correct.sum()),semantic_accuracy=g.semantic_correct.mean(),
  semantic_coverage=g.label.notna().mean(),semantic_conditional_accuracy=g.loc[g.label.notna(),'semantic_correct'].mean(),
  ambiguous_n=int(g.status.eq('ambiguous').sum()),ambiguous_rate=g.status.eq('ambiguous').mean(),
  unparseable_n=int(g.status.eq('unparseable').sum()),unparseable_rate=g.status.eq('unparseable').mean(),
  unresolved_rate=g.label.isna().mean(),optimistic_accuracy_upper=g.semantic_correct.mean()+g.label.isna().mean(),
  task_mean_balanced_accuracy=cs.groupby('property').recall.mean().mean(),
  task_mean_macro_f1=cs.groupby('property').f1.mean().mean(),
  parsed_response_numeric_only_n=int(g.numeric_only.sum()))

def group_masks(m):
 yield 'all', np.ones(len(m),dtype=bool)
 yield 'secondary_structure',m.question.isin(Q[:4]).to_numpy()
 yield 'physicochemical',m.question.isin(Q[4:]).to_numpy()
 for q in Q:yield SHORT[q],m.question.eq(q).to_numpy()

def boot_acc(m,mask,idx,ids):
 t=m.loc[mask]; n=t.groupby('protein_name').size().reindex(ids,fill_value=0).to_numpy()
 ft=t.groupby('protein_name').semantic_correct_ft.sum().reindex(ids,fill_value=0).to_numpy()
 zs=t.groupby('protein_name').semantic_correct_zs.sum().reindex(ids,fill_value=0).to_numpy()
 den=n[idx].sum(1); valid=den>0
 ds=(ft[idx].sum(1)[valid]-zs[idx].sum(1)[valid])/den[valid]
 d=(ft.sum()-zs.sum())/n.sum() if n.sum() else np.nan
 lo,hi=np.quantile(ds,[.025,.975]) if len(ds) else (np.nan,np.nan)
 return dict(n_qa=int(n.sum()),n_proteins=int((n>0).sum()),ft_accuracy=ft.sum()/n.sum() if n.sum() else np.nan,
  zs_accuracy=zs.sum()/n.sum() if n.sum() else np.nan,difference_pp=d*100,ci95_lower_pp=lo*100,ci95_upper_pp=hi*100,valid_replicates=len(ds))

def boot_class(m,q,idx,ids,which,common=False):
 t=m[m.question.eq(q)].set_index('protein_name').reindex(ids)
 eligible=(t.label_ft.notna()&t.label_zs.notna()).to_numpy() if common else np.ones(len(t),bool)
 stats=[]
 for model in ['ft','zs']:
  recalls=[];f1s=[]
  for c in LABELS[q]:
   truth=t.gold_label_ft.eq(c).to_numpy()&eligible; guess=t['label_'+model].eq(c).to_numpy()&eligible
   if not truth.any():continue
   s=truth[idx].sum(1);p=guess[idx].sum(1);tp=(truth&guess)[idx].sum(1)
   recalls.append(np.divide(tp,s,out=np.full(len(s),np.nan),where=s>0))
   f1s.append(np.divide(2*tp,s+p,out=np.full(len(s),np.nan),where=s>0))
  stats.append(np.nanmean(recalls if which=='balanced_accuracy' else f1s,axis=0))
 return stats[0]-stats[1]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);a=ap.parse_args();src=a.source
 out=ROOT/'results';out.mkdir(exist_ok=True)
 freeze=json.loads((out/'extraction_freeze.json').read_text())
 for name,h in freeze.items():
  p=ROOT/name
  assert hashlib.sha256(p.read_bytes()).hexdigest()==h, f'Extraction changed after freeze: {name}'
 extraction=pd.read_csv(out/'frozen_extraction.csv',keep_default_na=False).set_index('response_key')
 frames={};checks=[];manifest=[];summary=[];per=[];classes=[]
 for profile in PROFILES:
  split=pd.read_csv(src/'data/splits'/f'{profile}_test_ids.csv',dtype=str)
  assert split.protein_name.nunique()==EXPECTED[profile] and not split.protein_name.duplicated().any()
  for model in ['zero_shot','fine_tuned']:
   path=src/'data/evaluations'/f'{profile}_{model}.csv';b=path.read_bytes()
   d=pd.read_csv(path,dtype=str,keep_default_na=False)
   assert set(d.columns)=={'protein_name','question','gold','pred'}
   assert len(d)==EXPECTED[profile]*7 and d.protein_name.nunique()==EXPECTED[profile]
   assert not d.duplicated(['protein_name','question']).any()
   assert not d.eq('').any().any()
   assert set(d.question)==set(Q)
   assert d.groupby('protein_name').question.nunique().eq(7).all()
   assert set(d.protein_name)==set(split.protein_name)
   d['response_key']=[key(q,p) for q,p in zip(d.question,d.pred)]
   assert set(d.response_key)<=set(extraction.index)
   d=d.merge(extraction[['label','status','rule','evidence','numeric_only','review_id']],left_on='response_key',right_index=True,validate='many_to_one')
   d['label']=d.label.replace('',None)
   d['numeric_only']=d.numeric_only.astype(str).str.lower().eq('true')
   d['strict_label']=[strict(p,q) for p,q in zip(d.pred,d.question)]
   d['gold_label']=[strict(p,q) for p,q in zip(d.gold,d.question)]
   assert d.gold_label.notna().all()
   d['strict_correct']=d.strict_label.eq(d.gold_label)
   d['semantic_correct']=d.label.eq(d.gold_label)
   assert d.loc[d.strict_label.notna(),'label'].eq(d.loc[d.strict_label.notna(),'strict_label']).all()
   frames[profile,model]=d
   d.assign(profile=profile,model=model).to_csv(out/f'{profile}_{model}_annotated.csv',index=False)
   summary.append(dict(profile=profile,model=model,**metric_row(d)))
   for q,t in d.groupby('question',sort=False):
    mr=metric_row(t);mr['majority_reference']=t.gold_label.value_counts(normalize=True).max()
    mr['represented_classes']=t.gold_label.nunique()
    per.append(dict(profile=profile,model=model,property=SHORT[q],question=q,**mr))
   for mode,column in [('strict','strict_label'),('semantic','label')]:
    classes.append(class_stats(d,column).assign(profile=profile,model=model,scoring=mode))
   h=hashlib.sha256(b).hexdigest();blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
   manifest.append(dict(path=str(path.relative_to(src)),bytes=len(b),sha256=h,git_blob_sha1=blob))
   checks.append(dict(profile=profile,model=model,rows=len(d),proteins=d.protein_name.nunique(),questions_per_protein=7,duplicate_keys=0,empty_cells=0,split_ids_match=True,gold_valid=True,source_sha256=h))
 s=pd.DataFrame(summary);pt=pd.DataFrame(per);cl=pd.concat(classes,ignore_index=True)
 # Independent reproduction against repository's original published tables.
 original=pd.read_csv(src/'results/six_run_summary.csv')
 compare=s.merge(original,on=['profile','model'],suffixes=('_new','_archived'),validate='one_to_one')
 assert np.allclose(compare.strict_accuracy,compare.accuracy,atol=1e-14,rtol=0)
 assert np.allclose(compare.format_compliance_new,compare.format_compliance_archived,atol=1e-14,rtol=0)
 assert (compare.strict_correct==compare.correct).all()
 original_task=pd.read_csv(src/'results/six_run_per_task.csv')
 tc=pt.merge(original_task,on=['profile','model','question'],suffixes=('_new','_archived'),validate='one_to_one')
 assert len(tc)==42 and np.allclose(tc.strict_accuracy,tc.accuracy,atol=1e-14,rtol=0)
 assert np.allclose(tc.format_compliance_new,tc.format_compliance_archived,atol=1e-14,rtol=0)
 s.to_csv(out/'six_run_metrics.csv',index=False);pt.to_csv(out/'per_property_metrics.csv',index=False)
 cl.to_csv(out/'per_class_metrics.csv',index=False);pd.DataFrame(checks).to_csv(out/'completeness.csv',index=False)
 compare.to_csv(out/'strict_reproduction_comparison.csv',index=False)
 tc.to_csv(out/'strict_per_property_comparison.csv',index=False)
 (out/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 boots=[];decomp=[];classboots=[];sens=[];pairchecks=[];conditional=[];boundboots=[]
 for profile in PROFILES:
  ft,zs=frames[profile,'fine_tuned'],frames[profile,'zero_shot']
  m=ft.merge(zs,on=['protein_name','question'],suffixes=('_ft','_zs'),validate='one_to_one')
  assert len(m)==len(ft)==len(zs) and m.gold_label_ft.eq(m.gold_label_zs).all()
  ids=sorted(m.protein_name.unique());rng=np.random.default_rng(SEED+PROFILES.index(profile))
  idx=rng.integers(0,len(ids),size=(REPS,len(ids)))
  pairchecks.append(dict(profile=profile,paired_rows=len(m),matching_gold=True,missing_keys=0))
  for group,mask in group_masks(m):
   for subset,extra in [('all_responses',np.ones(len(m),bool)),('both_semantically_parsed',m.label_ft.notna()&m.label_zs.notna()),('zero_shot_strict_compliant',m.strict_label_zs.notna())]:
    boots.append(dict(profile=profile,group=group,subset=subset,**boot_acc(m,mask&extra,idx,ids),replicates=REPS,seed=SEED+PROFILES.index(profile)))
   t=m.loc[mask]; both=t.label_ft.notna()&t.label_zs.notna(); fu=t.label_ft.isna();zu=t.label_zs.isna()
   gain=int((both & t.semantic_correct_ft & ~t.semantic_correct_zs).sum())
   loss=int((both & ~t.semantic_correct_ft & t.semantic_correct_zs).sum())
   resolved=int((zu&t.semantic_correct_ft).sum());lost=int((fu&t.semantic_correct_zs).sum())
   actual=int(t.semantic_correct_ft.sum()-t.semantic_correct_zs.sum())
   assert actual==gain-loss+resolved-lost
   decomp.append(dict(profile=profile,group=group,n=len(t),both_parsed_n=int(both.sum()),wrong_to_correct=gain,correct_to_wrong=loss,
    net_classification_gain_pp=100*(gain-loss)/len(t),zero_unresolved_ft_correct=resolved,ft_unresolved_zero_correct=lost,
    net_coverage_contribution_pp=100*(resolved-lost)/len(t),semantic_gain_pp=100*actual/len(t),
    zs_unresolved=int(zu.sum()),ft_unresolved=int(fu.sum()),
    unidentified_gain_lower_pp=100*(actual-zu.sum())/len(t),unidentified_gain_upper_pp=100*(actual+fu.sum())/len(t)))
   # Deliberately give every unresolved zero-shot response a correct answer,
   # while every unresolved FT response remains wrong. This is a sensitivity
   # bound, not an imputation used in the primary score.
   mt=m.copy();mt['semantic_correct_zs']=mt.semantic_correct_zs|mt.label_zs.isna()
   boundboots.append(dict(profile=profile,group=group,**boot_acc(mt,mask,idx,ids)))
  for q in Q:
   for common in [False,True]:
    subset='both_semantically_parsed' if common else 'all_responses'
    tt=m[m.question.eq(q)]
    if common:tt=tt[tt.label_ft.notna()&tt.label_zs.notna()]
    point={}
    for model in ['ft','zs']:
     tt2=tt[['question','gold_label_'+model,'label_'+model]].rename(columns={'gold_label_'+model:'gold_label','label_'+model:'label'})
     c=class_stats(tt2,'label');point[model]=dict(balanced_accuracy=c.recall.mean(),macro_f1=c.f1.mean())
     conditional.append(dict(profile=profile,property=SHORT[q],subset=subset,model=model,n=len(tt),**point[model]))
    for which in ['balanced_accuracy','macro_f1']:
     dist=boot_class(m,q,idx,ids,which,common);lo,hi=np.quantile(dist,[.025,.975])
     classboots.append(dict(profile=profile,property=SHORT[q],subset=subset,metric=which,difference_pp=100*(point['ft'][which]-point['zs'][which]),ci95_lower_pp=100*lo,ci95_upper_pp=100*hi,replicates=REPS,seed=SEED+PROFILES.index(profile)))
  for model,d in [('zero_shot',zs),('fine_tuned',ft)]:
   for policy,mask in [('primary',np.ones(len(d),bool)),('no_numeric_only',~d.numeric_only),('automated_no_adjudication',np.ones(len(d),bool)),('explicit_answers_only',d.rule.str.contains('strict_label|explicit_answer'))]:
    labels=d.label.copy()
    if policy=='automated_no_adjudication':labels=d.response_key.map(extraction.automated_label).replace('',None)
    labels=labels.where(mask)
    sens.append(dict(profile=profile,model=model,policy=policy,accuracy=labels.eq(d.gold_label).mean(),coverage=labels.notna().mean()))
 pd.DataFrame(boots).to_csv(out/'paired_protein_bootstrap.csv',index=False)
 pd.DataFrame(classboots).to_csv(out/'class_aware_bootstrap.csv',index=False)
 pd.DataFrame(conditional).to_csv(out/'conditional_class_aware_metrics.csv',index=False)
 pd.DataFrame(boundboots).to_csv(out/'unresolved_best_case_sensitivity_bootstrap.csv',index=False)
 pd.DataFrame(decomp).to_csv(out/'gain_decomposition.csv',index=False)
 pd.DataFrame(sens).to_csv(out/'sensitivity.csv',index=False)
 pd.DataFrame(pairchecks).to_csv(out/'pair_checks.csv',index=False)
 # Cross-profile overlap is descriptive; never pool these as independent runs.
 overlaps=[]
 for i,p in enumerate(PROFILES):
  for r in PROFILES[i+1:]:
   x=frames[p,'zero_shot'];y=frames[r,'zero_shot'];m=x.merge(y,on=['protein_name','question'],suffixes=('_a','_b'))
   overlaps.append(dict(profile_a=p,profile_b=r,shared_protein_ids=len(set(x.protein_name)&set(y.protein_name)),shared_qa=len(m),identical_responses=int(m.pred_a.eq(m.pred_b).sum()),identical_gold=int(m.gold_a.eq(m.gold_b).sum())))
 pd.DataFrame(overlaps).to_csv(out/'cross_profile_overlap.csv',index=False)
 # Explicit confusion counts include unresolved as prediction outcome.
 cc=[]
 for (p,model),d in frames.items():
  for (q,gold,pred),n in d.assign(prediction=d.label.fillna('UNRESOLVED')).groupby(['question','gold_label','prediction']).size().items():cc.append(dict(profile=p,model=model,property=SHORT[q],gold=gold,prediction=pred,n=n))
 pd.DataFrame(cc).to_csv(out/'confusion_counts.csv',index=False)
 (out/'execution.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,seed=SEED,replicates=REPS,source_commit='ef4f2945b8673d98b77f8fbfca862175b0c87a3d',evaluation_rows=sum(len(d) for d in frames.values()),unique_question_responses=len(extraction)),indent=2)+'\n')
 print(s[['profile','model','strict_accuracy','format_compliance','semantic_accuracy','semantic_coverage','ambiguous_rate','unparseable_rate']].to_string(index=False))
 print(pd.DataFrame(boots).query('group=="all"').to_string(index=False))
 print(pd.DataFrame(decomp).query('group=="all"').to_string(index=False))

if __name__=='__main__':main()
