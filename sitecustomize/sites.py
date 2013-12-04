"""

Since WesternX's code is released my deploying it to a shared network location,
we cannot use the standard Python package installtion systems that currently
exist. Ergo, this package.

All of our in-house tools are located within a
directory located via :envvar:`KS_TOOLS`, which must be on the
:envvar:`python:PYTHONPATH`, and defaults to::

    /Volumes/VFX/production/key_tools

Since :envvar:`KS_TOOLS` must be on the :envvar:`python:PYTHONPATH`, any pure
Python packages are importable from that location without any further
configuration. However, some of the tools are not so simple. For
example, the ``key_base`` houses multiple
subdirectories that must be on Python's :data:`python:sys.path` (for
backwards compatibility). Those subdirectories include (but are not
limited to)::

    ./python
    ./3d/maya/python
    ./2d/nuke/python
    ./systems/python

These are added by Python at runtime via this package, which adds each directory within
:envvar:`KS_PYTHON_SITES` (and the directory from which
``sitecustomize`` was imported) as pseudo site-
packages. First, it adds the directory to the :data:`python:sys.path`.
Then it searches for ``*.pth`` files within that directory and processes
them the same as :func:`python:site.addsitedir` does. However, it also
looks for ``__site__.pth`` files within each top-level directory and
process them as well. This allows for a tool to self-describe its paths
and contain that metadata within its own repository. `Take a look at the
key_base/__site__.pth <../../../../key_base/__site__.pth>`_.

.. note:: This is very similar to Python Eggs which also describe
    themselves, but does not require an installation step to generate the
    ``*.pth`` file.


Environment Variables
---------------------

.. envvar:: KS_PYTHON_SITES

    A colon-delimited list of directories which will be added as pseudo
    site-packages (see :ref:`python_setup`) before :envvar:`KS_TOOLS`. Note
    that :envvar:`KS_TOOLS` will always be added after these directories so
    that your local tools need not include every tool since the production
    deployment will be used as a fallback by default. We tend not to actually
    modify this by hand and instead use a command-wrapper to set it.

.. envvar:: KS_TOOLS

    The directory from which the in-house tools are loaded. It is currently in use to:
    
    - setup Python in the :ref:`shell environment <shell_setup>`;
    - identify where to :ref:`deploy_tools`;
    - identify where to :ref:`build_docs`.
    
    If ``KS_TOOLS`` is set before the main environment script is sourced it will result in everything being loaded from that location, and will require a complete set of tools, particularly :ref:`sitecustomize <sitecustomize:index>` in order to bootstrap the rest of the :ref:`Python environment <python_setup>`.

    .. warning:: This is a master override and is usually overkill. Unless you completely understand how the Python path is augmented this will likely result in very puzzling errors.


API Reference
-------------

"""

from __future__ import absolute_import

import logging
import os
import sys
import warnings


log = logging.getLogger(__name__)


class _SysPathInserter(object):
    """Class to insert a series of paths into :data:`sys.path` incrementally."""
    
    def __init__(self, before=None):
        
        # Determine where we want to insert new paths.
        try:
            self.insert_at = sys.path.index(before) if before else None
        except ValueError:
            self.insert_at = None
            warnings.warn('%r was not found on sys.path' % before)
        
    def add(self, path):
        """Add the given path to the decided place in sys.path"""
        
        # sys.path always has absolute paths.
        path = os.path.abspath(path)
        
        # It must exist.
        if not os.path.exists(path):
            return
        
        # It must not already be in sys.path.
        if path in sys.path:
            return
        
        # Put it in the right place.
        if self.insert_at is not None:
            sys.path.insert(self.insert_at, path)
            self.insert_at += 1
        else:
            sys.path.append(path)


_processed_pths = set()


def _process_pth(path, base, file_name):
    """Process a ``.pth`` file similar to site.addpackage(...)."""
    
    pth_path = os.path.abspath(os.path.join(base, file_name))
    
    # Only process this once.
    if pth_path in _processed_pths:
        return
    _processed_pths.add(pth_path)    
    
    log.log(1, '_process_pth(..., %r, %r)', base, file_name)
        
    for line in open(pth_path):
        line = line.strip()
        
        # Blanks and comments.
        if not line or line.startswith('#'):
            continue
        
        # Execs.
        if line.startswith('import'):
            
            # Sorry easy-install: you break our environment.
            if file_name == 'easy-install.pth' and 'sys.__plen' in line:
                continue

            exec line
            continue
        
        # Add it.
        path.add(os.path.join(base, line))


def add_site_dir(dir_name, before=None):
    """Add a pseudo site-packages directory to :data:`python:sys.path`.
    
    :param str dir_name: The directory to add.
    :param str before: A directory on :data:`sys.path` that new paths should be
    inserted before.
    
    Looks for ``.pth`` files at the top-level and ``__site__.pth`` files within
    top-level directories.
    
    """
    
    log.log(5, 'add_site_dir(%r, before=%r)', dir_name, before)
    
    # Don't do anything if the folder doesn't exist.
    if not os.path.exists(dir_name):
        return
    
    path = _SysPathInserter(before=before)
    path.add(dir_name)

    # Process *.pth files in a manner similar to site.addsitedir(...).
    for file_name in os.listdir(dir_name):
    
        # Skip dotfiles.
        if file_name.startswith('.'):
            continue
    
        # *.pth files.
        if file_name.endswith('.pth'):
            _process_pth(path, dir_name, file_name)
    
        # __site__.pth files inside packages.
        if os.path.exists(os.path.join(dir_name, file_name, '__site__.pth')):
            _process_pth(path, os.path.join(dir_name, file_name), '__site__.pth')


def _setup():
    
    # Where do we want to start inserting directories into sys.path? Just before
    # this module, of course. So determine where we were imported from.
    our_sys_path = os.path.abspath(os.path.join(__file__,
        os.path.pardir,
        os.path.pardir,
    ))

    sites = [x.strip() for x in os.environ.get('KS_PYTHON_SITES', '').split(':') if x]
    sites.append(our_sys_path)
    for site in sites:
        try:
            add_site_dir(site, before=our_sys_path)
        except Exception, why:
            warnings.warn('Error while adding site-package %r: %r' % (site, why))

