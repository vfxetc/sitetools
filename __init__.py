"""This package is responsible for setting up :data:`python:sys.path` for Western X.

This adds all the directories listed within :envvar:`KS_PYTHON_SITES`, and the directory
from which this was imported from, in a similar manner as site-packages via
:func:`python:site.addsitedir`.

We have reimplemented that functionality for two reasons:

1. Our NFS was throwing some wierd errors with site.addsitedir.
2. We added ``__site__.pth`` files to packages to allow them to describe themselves
   and keep their ``.pth`` file in their own repository.

"""

import os
import sys


# Where do we want to start inserting directories into sys.path? Just before
# this module, of course.

# Determine where we were loaded from.
_our_sys_path = os.path.abspath(os.path.join(__file__,
    os.path.pardir,
    os.path.pardir,
))

# Determine where we are in the sys.path.
try:
    insert_at = sys.path.index(_our_sys_path)
except ValueError:
    print 'Could not find our entry in sys.path!'
    print 'sys.path = ['
    for x in sys.path:
        print '\t' + repr(x)
    print ']'
    print '_our_sys_path = %r' % _our_sys_path


def _add_to_sys_path(x):
    """Add a directory to :data:`python:sys.path` if it is not already there.
    
    The directory is added BEFORE the one which imported this file, so that
    :envvar:`KS_PYTHON_SITES` will override anything that is already in :data:`python:sys.path`.
    
    """
    
    global insert_at
    
    # TODO: Make sure I don't have to deal with case-insensitive filesystems.
    x = os.path.abspath(x)
    
    if x not in sys.path:
        sys.path.insert(insert_at, x)
        insert_at += 1


def _process_pth(base, file_name):
    """Process a ``.pth`` file similar to site.addpackage(...)."""
    with open(os.path.join(base, file_name)) as fh:
        for line in fh:
            line = line.strip()
            if line.startswith('#'):
                continue
            if line.startswith('import'):
                exec line
                continue
            dir_name = os.path.abspath(os.path.join(base, line))
            if os.path.exists(dir_name):
                _add_to_sys_path(dir_name)


def add_site_dir(dir_name):
    """Add a pseudo site-packages directory to :data:`python:sys.path`.
    
    :param str dir_name: The directory to add.
    
    Looks for ``.pth`` files at the top-level and ``__site__.pth`` files within
    top-level directories.
    
    
    """
    
    # Don't so anything if the folder doesn't exist.
    if not os.path.exists(dir_name):
        return
        
    # Add dir to sys.path.
    _add_to_sys_path(dir_name)

    # Process *.pth files in a manner similar to site.addsitedir(...).
    for file_name in os.listdir(dir_name):
    
        # Skip dotfiles.
        if file_name.startswith('.'):
            continue
    
        # *.pth files.
        if file_name.endswith('.pth'):
            _process_pth(dir_name, file_name)
    
        # __site__.pth files inside packages.
        if os.path.exists(os.path.join(dir_name, file_name, '__site__.pth')):
            _process_pth(os.path.join(dir_name, file_name), '__site__.pth')


# Setup the pseudo site-packages.
sites = [x.strip() for x in os.environ.get('KS_PYTHON_SITES', '').split(':') if x]
sites.append(_our_sys_path)
for site in sites:
    add_site_dir(site)


