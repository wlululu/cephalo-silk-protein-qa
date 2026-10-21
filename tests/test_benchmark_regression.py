"""Regression checks for historical benchmark snapshots: CPU only."""
import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from score_benchmark import evaluate

EXPECTED = {
    'spider_only': {'proteins': 217, 'qa': 1519, 'fine_tuned': 1414, 'zero_shot': 635},
    'general_only': {'proteins': 702, 'qa': 4914, 'fine_tuned': 4293, 'zero_shot': 1505},
    'spider_staged': {'proteins': 217, 'qa': 1519, 'fine_tuned': 1435, 'zero_shot': 626},
}

class BenchmarkRegressionTests(unittest.TestCase):
    def test_archived_prediction_counts_and_test_ids(self):
        for profile, exp in EXPECTED.items():
            with self.subTest(profile=profile):
                expected_ids = set(pd.read_csv(ROOT / 'data' / 'splits' / f'{profile}_test_ids.csv').protein_name.astype(str))
                self.assertEqual(len(expected_ids), exp['proteins'])
                for model in ('fine_tuned', 'zero_shot'):
                    frame = evaluate(pd.read_csv(ROOT / 'data' / 'evaluations' / f'{profile}_{model}.csv', dtype={'protein_name':str}), f'{profile}/{model}')
                    self.assertEqual(len(frame), exp['qa'])
                    self.assertEqual(set(frame.protein_name), expected_ids)
                    self.assertEqual(int(frame.categorical_correct.sum()), exp[model])

    def test_zero_shot_fine_tuned_record_pairing(self):
        for profile in EXPECTED:
            with self.subTest(profile=profile):
                frames=[]
                for model in ('zero_shot','fine_tuned'):
                    d=pd.read_csv(ROOT / 'data' / 'evaluations' / f'{profile}_{model}.csv', dtype={'protein_name':str})
                    frames.append(set(zip(d.protein_name,d.question,d.gold)))
                self.assertEqual(frames[0], frames[1])

if __name__ == '__main__':
    unittest.main()
