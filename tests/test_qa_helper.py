import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_qa_from_properties import build,QUESTIONS
class QATests(unittest.TestCase):
 def test_thresholds_and_ties(self):
  example=dict(alpha_frac=.5,beta_frac=.5,coil_frac=0,instability_index=40,gravy=0,isoelectric_point=7)
  labels=build(example)
  self.assertEqual(len(labels),7)
  self.assertEqual(labels,['Yes','Yes','No','alpha-helix','Yes','No','Neutral'])
if __name__=='__main__':unittest.main()
