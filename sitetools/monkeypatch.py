from __future__ import absolute_import

import logging
import os
import errno
import sys
import warnings

try:
    from metatools.monkeypatch import patch
except ImportError:
    warnings.warn('cannot monkeypatch without metatools')
    patch = None


def _setup():

    if not patch:
        return
    
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


    # Do not use linecache to get the source line if the filename does not
    # appear to be Python source.
    @patch(warnings)
    def formatwarning(func, message, category, filename, lineno, line=None):
        if filename and os.path.splitext(filename)[1] not in ('.py', ):
            line = ''
        if sys.version_info > (2, 6):
            return func(message, category, filename, lineno, line=line).rstrip()
        else:
            return func(message, category, filename, lineno).rstrip()

