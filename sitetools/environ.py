"""

Since our development environment is controlled completely by passing
environment variables from one process to its children, in generaly allow all
variables to flow freely. There are, however, a few circumstances in which we
need to inhibit this flow.

Maya and Nuke, for example, add to the :envvar:`python:PYTHONHOME`, and our
launchers add to :envvar:`KS_SITES` (for PyQt, etc.). These changes must
not propigate to other processes.

These tools allow us to manage those variables which should not propigate.
Upon Python startup, these tools will reset any variables which have been flagged.


Actual Variables
----------------
.. envvar:: KS_ENVIRON_DIFF

    A set of variables to update (or delete) from Python's :data:`os.environ`
    at startup. This is used to force variables that are nessesary for startup
    to not propigate into the next executable.
    
    .. warning:: Do not use this directly, as the format is subject to change
        without notice. Instead, use :func:`sitecustomize.environ.freeze`.


API Reference
-------------

"""

from __future__ import absolute_import

import contextlib
import json
import logging
import os
import re


log = logging.getLogger(__name__)

VARIABLE_NAME = 'KS_ENVIRON_DIFF'
VARIABLE_PATTERN = 'KS_%s_ENVIRON_DIFF'

_dumps = json.dumps
_loads = json.loads



def _variable_name(label):
    if label:
        return VARIABLE_PATTERN % re.sub(r'\W+', '_', label.upper())
    else:
        return VARIABLE_NAME


def freeze(environ, names, label=None):
    """Flag the given names to reset to their current value in the next Python.
    
    :param dict environ: The environment that will be passed to the next Python.
    :param names: A list of variable names that should be reset to their current
        value (as in ``environ``) when the next sub-Python starts.
    :param str label: A name for this environment freeze; the default of ``None``
        will be unfrozen at startup.
    
    This is useful to reset environment variables that are set by wrapper
    scripts that are nessesary to bootstrap the process, but we do not want to
    carry into any subprocess. E.g. ``LD_LIBRARY_PATH``.

    This may be called multiple times for the same label as it updates any
    existing freezes.
    
    Usage::
    
        import os
        from subprocess import call
        
        from sitecustomize.environ import freeze
        
        env = dict(os.environ)
        env['DEMO'] = 'one'
        freeze(env, ['DEMO'])
        env['DEMO'] = 'two'
        
        call(['python', '-c', 'import os; print os.environ["DEMO"]'], env=env)
        # Prints: one
        
    """
    diff = _get_diff(environ, label)
    for name in names:
        diff[name] = environ.get(name)
    environ[_variable_name(label)] = _dumps(diff)


def _get_diff(environ, label, pop=False):
    """Get previously frozen key-value pairs.

    :param str label: The name for the frozen environment.
    :param bool pop: Destroy the freeze after use; only allow application once.
    :returns: ``dict`` of frozen values.

    """
    if pop:
        blob = environ.pop(_variable_name(label), None)
    else:
        blob = environ.get(_variable_name(label))

    return _loads(blob) if blob else {}


def _apply_diff(environ, diff):
    """Apply a frozen environment.

    :param dict diff: key-value pairs to apply to the environment.
    :returns: A dict of the key-value pairs that are being changed.

    """
    original = {}

    if diff:
        for k, v in diff.iteritems():

            if v is None:
                log.log(5, 'unset %s', k)
            else:
                log.log(5, '%s="%s"', k, v)

            original[k] = environ.get(k)

            if original[k] is None:
                log.log(1, '%s was not set', k)
            else:
                log.log(1, '%s was "%s"', k, original[k])

            if v is None:
                environ.pop(k, None)
            else:
                environ[k] = v
    else:
        log.log(5, 'nothing to apply')

    return original


def unfreeze(label, pop=False, environ=None):
    """Reset the environment to its state before it was frozen by :func:`freeze`.

    :param str label: The name for the frozen environment.
    :param bool pop: Destroy the freeze after use; only allow unfreeze once.
    :param dict environ: The environment to work on; defaults to ``os.environ``.
    :returns: A context manager to re-freeze the environment on exit.

    Usage::

        unfreeze('nuke')

        # or

        with unfreeze('maya'):
            # do something

    """

    environ = os.environ if environ is None else environ
    diff = _get_diff(environ, label, pop=pop)
    original = _apply_diff(environ, diff)
    return _refreezer(environ, diff, original)


@contextlib.contextmanager
def _refreezer(environ, diff, original):
    # The __enter__ action has already been performed by unfreeze.
    try:
        yield
    finally:
        changed = _apply_diff(environ, original)
        if changed != diff:
            log.warning('environ changed during unfreeze context; expected %r got %r' % (original, changed))


def _setup():
    _apply_diff(os.environ, _get_diff(os.environ, None, pop=True))

