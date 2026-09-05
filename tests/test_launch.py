from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import launch


class LaunchTests(unittest.TestCase):
    def invoke(self, arguments):
        with patch.object(sys, 'argv', ['gxr', *arguments]), \
             patch.object(sys, 'prefix', str(launch.ROOT / '.venv')), \
             patch('launch.runtime'), patch('launch.local_database') as database, \
             patch('launch.run') as run, patch('builtins.print'):
            launch.main()
            return database, run

    def test_default_start_verifies_before_reader(self):
        database, run = self.invoke(['start'])
        database.assert_called_once()
        calls = run.call_args_list
        self.assertEqual(calls[0].args[2:], ('up', 'paysim-schemaless'))
        self.assertEqual(calls[1].args[1].name, 'create_reader.py')
        self.assertEqual(calls[2].args[1].name, 'check_reader.py')

    def test_all_demos(self):
        _, run = self.invoke(['start', 'all'])
        self.assertEqual([c.args[3] for c in run.call_args_list[:3]], list(launch.DEMOS))

    def test_invalid_mode_has_no_side_effects(self):
        with self.assertRaises(SystemExit):
            self.invoke(['start', 'all', '--entities-only'])

    def test_failed_setup_does_not_grant_reader(self):
        with patch.object(sys, 'argv', ['gxr', 'start']), \
             patch.object(sys, 'prefix', str(launch.ROOT / '.venv')), \
             patch('launch.runtime'), patch('launch.local_database'), \
             patch('launch.run', side_effect=ValueError('load failed')) as run:
            with self.assertRaisesRegex(ValueError, 'load failed'):
                launch.main()
            self.assertEqual(run.call_count, 1)

    def test_stop_preserves_volumes(self):
        _, run = self.invoke(['stop'])
        self.assertEqual(run.call_args_list[0].args, ('docker', 'compose', 'stop'))
        self.assertEqual(run.call_args_list[1].args[-1], 'stop')

    def test_replay_kafka_prepares_broker(self):
        _, run = self.invoke(['replay', '--via', 'kafka', '--seconds', '0'])
        self.assertIn('pip', run.call_args_list[0].args)
        self.assertEqual(run.call_args_list[1].args[-3:], ('up', '-d', '--wait'))
        self.assertEqual(run.call_args_list[2].args[-4:], ('--via', 'kafka', '--seconds', '0.0'))

    def test_remote_settings_rejected_before_docker(self):
        with patch('dotenv.dotenv_values', return_value={'PGHOST': 'remote.example'}), \
             patch('launch.run') as run, patch('pathlib.Path.exists', return_value=True):
            with self.assertRaisesRegex(ValueError, 'default local'):
                launch.local_database()
            run.assert_not_called()

    def test_database_creation_only_when_missing(self):
        config = dict(PGHOST='127.0.0.1', PGPORT='55432', PGDATABASE='kineviz_demo',
                      PGUSER='postgres', PGSSLMODE='disable',
                      PGPASSWORD='test-placeholder', POSTGRES_PASSWORD='test-placeholder')
        for exists in (None, (1,)):
            with self.subTest(exists=exists), \
                 patch('dotenv.dotenv_values', return_value=config), \
                 patch.dict('os.environ', {}, clear=True), \
                 patch('pathlib.Path.exists', return_value=True), \
                 patch('launch.run'), patch('demo.preflight'), \
                 patch('psycopg.connect') as connect:
                conn = connect.return_value.__enter__.return_value
                conn.execute.return_value.fetchone.return_value = exists
                launch.local_database()
                self.assertEqual(conn.execute.call_count, 1 if exists else 2)


if __name__ == '__main__':
    unittest.main()
