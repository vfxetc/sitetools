import os
import pwd
import re
import sys


if hasattr(sys, 'flags') and sys.flags.verbose:

    def verbose(msg, *args, **kwargs):
        if kwargs:
            print msg % kwargs
        elif args:
            print msg % args
        else:
            print msg

else:

    def verbose(*args, **kwargs):
        pass


def expand_user(path, user=None):
    """Roughly the same as os.path.expanduser, but you can pass a default user."""

    def _replace(m):
        m_user = m.group(1) or user
        return pwd.getpwnam(m_user).pw_dir if m_user else pwd.getpwuid(os.getuid()).pw_dir

    return re.sub(r'~(\w*)', _replace, path)


def unique_list(input_, key=lambda x:x):
    """Return the unique elements from the input, in order."""
    seen = set()
    output = []
    for x in input_:
        keyx = key(x)
        if keyx not in seen:
            seen.add(keyx)
            output.append(x)
    return output


def get_environ_list(name, default=None):
    """Return the split colon-delimited list from an environment variable.

    Returns an empty list if the variable didn't exist.

    """
    packed = os.environ.get(name)
    if packed is not None:
        return packed.split(':')
    elif default is not None:
        return default
    else:
        return []


CSI = '\x1b['
_colours = dict(
    black=0,
    red=1,
    green=2,
    yellow=3,
    blue=4,
    magenta=5,
    cyan=7,
    white=7,
)


def colour(message, fg=None, bg=None, bright=False, reset=False):
    parts = []
    if fg is not None:
        parts.extend((CSI, '3', str(_colours[fg]), 'm'))
    if bg is not None:
        parts.extend((CSI, '4', str(_colours[bg]), 'm'))
    if bright:
        parts.extend((CSI, '1m'))
    parts.append(message)
    if reset:
        parts.extend((CSI, '0m'))
    return ''.join(parts)
