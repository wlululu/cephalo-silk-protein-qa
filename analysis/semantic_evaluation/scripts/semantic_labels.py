"""Ground-truth-blind, deterministic extraction of archived categorical answers.

Only (question, response) are accepted. No IDs, profiles, golds, or correctness
enter extraction. Evidence offsets refer to normalized text. See METHODS.md.
"""
import re
import hashlib

QUESTIONS = [
 'Does this protein contain alpha-helix?',
 'Does this protein contain beta-sheet?',
 'Does this protein contain coil?',
 'Which secondary structure is most prevalent?',
 'Is the protein predicted to be stable (instability index ≤ 40)?',
 'Is the protein hydrophobic (GRAVY > 0)?',
 'Is the protein acidic (pI < 7) or basic (pI > 7)?',
]
LABELS = {q: ['yes','no'] for q in QUESTIONS}
LABELS[QUESTIONS[3]]=['alpha-helix','beta-sheet','coil']
LABELS[QUESTIONS[6]]=['acidic','basic','neutral']
PATTERNS = {
 'alpha-helix':r'\balpha[ -]hel(?:ix|ices|ical)(?:es)?\b',
 'beta-sheet':r'\bbeta[ -](?:sheet|strand)s?\b',
 'coil':r'(?<!helical )\b(?:random[ -])?coils?\b',
}

def normalize(text):
 return re.sub(r'\s+',' ',str(text).lower().replace('α','alpha').replace('β','beta').replace('–','-').replace('−','-').replace('’',"'").replace('**','').replace('__','')).strip()

def strict(response, question):
 s=re.sub(r'[\s.!?;,。！？；，]+$','',str(response).strip().lower()).strip()
 return s if s in LABELS[question] else None

def key(question,response):
 return hashlib.sha256((question+'\0'+str(response)).encode()).hexdigest()

