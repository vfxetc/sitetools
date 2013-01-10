"""Setup Python for Western X.

Variables previously frozen via :func:`sitecustomize.environ.freeze` will be
restored.

All directories listed within :envvar:`KS_PYTHON_SITES` and the directory
from which this was imported from will be added to :data:`sys.path`, in a
similar manner as site-packages via :func:`python:site.addsitedir`. We
reimplemented that functionality because:

1. Our NFS was throwing some wierd errors with :func:`site.addsitedir` (due to ``._*`` files).
2. We added ``__site__.pth`` files to packages to allow them to describe themselves
   and keep their ``.pth`` file in their own repository.

Also monkey-patch :func:`os.chflags` to not error on our NFS (by ignoring the
error). This was fixed in Python2.7, but we don't have that luxury.

.. warning:: Be extremely careful while modifying this package and test it very
    thoroughly, since being able to locate any other packages is dependant on it
    running successfully.

"""


import errno
import os
import warnings


# We need to be super careful in this module.
try:
    from .environ import apply_diff as environ_apply_diff
except ImportError, why:
    warnings.warn('Error while importing sitecustomize.environ: %r' % why)
    def environ_apply_diff(*args, **kwargs):
        pass
try:
    from .sites import add_site_dir
except ImportError, why:
    warnings.warn('Error while importing sitecustomize.sites: %r' % why)
    def add_site_dir(*args, **kwargs):
        pass
try:
    from .monkeypatch import patch
except ImportError, why:
    warnings.warn('Error while importing sitecustomize.monkeypatch: %r' % why)
    def patch(*args, **kwargs):
        return lambda *a, **kw: None


__all__ = ['add_site_dir', 'patch']


# Where do we want to start inserting directories into sys.path? Just before
# this module, of course. So determine where we were imported from.
our_sys_path = os.path.abspath(os.path.join(__file__,
    os.path.pardir,
    os.path.pardir,
))


# Setup the pseudo site-packages.
sites = [x.strip() for x in os.environ.get('KS_PYTHON_SITES', '').split(':') if x]
sites.append(our_sys_path)
for site in sites:
    try:
        add_site_dir(site, before=our_sys_path)
    except Exception, why:
        warnings.warn('Error while adding site-package %r: %r' % (site, why))


# Restore frozen environment variables.
try:
    environ_apply_diff()
except ImportError, why:
    warnings.warn('Error while running sitecustomize.environ.apply_diff: %r' % why)


# Monkey-patch chflags for Python2.6 since our NFS does not support it and
# Python2.6 does not ignore that lack of support.
# See: http://hg.python.org/cpython/rev/e12efebc3ba6/
@patch(os, 'chflags', max_version=(2, 6))
def os_chflags(func, *args, **kwargs):
    """Monkey-patched to ignore "Not Supported" errors for our NFS."""
    
    # Some OSes don't have the function, so screw it.
    if not func:
        return
    
    try:
        return func(*args, **kwargs)
    except OSError, why:
        
        # Ignore "Not Supported" errors.
        for err in 'EOPNOTSUPP', 'ENOTSUP':
            if hasattr(errno, err) and why.errno == getattr(errno, err):
                return
        
        # Must hardcode the errno because my version has no constant.
        if why.errno == 45:
            return
        
        # This must be an important error.
        raise




