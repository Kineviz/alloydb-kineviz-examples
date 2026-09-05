from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock,patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from demo import preflight,owned,connect


class SafetyTests(unittest.TestCase):
    def test_old_alloydb_is_rejected(self):
        conn=MagicMock()
        conn.execute.return_value.fetchone.return_value=(160008,)
        with self.assertRaisesRegex(ValueError,'PostgreSQL 19'):
            preflight(conn)

    def test_existing_unowned_schema_is_rejected(self):
        conn=MagicMock()
        conn.execute.return_value.fetchone.side_effect=[(1,),('other application',)]
        with self.assertRaisesRegex(ValueError,'not owned'):
            owned(conn,'paysim_demo',create=True)
        self.assertEqual(conn.execute.call_count,2)

    def test_insecure_remote_connection_is_rejected(self):
        with patch('demo.load_dotenv'),patch.dict('os.environ',{'PGDATABASE':'example','PGHOST':'remote.example','PGSSLMODE':'prefer'},clear=True):
            with self.assertRaisesRegex(ValueError,'verify-full'):
                connect()


if __name__=='__main__':
    unittest.main()
