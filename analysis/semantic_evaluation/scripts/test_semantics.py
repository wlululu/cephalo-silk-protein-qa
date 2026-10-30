import unittest
from semantic_labels import extract,QUESTIONS as Q

class SemanticTests(unittest.TestCase):
 def check(self,i,text,label,status='parsed'):
  a=extract(Q[i],text);self.assertEqual((a['label'],a['status']),(label,status),a)
 def test_negation(self):
  self.check(4,'The protein is not stable.','no')
  self.check(4,'The protein is not unstable.','yes')
  self.check(5,'The protein is hydrophilic, not hydrophobic.','no')
  self.check(5,'The protein is not hydrophobic.','no')
  self.check(6,'The protein is not acidic.',None,'ambiguous')
 def test_conflicts(self):
  self.check(5,'Yes. The protein is hydrophilic.',None,'ambiguous')
  self.check(4,'The protein is stable. The protein is unstable.',None,'ambiguous')
  self.check(5,'The protein is hydrophobic or hydrophilic.',None,'ambiguous')
  self.check(1,'No. The protein contains beta-sheets.',None,'ambiguous')
 def test_generic_not_prediction(self):
  self.check(6,'Proteins with a pI less than 7 are acidic.',None,'unparseable')
  self.check(4,'An instability index of 40 or less suggests that the protein is stable.',None,'unparseable')
  self.check(4,'The protein is stable if its instability index is below 40.',None,'unparseable')
  self.check(5,'To determine if the protein is hydrophobic, we need the sequence.',None,'unparseable')
 def test_presence_and_scope(self):
  self.check(1,'There are no regions of beta-sheet present in the protein structure.','no')
  self.check(1,'The image does not show any distinct beta-sheet regions.','no')
  self.check(0,'The protein contains alpha-helices but no beta-sheets.','yes')
  self.check(3,'The predominant secondary structure is alpha-helix, depicted by helical coils.','alpha-helix')
  self.check(3,'The predominant structure is alpha-helix or beta-sheet.',None,'ambiguous')
 def test_numeric_and_thresholds(self):
  self.check(5,'The protein has a GRAVY score of 0.0.','no')
  self.check(5,'The protein has a GRAVY score of -0.474.','no')
  self.check(4,'The protein has an instability index of 40.','yes')
  self.check(4,'The protein has an instability index of 41.','no')
  self.check(6,'The protein has a pI of 7.','neutral')
  self.check(6,'The protein has a pI of 8.','basic')
  self.check(6,'The protein has a pI of 8. The protein is acidic.',None,'ambiguous')
 def test_uncertainty(self):
  self.check(4,'I cannot determine stability from the image.',None,'ambiguous')
  self.check(3,'The image shows a protein structure which is',None,'unparseable')

if __name__=='__main__':unittest.main()
