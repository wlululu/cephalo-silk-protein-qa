"""Run blind parsing and content-keyed adjudications BEFORE evaluating golds."""
from pathlib import Path
import json,hashlib
import pandas as pd
from semantic_labels import extract,key
ROOT=Path(__file__).resolve().parents[1]
x=pd.read_csv(ROOT/'blind_unique_responses.csv')
# IDs are row numbers in the blind unique-response file, not protein IDs.
# These are content-only adjudications; stored hashes are the durable lookup.
decisions={
 233:('alpha-helix','parsed','Yellow is explicitly alpha-helix; yellow is more prevalent than both other colors.'),
 701:('alpha-helix','parsed','Yellow ribbons are alpha-helices; predominant structure is explicitly yellow ribbons.'),
 996:('alpha-helix','parsed','Yellow is alpha-helix and explicitly more prevalent than both alternatives.'),
 335:('no','parsed','Blue maps to alpha-helices; response explicitly says no blue segments.'),
 753:('no','parsed','Blue maps to alpha-helices; response explicitly says no blue regions.'),
 1623:('no','parsed','Blue maps to alpha-helices; response explicitly says no blue segments.'),
 340:('no','parsed','Beta-sheet mapped to red/green regions, both explicitly absent.'),
 708:('no','parsed','Beta-sheet mapped to red/green regions, both explicitly absent.'),
 388:('no','parsed','Blue segments mapped to beta-sheets and explicitly absent.'),
 1373:('no','parsed','Blue regions mapped to beta-sheets and explicitly absent.'),
 352:('yes','parsed','Blue segments described as alpha-helices; absent yellow is a different structure.'),
 581:('yes','parsed','Local image description explicitly maps colored structures to beta-sheet (yellow).'),
 1123:(None,'unparseable','Beta-sheet predominance is only within yellow ribbons; relative size of whole-protein components is unspecified.'),
 1443:(None,'unparseable','Dominance refers to one of three regions; no whole-protein ranking.'),
 784:(None,'ambiguous','Describes two structures but gives absence only for the first; target cannot be uniquely resolved.'),
 786:(None,'ambiguous','Describes two structures; relative prevalence only for the first, not a unique target.'),
}
# The saved policy is authoritative and matched by response content, never by
# row position. The dictionary above documents the original blind review log.
policy={r['response_key']:r for r in json.loads((ROOT/'scripts/adjudication_policy.json').read_text())}
annotations=[];records=[]
for i,r in x.iterrows():
 a=extract(r.question,r.pred); raw=a.copy(); k=key(r.question,r.pred)
 if k in policy:
  item=policy[k];label=item['label'] or None;status=item['status'];reason=item['evidence']
  assert item['question']==r.question and item['pred']==r.pred
  a=dict(label=label,status=status,rule='blind_adjudication',evidence=reason,numeric_only=False)
  annotations.append(dict(review_id=i,response_key=k,question=r.question,pred=r.pred,**a))
 records.append(dict(review_id=i,response_key=k,question=r.question,pred=r.pred,**a,automated_label=raw['label'],automated_status=raw['status']))
pd.DataFrame(annotations).to_csv(ROOT/'results/blind_adjudications.csv',index=False)
pd.DataFrame(records).to_csv(ROOT/'results/frozen_extraction.csv',index=False)
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'scripts/semantic_labels.py',ROOT/'scripts/freeze_extraction.py',ROOT/'scripts/adjudication_policy.json',ROOT/'blind_unique_responses.csv',ROOT/'results/blind_adjudications.csv',ROOT/'results/frozen_extraction.csv']}
(ROOT/'results/extraction_freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(pd.DataFrame(records).groupby(['question','status']).size().to_string())
