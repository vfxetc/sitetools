"""This package is responsible for setting up :data:`python:sys.path` for Western X.

This adds all the directories listed within :envvar:`KS_PYTHON_SITES`, and the directory
from which this was imported from, in a similar manner as site-packages via
:func:`python:site.addsitedir`.

We have reimplemented that functionality for two reasons:

1. Our NFS was throwing some wierd errors with site.addsitedir.
2. We added ``__site__.pth`` files to packages to allow them to describe themselves
   and keep their ``.pth`` file in their own repository.

.. warning:: Be extremely careful while modifying this package and test it very
    thoroughly, since being able to locate any other packages is dependant on it
    running successfully.
    
"""

import os
import sys
import warnings


def _add_to_sys_path(x):
    """Add a directory to :data:`python:sys.path` if it is not already there.
    
    The directory is added BEFORE the one which imported this file, so that
    :envvar:`KS_PYTHON_SITES` will override anything that is already in :data:`python:sys.path`.
    
    """
    global insert_at
    
    # TODO: Make sure I don't have to deal with case-insensitive filesystems.


def _process_pth(paths, base, file_name):
    """Process a ``.pth`` file similar to site.addpackage(...)."""
    for line in open(os.path.join(base, file_name)):
        line = line.strip()
        if line.startswith('#'):
            continue
        if line.startswith('import'):
            exec line
            continue
        dir_name = os.path.abspath(os.path.join(base, line))
        paths.append(dir_name)


def add_site_dir(dir_name, before=None):
    """Add a pseudo site-packages directory to :data:`python:sys.path`.
    
    :param str dir_name: The directory to add.
    
    Looks for ``.pth`` files at the top-level and ``__site__.pth`` files within
    top-level directories.
    
    
    """
    
    # Don't so anything if the folder doesn't exist.
    if not os.path.exists(dir_name):
        return
    paths = [dir_name]
    
    # Determine where we want to insert new paths.
    try:
        insert_at = sys.path.index(before) if before else None
    except ValueError:
        insert_at = None
        warnings.warn('%r was not found on sys.path' % before)

    # Process *.pth files in a manner similar to site.addsitedir(...).
    for file_name in os.listdir(dir_name):
    
        # Skip dotfiles.
        if file_name.startswith('.'):
            continue
    
        # *.pth files.
        if file_name.endswith('.pth'):
            _process_pth(paths, dir_name, file_name)
    
        # __site__.pth files inside packages.
        if os.path.exists(os.path.join(dir_name, file_name, '__site__.pth')):
            _process_pth(paths, os.path.join(dir_name, file_name), '__site__.pth')
    
    # Add everything which exists to the path before the path we were asked to.
    existing = set(sys.path)
        
    for path in paths:

        path = os.path.abspath(path)
        
        if path in existing:
            continue
        existing.add(path)
        
        if not os.path.exists(path):
            continue
        
        if insert_at:
            sys.path.insert(insert_at, path)
            insert_at += 1
        else:
            sys.path.append(path)
        
