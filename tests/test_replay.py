import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'streaming'))
from replay import graph_rows


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.out=Path(cls.temp.name)
        subprocess.run([sys.executable,str(ROOT/'vendor/paysim.py'),'--out',str(cls.out)],check=True,stdout=subprocess.DEVNULL)
        with (cls.out/'transactions.csv').open(newline='') as f:
            cls.rows=list(csv.DictReader(f))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_replay_matches_every_batch_transaction_and_edge(self):
        with (self.out/'GraphNode.csv').open(newline='') as f:
            expected={r[0]:(r[1],json.loads(r[2])) for r in csv.reader(f) if r[1]=='transaction'}
        with (self.out/'GraphEdge.csv').open(newline='') as f:
            edges={tuple(r[:4]):json.loads(r[4]) for r in csv.reader(f) if r[3] in {'performs','to_client','to_merchant','to_bank'}}
        self.assertEqual(len(self.rows),12033)
        for row in self.rows:
            n,ee=graph_rows(row)
            self.assertEqual((n[1],n[2]),expected[n[0]])
            for e in ee:
                self.assertEqual(e[4],edges[tuple(e[:4])])
        self.assertEqual(len(edges),2*len(self.rows))

    def test_rejects_bad_values_before_load(self):
        for field,value in [('amount','NaN'),('amount','-1'),('receiver_type','unknown'),('global_step','0'),('is_fraud','yes'),('ts','yesterday')]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                graph_rows(dict(self.rows[0],**{field:value}))

    def test_stable_keys(self):
        self.assertEqual(graph_rows(self.rows[0]),graph_rows(self.rows[0]))


if __name__=='__main__':
    unittest.main()
