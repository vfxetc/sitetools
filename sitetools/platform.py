from __future__ import absolute_import

import platform
import sys
from distutils.util import get_platform


# This is the same as distutils uses.
basic_platform_spec = '%s-%s' % (get_platform(), sys.version[:3])

# extended_platform_spec is a little more platform specific as it allows us to isolate
# the different versions of Fedora we use.
_, _, _, _, machine, _ = platform.uname()
if sys.platform == 'darwin':
    osx_v, _, _ = platform.mac_ver()
    extended_platform_spec = 'macosx-%s-%s-%s' % ('.'.join(osx_v.split('.')[:2]), machine, sys.version[:3])
elif sys.platform.startswith('linux'):
    name, version, nick = platform.linux_distribution()
    extended_platform_spec = '%s-%s-%s-%s' % (name.lower(), version, machine, sys.version[:3])
else:
    extended_platform_spec = basic_platform_spec

