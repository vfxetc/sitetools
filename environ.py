import os
import json
import sys


VARIABLE_NAME = 'KS_PYTHON_ENVIRON_DIFF'

_dumps = json.dumps
_loads = json.loads


def _existing_diff(environ):
    blob = environ.get(VARIABLE_NAME)
    return _loads(blob) if blob else {}

def freeze(environ, names):
    """Flag the given names to reset to their current value in the next Python.
    
    :param dict environ: The environment that will be passed to the next Python.
    :param names: A list of variable names that should be reset to their current
        value (as in ``environ``) when the next sub-Python starts.
    
    This is useful to reset environment variables that are set by wrapper
    scripts that are nessesary to bootstrap the process, but we do not want to
    carry into any subprocess. E.g. ``LD_LIBRARY_PATH``.
    
    """
    diff = _existing_diff(environ)
    for name in names:
        diff[name] = environ.get(name)
    environ[VARIABLE_NAME] = _dumps(diff)
    
def apply_diff():
    blob = os.environ.pop(VARIABLE_NAME, None)
    diff = _loads(blob) if blob else {}
    for k, v in diff.iteritems():
        if sys.flags.verbose:
            print '# %s.apply_diff(...): %r -> %r' % (__name__, k, v)
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v