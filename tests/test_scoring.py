import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from strict_labels import normalize_short_label, LABELS
from score_benchmark import evaluate

class TestLabelNormalization(unittest.TestCase):
    def test_punctuation_case(self):
        q='Does this protein contain alpha-helix?'
        self.assertEqual(normalize_short_label(' YES!  ',q),'yes')
        self.assertEqual(normalize_short_label('Yes.',q),'yes')
        self.assertIsNone(normalize_short_label('The answer is Yes.',q))
        self.assertIsNone(normalize_short_label('No, because...',q))
    def test_multiple_categories(self):
        q='Which secondary structure is most prevalent?'
        self.assertEqual(normalize_short_label('beta-sheet.',q),'beta-sheet')
        self.assertIsNone(normalize_short_label('a beta-sheet',q))
    def test_duplicate_detection(self):
        q='Does this protein contain coil?'
        df=pd.DataFrame([{'protein_name':'A','question':q,'gold':'Yes','pred':'Yes'},
                         {'protein_name':'A','question':q,'gold':'Yes','pred':'No'}])
        with self.assertRaises(ValueError):evaluate(df,'synthetic')
    def test_unknown_label(self):
        q='Does this protein contain coil?'
        df=pd.DataFrame([{'protein_name':'A','question':q,'gold':'Yes','pred':'Yes.'}])
        d=evaluate(df,'synthetic')
        self.assertEqual(int(d.categorical_correct.sum()),1)

if __name__=='__main__':unittest.main()
