from pathlib import Path
import sys
import unittest
from unittest.mock import MagicMock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import launch

class RestartTests(unittest.TestCase):
    def test_preserves_schema_and_checks_ownership_before_delete(self):
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = ('paysim_demo.graphnode',)
        with patch('demo.connect') as connect, patch('demo.generate'), \
             patch('demo.preflight'), patch('demo.owned') as owned, \
             patch('demo.setup') as setup, patch('demo.verify') as verify, patch('builtins.print'):
            connect.return_value.__enter__.return_value = conn
            launch.restart_transactions()
            owned.assert_called_once_with(conn, 'paysim_demo', create=True)
            statements = [c.args[0] for c in conn.execute.call_args_list]
            self.assertFalse(any('DROP' in q or 'TRUNCATE' in q for q in statements))
            deletes = [q for q in statements if q.startswith('DELETE')]
            self.assertEqual(len(deletes), 2)
            self.assertTrue(all("label='transaction'" in q for q in deletes))
            setup.assert_called_once_with(conn, 'paysim-schemaless', True)
            verify.assert_called_once_with(conn, 'paysim-schemaless', True)

    def test_unowned_schema_prevents_deletion(self):
        with patch('demo.connect') as connect, patch('demo.generate'), \
             patch('demo.preflight'), patch('demo.owned', side_effect=ValueError('unowned')):
            with self.assertRaisesRegex(ValueError, 'unowned'):
                launch.restart_transactions()
            connect.return_value.__enter__.return_value.execute.assert_not_called()

    def test_restart_is_opt_in(self):
        with patch.object(sys, 'argv', ['gxr', 'replay']), \
             patch.object(sys, 'prefix', str(launch.ROOT / '.venv')), \
             patch('launch.runtime'), patch('launch.run'), \
             patch('launch.restart_transactions') as restart:
            launch.main()
            restart.assert_not_called()
