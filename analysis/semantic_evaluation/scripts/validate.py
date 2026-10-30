"""Independent CSV-based checks of source hashes and primary results."""
import csv,hashlib,json,math,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results';S=ROOT.parents[1]
def rows(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def norm(s):return re.sub(r'[\s.!?;,。！？；，]+$','',s.strip().lower()).strip()
audit=[]
manifest=json.loads((R/'source_manifest.json').read_text())
for f in manifest:
 b=(S/f['path']).read_bytes()
 assert hashlib.sha256(b).hexdigest()==f['sha256']
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['git_blob_sha1']
for summary in rows(R/'six_run_metrics.csv'):
 p=summary['profile'];model=summary['model'];d=rows(R/f'{p}_{model}_annotated.csv')
 source=rows(S/'data/evaluations'/f'{p}_{model}.csv')
 assert len(d)==len(source)==int(summary['n'])
 assert len({(r['protein_name'],r['question']) for r in source})==len(source)
 nstrict=sum(norm(r['pred'])==norm(r['gold']) for r in source)
 nsemantic=sum(r['label']==norm(r['gold']) for r in d)
 assert nstrict==int(summary['strict_correct'])
 assert nsemantic==int(summary['semantic_correct'])
 assert math.isclose(nsemantic/len(d),float(summary['semantic_accuracy']),abs_tol=1e-14)
 assert sum(r['status'] in ['ambiguous','unparseable'] for r in d)+sum(bool(r['label']) for r in d)==len(d)
 a=Counter(r['protein_name'] for r in source);assert set(a.values())=={7}
 for original,annotated in zip(source,d):
  assert all(original[k]==annotated[k] for k in ['protein_name','question','pred','gold'])
 audit.append(dict(profile=p,model=model,source_hash='PASS',row_alignment='PASS',independent_strict='PASS',independent_semantic='PASS',status_partition='PASS'))
for d in rows(R/'gain_decomposition.csv'):
 assert math.isclose(float(d['net_classification_gain_pp'])+float(d['net_coverage_contribution_pp']),float(d['semantic_gain_pp']),abs_tol=1e-10)
for d in rows(R/'paired_protein_bootstrap.csv'):
 if int(d['n_qa'])==0:
  assert d['ci95_lower_pp']==d['ci95_upper_pp']=='';continue
 assert float(d['ci95_lower_pp'])<=float(d['difference_pp'])<=float(d['ci95_upper_pp'])
with (R/'independent_validation.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(audit[0]));w.writeheader();w.writerows(audit)
print('PASS: six source hashes, all row alignments, independent strict/semantic counts, complete seven-QA blocks, decompositions and interval ordering.')
