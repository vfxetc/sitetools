"""Common tasks for setting up a Python execution environment.

Variables previously frozen via :func:`sitecustomize.environ.freeze` will be
restored.

All directories listed within :envvar:`KS_PYTHON_SITES` and the directory
from which this was imported from will be added to :data:`sys.path`, in a
similar manner as site-packages via :func:`python:site.addsitedir`. We
reimplemented that functionality because:

1. Our NFS was throwing some wierd errors with :func:`site.addsitedir` (due to ``._*`` files).
2. We added ``__site__.pth`` files to packages to allow them to describe themselves
   and keep their ``.pth`` file in their own repository.

.. warning:: Be extremely careful while modifying this package and test it very
    thoroughly, since being able to locate any other packages is dependant on it
    running successfully.

"""

import traceback
import warnings


def import_and_call(mod_name, func_name, *args, **kwargs):

    try:
        mod = __import__(mod_name, fromlist=['.'])
    except (ImportError, SyntaxError), e:
        warnings.warn('Error while importing %s to call %s\n%s' % (mod_name, func_name, traceback.format_exc()))
        return

    func = getattr(mod, func_name, None)
    if not func:
        warnings.warn('%s.%s does not exist' % (mod_name, func_name))
        return

    try:
        func(*args, **kwargs)
    except Exception, e:
        warnings.warn('Error while calling %s.%s\n%s' % (mod_name, func_name, traceback.format_exc()))


import_and_call('sitecustomize.sites', '_setup')
import_and_call('sitecustomize.environ', '_setup')


# The public API.
from sitecustomize.sites import add_site_dir

