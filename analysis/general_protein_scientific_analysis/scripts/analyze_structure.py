"""New descriptive/conditional analysis. Never invokes the frozen extractor.
Uses previously validated categorical predictions and existing gold labels only.
"""
from pathlib import Path
import json,hashlib,platform
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

ROOT=Path(__file__).resolve().parents[1];I=ROOT/'inputs';O=ROOT/'results';O.mkdir(exist_ok=True)
SEED=20261030;B=20000
Q=['Does this protein contain alpha-helix?','Does this protein contain beta-sheet?','Does this protein contain coil?',
 'Which secondary structure is most prevalent?','Is the protein predicted to be stable (instability index ≤ 40)?',
 'Is the protein hydrophobic (GRAVY > 0)?','Is the protein acidic (pI < 7) or basic (pI > 7)?']
T=['alpha_presence','beta_presence','coil_presence','predominant','stability','hydrophobicity','pI']
STRUCT=['alpha-helix','beta-sheet','coil'];POS={'stability':'yes','hydrophobicity':'yes','pI':'acidic'}

def wilson(k,n):
 if not n:return (np.nan,np.nan)
 z=1.959963984540054;p=k/n;d=1+z*z/n
 c=(p+z*z/(2*n))/d;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return max(0,c-h),min(1,c+h)
def ci(x):return np.quantile(x,[.025,.975]).tolist()
def holm(p):
 p=np.array(p);order=np.argsort(p);out=np.empty(len(p));out[order]=np.minimum(1,np.maximum.accumulate(p[order]*(len(p)-np.arange(len(p)))))
 return out
def metrics(y,p,classes):
 tp=np.array([np.sum((y==c)&(p==c),axis=-1) for c in classes]);s=np.array([np.sum(y==c,axis=-1) for c in classes]);n=np.array([np.sum(p==c,axis=-1) for c in classes])
 rec=np.divide(tp,s,out=np.full(tp.shape,np.nan),where=s>0)
 f1=np.divide(2*tp,s+n,out=np.full(tp.shape,np.nan),where=s>0)
 return dict(accuracy=np.mean(y==p,axis=-1),balanced_accuracy=np.nanmean(rec,axis=0),macro_f1=np.nanmean(f1,axis=0))

