import os

from . import *

from sitetools.environ import freeze, unfreeze


class TestEnvironFreeze(TestCase):

    def test_freeze_for_startup(self):

        env = {'X': '1'}

        freeze(env, ['X'])

        env['X'] = '2'

        self.assertIn('KS_ENVIRON_DIFF', env)
        self.assertEqual(env['X'], '2')

        unfreeze(None, pop=True, environ=env)

        self.assertNotIn('KS_ENVIRON_DIFF', env)
        self.assertEqual(env['X'], '1')

    def test_freeze_for_app_use(self):

        env = {'X': '1'}

        freeze(env, ['X'], 'nuke')

        env['X'] = '2'

        self.assertIn('KS_NUKE_ENVIRON_DIFF', env)
        self.assertEqual(env['X'], '2')

        refreezer_ctx = unfreeze('nuke', environ=env)
        self.assertEqual(env['X'], '1')

        with refreezer_ctx:
            self.assertEqual(env['X'], '1')

        self.assertEqual(env['X'], '2')


