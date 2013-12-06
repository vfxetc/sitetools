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


def get_environ_list(name):
    """Return the split colon-delimited list from an environment variable.

    Returns an empty list if the variable didn't exist.

    """
    packed = os.environ.get(name)
    return packed.split(':') if packed is not None else []

