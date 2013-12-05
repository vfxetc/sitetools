import os

from setuptools import setup
from setuptools.command.install_lib import install_lib as _install_lib
from setuptools.command.develop import develop as _develop


# We hook the startup sequence via a .pth file in the site-packages folder.
# Any line that starts with "import" is executed, so we piggy back a little
# more code on there to call our hook.

hook_source = '''

try:
    import sitetools._startup
except ImportError:
    pass
except Exception as e:
    import warnings
    warnings.warn('Error while calling sitetools._hook: %r' % e)

'''.strip().replace('   ', '\t')


# The following mixin and classes will install our hook into site-packages.
# The hook was designed so that it will fail relatively gracefully if the
# package is uninstalled, so we don't bother making sure that the hook itself
# is uninstalled.

class install_mixin:

    def run(self):
        self._install_base.run(self)

        print 'Installing sitetools hook'
        hook_path = os.path.join(self.install_dir, 'zzz_sitetools_hook.pth')
        with open(hook_path, 'w') as fh:
            fh.write('import os; exec %r\n' % hook_source)


class install_lib(install_mixin, _install_lib):
    _install_base = _install_lib

class develop(install_mixin, _develop):
    _install_base = _develop



setup(
    
    name='sitetools',
    version='0.1.0',
    description='Customize your Python startup sequence.',
    url='http://github.com/mikeboers/sitetools',
    
    packages=['sitetools'],
    
    author='Mike Boers',
    author_email='sitetools@mikeboers.com',
    license='BSD-3',

    scripts=['scripts/dev'],
    
    cmdclass={
        'install_lib': install_lib,
        'develop': develop,
    },
)
