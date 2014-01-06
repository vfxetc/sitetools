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
        self.assertRaises(ValueError, Site, os.path.join(sys.prefix, 'bin', 'pip'))

    def test_not_in_venv(self):
        self.assertRaises(ValueError, Site, '/etc/hosts')