def extract(question,response):
 """Return label/status/rule/evidence; never read ground truth."""
 s=normalize(response); direct=strict(response,question)
 if direct is not None:
  return dict(label=direct,status='parsed',rule='strict_label',evidence=s,numeric_only=False)
 task=QUESTIONS.index(question)
 ev=[]
 def add(label,rule,text):
  if label in LABELS[question]:ev.append((label,rule,text))
 # Explicit categorical answer cues: only at start or attached to 'answer'.
 if task not in (3,6):
  for pat in [r'^(yes|no)\b',r'\b(?:final\s+)?answer\s*(?:is\s*)?[:=]?\s*["\x27]?\b(yes|no)\b']:
   for m in re.finditer(pat,s):add(m[1],'explicit_answer',m[0])
 else:
  aliases={**PATTERNS} if task==3 else {x:r'\b'+x+r'\b' for x in LABELS[question]}
  for label,pat in aliases.items():
   for m in re.finditer(r'(?:^|\b(?:final\s+)?answer\s*(?:is\s*)?[:=]?\s*)["\x27]?('+pat+')',s):add(label,'explicit_answer',m[0])

 # Split clauses at sentence boundaries, keeping decimal points intact.
 clauses=re.split(r'(?<!\d)[.!?](?:\s+|$)|(?<=\d)[.!?](?!\d)(?:\s+|$)',s)
 if task in (0,1,2):
  target=PATTERNS[['alpha-helix','beta-sheet','coil'][task]]
  # Negative assertions trump bare color legends, but not explicit positive
  # presence statements. Missing other structures is irrelevant.
  negatives=[];positive=[];legend=[]
  for c in clauses:
   negpat=[r'\b(?:no|without|absence of|lack(?:s|ing)?(?: of)?)\s+(?:(?:visible|distinct|significant|clear|any|evidence of|presence of|regions of)\s+){0,3}'+target,
           r'\b(?:does not|doesn\x27t|do not|not)\s+(?:(?:appear to|seem to|explicitly|clearly)\s+)*(?:show|display|contain|have|include|present|visible)\s+(?:(?:any|significant|distinct|visible|clear|regions that are|predominantly)\s+)*'+target,
           target+r'.{0,30}\b(?:absent|not present|not visible)\b']
   neg=any(re.search(p,c) for p in negpat)
   if neg:negatives.append(c);continue
   if re.search(r'\bno (?:distinct )?(?:regions?|segments?|parts?) (?:colored|in)|\bno (?:blue|yellow|purple|magenta|white|gray|green|red)\b',c):continue
   if not re.search(target,c):continue
   if re.search(r'\b(question asks|if the protein|whether|such as|can be either|commonly used to (?:represent|illustrate)|common method used to (?:represent|illustrate))\b',c):continue
   # Actual local assertions, not textbook definitions of the structure.
   if re.search(r'\b(?:protein|structure|image|diagram|ribbon)\b.{0,75}\b(?:contains?|includes?|has|shows?|with|depicted|composed)\b.{0,100}'+target,c) or re.search(r'\b(?:presence of|regions of|regions are|there are(?: also)?|there is)\b.{0,65}'+target,c):
    positive.append(c)
   elif re.search(r'\b(?:regions?|segments?|ribbons?|arrows?|parts?|structures?|helices|lines)\b.{0,50}\b(?:represent|indicat|are|correspond)',c) or re.search(target+r'.{0,45}(?:colored|shown|highlighted|depicted)',c):legend.append(c)
  for c in negatives:add('no','explicit_absence',c)
  for c in positive:add('yes','explicit_presence',c)
  # A local color assignment supports presence unless explicitly contradicted
  # by absence, a color absence, or an explicit 'no' answer.
  if not negatives and not any(e[0]=='no' for e in ev) and not re.search(r'\bno (?:distinct )?(?:regions?|segments?|parts?) (?:colored|in)|\bno (?:blue|yellow|purple|magenta|white|gray|green)\b',s):
   for c in legend:add('yes','local_structure_description',c)
 elif task==3:
  trigger=r'\b(?:predominant(?:ly)?|most (?:prevalent|abundant|common|prominent)|primarily|mainly|majority|dominant)\b'
  for c in clauses:
   for m in re.finditer(trigger,c):
    # Extract first named class following dominance cue, no wandering into
    # separate sentences or a list of structures; capture preceding class too.
    after=c[m.end():m.end()+100]
    hits=sorted((z.start(),z.end(),label) for label,pat in PATTERNS.items() for z in re.finditer(pat,after))
    if hits:
     a,b,label=hits[0]
     bridge=after[:a]
     if not re.search(r'\b(not|no|without|rather than)\b',c[max(0,m.start()-15):m.end()]+bridge):
      add(label,'dominant_structure',c)
      # Equal alternatives immediately joined by and/or are not a unique class.
      if len(hits)>1 and re.fullmatch(r'\s*(?:and|or|/)\s*',after[b:hits[1][0]]):add(hits[1][2],'conflicting_dominance',c)
    before=c[max(0,m.start()-85):m.start()]
    for label,pat in PATTERNS.items():
     for z in re.finditer(pat,before):
      gap=before[z.end():]
      if re.fullmatch(r'(?:\s+(?:is|are|appears|to|be|the|structure|secondary|in|this|protein|clearly|seems|which|that|and))*\s*',gap) and not re.search(r'\b(?:not|no)\b',gap):add(label,'dominant_structure',c)
 elif task in (4,5,6):
  vocab={4:{'stable':'yes','unstable':'no'},5:{'hydrophobic':'yes','hydrophilic':'no','non-hydrophobic':'no'},6:{'acidic':'acidic','basic':'basic','neutral':'neutral'}}[task]
  for c in clauses:
   # Assertions about THIS protein/it, not conditional definitions or regions.
   for word,label in vocab.items():
    pat=r'\b(?:the protein(?:\x27s (?:overall )?structure)?|this protein|(?:the )?(?:overall )?protein structure|the overall structure|the structure|it)\s+(?:is |appears (?:to be )?|seems (?:to be )?|would be |can be considered |has been predicted to be )(?:(?:predicted|likely|considered|classified|generally|relatively|highly|more|very|thermodynamically|structurally|chemically|to be|as|a)\s+)*(not\s+)?'+re.escape(word)+r'\b'
    for m in re.finditer(pat,c):
     if re.search(r'\b(?:if|whether|to determine|cannot determine|unable to determine)\b',c):continue
     if re.search(r'^(?:an instability index|proteins with|a protein with|for example)\b',c.strip()):continue
     out=label
     if m[1]:
      if task in (4,5):out='no' if label=='yes' else 'yes'
      else:continue # not acidic does not distinguish basic from neutral
     add(out,'property_assertion',m[0])
     rest=c[m.end():]
     for alt,altlabel in vocab.items():
      if re.match(r'\s*(?:and|or|/)\s+'+re.escape(alt)+r'\b',rest):add(altlabel,'conflicting_assertions',c)
   # A full protein described as 'a stable protein' etc.
   for word,label in vocab.items():
    for m in re.finditer(r'\b(?:shows|depicts|is)\s+(?:a|an)\s+'+word+r'\s+protein\b',c):add(label,'property_assertion',m[0])
   # Explicit response-provided scalar; no threshold definition or generic
   # hypothetical scalar becomes a prediction. Do not validate claimed values.
   if task==4:
    prop=r'(?:predicted\s+)?instability index(?: value)?'
   elif task==5:
    prop=r'gravy(?:\s*\([^)]*\))?(?:\s+(?:score|value))?'
   else:
    prop=r'(?:pi(?:\s*\(isoelectric point\))?|isoelectric point(?:\s*\(pi\))?)'
   patterns=[prop+r'\s+(?:(?:of (?:the|this) protein|for (?:the|this) protein)\s+)?(?:of|is|=|:)\s+(?:(?:calculated|predicted|estimated|approximately|about|to be)\s+)*(-?\d+(?:\.\d+)?)']
   for p in patterns:
    for m in re.finditer(p,c):
     prefix=c[:m.start()]
     if re.search(r'\b(?:if|proteins with|a protein with|for example|such as)\b',prefix) or re.match(r'^an\s*$',prefix.strip()):continue
     if re.search(r'\b(?:cannot|can not|not (?:known|visible|provided|shown)|need to)\b',prefix):continue
     # Must be tied to the given image/protein or a direct value declaration.
     if not (re.search(r'\b(?:the protein|this protein|the image|protein\x27s|structure)\b',c) or c.lstrip().startswith(('the gravy','gravy','the instability index','instability index','the pi','pi'))):continue
     val=float(m[1]); label=('yes' if val<=40 else 'no') if task==4 else ('yes' if val>0 else 'no') if task==5 else ('acidic' if val<7 else 'basic' if val>7 else 'neutral')
     add(label,'response_numeric_threshold',m[0])
   if task==5:
    for m in re.finditer(r'\b(?:the protein|it)\s+is\s+(?:considered\s+)?neutral\s+(?:in|with respect to)\s+hydrophobicity',c):add('no','property_assertion',m[0])
    for m in re.finditer(r'\b(?:the protein|this protein|it)\s+has\s+a\s+(positive|negative|zero)\s+gravy(?: score)?',c):add('yes' if m[1]=='positive' else 'no','response_numeric_threshold',m[0])

 labels={e[0] for e in ev}
 if len(labels)>1:
  return dict(label=None,status='ambiguous',rule='conflicting_assertions',evidence=repr(ev),numeric_only=False)
 if len(labels)==1:
  return dict(label=next(iter(labels)),status='parsed',rule='+'.join(sorted({e[1] for e in ev})),evidence=repr(ev),numeric_only=all(e[1]=='response_numeric_threshold' for e in ev))
 # Explicit alternatives or inability to choose are distinguished from no
 # answer. A generic description/definition and abrupt ending are unparseable.
 ambiguity=r'\b(?:cannot|can not|can\x27t|unable to|not possible to|impossible to)\s+(?:be\s+)?(?:determine|tell|conclude|predict|assess)|\b(?:uncertain|unclear|ambiguous|either yes or no)\b'
 if re.search(ambiguity,s):
  return dict(label=None,status='ambiguous',rule='explicit_uncertainty',evidence=s,numeric_only=False)
 if task==6 and re.search(r'\b(?:the protein|it) is not (?:acidic|basic|neutral)\b',s):
  return dict(label=None,status='ambiguous',rule='incomplete_multiclass_negation',evidence=s,numeric_only=False)
 return dict(label=None,status='unparseable',rule='no_task_answer',evidence='',numeric_only=False)
