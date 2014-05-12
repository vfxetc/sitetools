import os
import sys

from . import *

from sitetools.sites import Site


class TestSite(TestCase):

    def test_directory(self):
        site = Site(os.path.dirname(__file__))
        self.assertFalse(site.is_venv)
        self.assertIsNone(site.bin_path)
        self.assertEqual(site.python_path, os.path.dirname(__file__))

    def test_our_executable(self):

        site = Site(sys.executable)

        self.assertEqual(sys.executable, site.path)
        self.assertTrue(site.is_venv)

        self.assertEqual(os.path.abspath(os.path.join(sys.prefix, 'bin')), site.bin_path)
        self.assertEqual(os.path.abspath(os.path.join(
            sys.prefix,
            'lib',
            'python%s.%s' % sys.version_info[:2],
            'site-packages',
        )), site.python_path)

    def test_non_existant(self):
        self.assertRaises(ValueError, Site, 'does-not-exist')

    def test_not_python_executable(self):
        for name in '2to3', 'idle', 'pydoc':
            path = os.path.join(sys.prefix, 'bin', name)
            if os.path.exists(path):
                self.assertRaises(ValueError, Site, path)
                break
        else:
            self.fail('no executables to test in %s/bin' % sys.prefix)

    def test_not_in_venv(self):
        self.assertRaises(ValueError, Site, '/etc/hosts')