def main():
 manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(I.glob('*')) if p.is_file()}
 (O/'input_hashes.json').write_text(json.dumps(manifest,indent=2)+'\n')
 frames={m:pd.read_csv(I/f'general_only_{m}_annotated.csv',keep_default_na=False) for m in ['fine_tuned','zero_shot']}
 for m,d in frames.items():
  assert len(d)==4914 and d.protein_name.nunique()==702 and not d.duplicated(['protein_name','question']).any()
  assert set(d.question)==set(Q)
 a=frames['fine_tuned'];ids=sorted(a.protein_name.unique());gold=a.pivot(index='protein_name',columns='question',values='gold_label').loc[ids,Q];gold.columns=T
 preds={m:d.pivot(index='protein_name',columns='question',values='label').loc[ids,Q].set_axis(T,axis=1) for m,d in frames.items()}
 ztruth=frames['zero_shot'].pivot(index='protein_name',columns='question',values='gold_label').loc[ids,Q].set_axis(T,axis=1)
 assert gold.equals(ztruth);assert all(set(preds['fine_tuned'][t])<=set(gold[t]) for t in T)
 wide=gold.add_prefix('gold_').join(preds['fine_tuned'].add_prefix('ft_')).join(preds['zero_shot'].add_prefix('zs_'))
 wide.to_csv(O/'protein_level_existing_labels.csv',index_label='protein_name')
 old=pd.read_csv(I/'per_property_metrics.csv').query('profile=="general_only" & model=="fine_tuned"').set_index('property')
 rng=np.random.default_rng(SEED);idx=rng.integers(0,702,size=(B,702))
 summary=[]
 for t in T:
  y=gold[t].to_numpy();p=preds['fine_tuned'][t].to_numpy();classes=sorted(set(y));pt=metrics(y,p,classes);dist=metrics(y[idx],p[idx],classes)
  assert np.isclose(pt['accuracy'],old.loc[t,'semantic_accuracy'])
  assert np.isclose(pt['balanced_accuracy'],old.loc[t,'task_mean_balanced_accuracy'])
  assert np.isclose(pt['macro_f1'],old.loc[t,'task_mean_macro_f1'])
  counts=pd.Series(y).value_counts();major=counts.idxmax();minor=counts.idxmin() if len(classes)>1 else None
  nminor=int(counts[minor]) if minor else 0;kminor=int(np.sum((y==minor)&(p==minor))) if minor else 0
  lo,hi=wilson(kminor,nminor);delta=(y==p).astype(float)-(y==major).astype(float)
  dlo,dhi=ci(delta[idx].mean(1));balo,bahi=ci(dist['balanced_accuracy']);aclo,achi=ci(dist['accuracy'])
  summary.append(dict(task=t,n=702,represented_classes=len(classes),accuracy=pt['accuracy'],accuracy_ci_low=aclo,accuracy_ci_high=achi,
   majority_label=major,majority_reference=counts.max()/702,accuracy_above_majority_pp=delta.mean()*100,majority_gain_ci_low_pp=dlo*100,majority_gain_ci_high_pp=dhi*100,
   balanced_accuracy=pt['balanced_accuracy'],ba_ci_low=balo,ba_ci_high=bahi,macro_f1=pt['macro_f1'],minority_label=minor,
   minority_n=nminor,minority_correct=kminor,minority_recall=kminor/nminor if nminor else np.nan,minority_recall_ci_low=lo,minority_recall_ci_high=hi,
   equal_recall_reference=1/len(classes) if len(classes)>1 else np.nan))
 pd.DataFrame(summary).to_csv(O/'scientific_summary.csv',index=False)
 assoc=[];prevalence=[];submetrics=[];recalls=[];confusions=[];conditional=[];contrasts=[]
 structures=gold.predominant.to_numpy();perm_rng=np.random.default_rng(SEED+1)
 for t in ['stability','hydrophobicity','pI']:
  y=gold[t].to_numpy();ft=preds['fine_tuned'][t].to_numpy();classes=sorted(set(y));positive=POS[t]
  tab=pd.crosstab(gold.predominant,gold[t]).reindex(STRUCT)
  chi,pval,dof,expected=chi2_contingency(tab,correction=False);v=np.sqrt(chi/702)
  # Algebraic best accuracy for one constant label per gold structure group.
  # Uses evaluation labels: intentionally optimistic in-sample reference, not a fitted model.
  oracle=tab.max(axis=1).sum()/702
  assoc.append(dict(task=t,chi2=chi,df=dof,p_value=pval,cramers_v=v,minimum_expected_cell=expected.min(),coarse_structure_modal_ceiling=oracle))
  for st in STRUCT:
   mask=structures==st;n=int(mask.sum());yy=y[mask]
   for model,pred in preds.items():
    pp=pred[t].to_numpy()[mask];classes_sub=sorted(set(yy));pt=metrics(yy,pp,classes_sub)
    srng=np.random.default_rng(SEED+100+T.index(t)*3+STRUCT.index(st));ix=srng.integers(0,n,size=(B,n));md=metrics(yy[ix],pp[ix],classes_sub)
    row=dict(task=t,structure=st,n=n,model=model,coverage=np.mean(pp!=''),**pt)
    for k in pt:row[k+'_ci_low'],row[k+'_ci_high']=ci(md[k])
    row['subgroup_majority_reference']=pd.Series(yy).value_counts().max()/n
    submetrics.append(row)
    for c in classes:
     support=int(np.sum(yy==c));tp=int(np.sum((yy==c)&(pp==c)));k=int(np.sum(pp==c));lo,hi=wilson(tp,support)
     recalls.append(dict(task=t,structure=st,model=model,label=c,support=support,true_positive=tp,predicted_count=k,recall=tp/support if support else np.nan,recall_ci_low=lo,recall_ci_high=hi,precision=tp/k if k else np.nan))
     for pc in classes+['']:
      confusions.append(dict(task=t,structure=st,model=model,gold=c,prediction=pc or 'UNRESOLVED',n=int(np.sum((yy==c)&(pp==pc)))))
   pp=ft[mask];g=int(np.sum(yy==positive));k=int(np.sum(pp==positive));gl,gh=wilson(g,n);pl,ph=wilson(k,n)
   delta=(pp==positive).astype(float)-(yy==positive).astype(float);dl,dh=ci(delta[ix].mean(1))
   prevalence.append(dict(task=t,structure=st,n=n,positive_label=positive,gold_positive=g,ft_positive=k,gold_prevalence=g/n,gold_ci_low=gl,gold_ci_high=gh,ft_prevalence=k/n,ft_ci_low=pl,ft_ci_high=ph,ft_minus_gold_prevalence_pp=100*delta.mean(),bias_ci_low_pp=100*dl,bias_ci_high_pp=100*dh))
  # Conditional null: keep gold structure, class support, and prediction counts fixed;
  # randomize which proteins get the predicted positive label within each structure group.
  null=np.zeros(B);mean=0
  for st in STRUCT:
   mask=structures==st;n=int(mask.sum());g=int(np.sum(y[mask]==positive));k=int(np.sum(ft[mask]==positive))
   tp=perm_rng.hypergeometric(g,n-g,k,size=B)
   null+=n-g-k+2*tp;mean+=(g*k+(n-g)*(n-k))/n
  observed=int(np.sum(y==ft));pv=(1+np.sum(null>=observed))/(B+1)
  # Bootstrap effect beyond this conditional independence expectation.
  residual=np.zeros(B)
  for b in range(0,B,250):
   ii=idx[b:b+250];yy=y[ii];pp=ft[ii];st=structures[ii];exp=np.zeros(len(ii))
   for label in STRUCT:
    mask=st==label;n=mask.sum(1);g=((yy==positive)&mask).sum(1);k=((pp==positive)&mask).sum(1)
    exp+=(g*k+(n-g)*(n-k))/n
   residual[b:b+250]=(np.sum(yy==pp,axis=1)-exp)/702
  rl,rh=ci(residual)
  conditional.append(dict(task=t,n=702,observed_correct=observed,observed_accuracy=observed/702,conditional_null_expected_correct=mean,conditional_null_expected_accuracy=mean/702,excess_accuracy_pp=(observed-mean)/702*100,excess_ci_low_pp=rl*100,excess_ci_high_pp=rh*100,permutation_p_one_sided=pv,replicates=B,seed=SEED+1))
  # Gold prevalence contrasts, all three structure pairs with fixed-group bootstrap.
  for i,s1 in enumerate(STRUCT):
   for s2 in STRUCT[i+1:]:
    a=(y[structures==s1]==positive);b=(y[structures==s2]==positive)
    crng=np.random.default_rng(SEED+200+T.index(t)*10+i*3+STRUCT.index(s2))
    dist=a[crng.integers(0,len(a),(B,len(a)))].mean(1)-b[crng.integers(0,len(b),(B,len(b)))].mean(1)
    l,h=ci(dist);contrasts.append(dict(task=t,structure_a=s1,n_a=len(a),structure_b=s2,n_b=len(b),prevalence_difference_pp=100*(a.mean()-b.mean()),ci_low_pp=100*l,ci_high_pp=100*h))
 aa=pd.DataFrame(assoc);aa['p_holm_three_properties']=holm(aa.p_value);aa.to_csv(O/'structure_label_associations.csv',index=False)
 cc=pd.DataFrame(conditional);cc['p_holm_three_properties']=holm(cc.permutation_p_one_sided);cc.to_csv(O/'conditional_prediction_associations.csv',index=False)
 for name,data in [('prevalence_by_structure',prevalence),('subgroup_metrics',submetrics),('subgroup_class_recall',recalls),('subgroup_confusion_counts',confusions),('prevalence_contrasts',contrasts)]:pd.DataFrame(data).to_csv(O/(name+'.csv'),index=False)
 # Retain original paired FT-vs-zero-shot intervals by reference, not recomputation.
 prior=pd.read_csv(I/'paired_protein_bootstrap.csv');prior[prior.profile.eq('general_only')].to_csv(O/'reused_general_paired_intervals.csv',index=False)
 # Verification: all three structure groups reconcile to each entire task.
 rc=pd.DataFrame(recalls)
 for t in POS:
  assert sum(r['n'] for r in prevalence if r['task']==t)==702
  for m in preds:
   assert rc[(rc.task==t)&(rc.model==m)].support.sum()==702
   assert rc[(rc.task==t)&(rc.model==m)].true_positive.sum()==np.sum(gold[t]==preds[m][t])
 for path,h in manifest.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
 (O/'validation.json').write_text(json.dumps(dict(input_hashes_unchanged=True,previous_ft_metrics_matched=True,paired_gold_labels_equal=True,subgroup_counts_reconcile=True,n_proteins=702,n_qa_per_model=4914,structure_groups=gold.predominant.value_counts().to_dict(),bootstrap_replicates=B,seed=SEED,python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__),indent=2)+'\n')
 print(pd.DataFrame(summary).round(4).to_string(index=False));print(aa.to_string(index=False));print(cc.to_string(index=False))

if __name__=='__main__':main()
