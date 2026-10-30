"""Independent scalar checks of new scientific calculations and preservation."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib,math
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results';I=ROOT/'inputs'
def read(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
gold={};pred={}
for r in read(R/'protein_level_existing_labels.csv'):
 gold[r['protein_name']]={k[5:]:v for k,v in r.items() if k.startswith('gold_')}
 pred[r['protein_name']]={k[3:]:v for k,v in r.items() if k.startswith('ft_')}
assert len(gold)==702
for r in read(R/'scientific_summary.csv'):
 t=r['task'];labels=Counter(x[t] for x in gold.values());correct=sum(gold[p][t]==pred[p][t] for p in gold)
 assert math.isclose(correct/702,float(r['accuracy']),abs_tol=1e-14)
 assert math.isclose(max(labels.values())/702,float(r['majority_reference']),abs_tol=1e-14)
 assert math.isclose((correct-max(labels.values()))/702*100,float(r['accuracy_above_majority_pp']),abs_tol=1e-12)
for r in read(R/'structure_label_associations.csv'):
 t=r['task'];cells=Counter((x['predominant'],x[t]) for x in gold.values());group=Counter(x['predominant'] for x in gold.values());labels=Counter(x[t] for x in gold.values())
 chi=sum((cells[s,c]-group[s]*labels[c]/702)**2/(group[s]*labels[c]/702) for s in group for c in labels)
 assert math.isclose(chi,float(r['chi2']),abs_tol=1e-10)
 assert math.isclose(sum(max(cells[s,c] for c in labels) for s in group)/702,float(r['coarse_structure_modal_ceiling']),abs_tol=1e-14)
for r in read(R/'conditional_prediction_associations.csv'):
 t=r['task'];positive='acidic' if t=='pI' else 'yes';expected=0
 for s in ['alpha-helix','beta-sheet','coil']:
  ids=[p for p in gold if gold[p]['predominant']==s];n=len(ids);g=sum(gold[p][t]==positive for p in ids);k=sum(pred[p][t]==positive for p in ids)
  expected+=(g*k+(n-g)*(n-k))/n
 assert math.isclose(expected,float(r['conditional_null_expected_correct']),abs_tol=1e-10)
for r in read(R/'subgroup_class_recall.csv'):
 if r['model']!='fine_tuned':continue
 ids=[p for p in gold if gold[p]['predominant']==r['structure'] and gold[p][r['task']]==r['label']]
 assert len(ids)==int(r['support']);assert sum(pred[p][r['task']]==r['label'] for p in ids)==int(r['true_positive'])
for p,h in json.loads((R/'input_hashes.json').read_text()).items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
print('PASS: independent summary/majority counts, chi-square statistics, empirical structure ceilings, conditional expectations, all fine-tuned subgroup recalls, and unchanged inputs.')
