"""

This module is mostly a re-implementation of :func:`python:site.addsitedir`,
with slight modifications:

1. We add the given directory to the :data:`python:sys.path`.
2. We search for ``*.pth`` files within that directory and process them
   (nearly) the same as :func:`python:site.addsitedir` does.
3. We look for ``__site__.pth`` files within each top-level directory and
   process them as well. This allows for a tool to self-describe its
   paths and contain that metadata within its own repository, and therefore
   be usable without being "installed".



We reimplemented this because:

1. Our NFS was throwing some wierd errors with :func:`site.addsitedir` (due to ``._*`` files).
2. We wanted self-describing repositories.
3. We wanted virtualenvs to be able to inherit from each other.


Environment Variables
---------------------

.. envvar:: KS_SITES

    A colon-delimited list of sites to add as pseudo site-packages (see :ref:`python_setup`).

    If the "site" is a directory, it will be processed as if it were a ``site-packages`` directory.

    If the "site" is a file named ``python``, it will search for the corresponding ``site-packages`` directory.

    If the current environment (equivalent to :data:`python:sys.executable`) is
    found in this list then it will be used as a centering point for the
    other sites listed. Anything before the current environment will be prepended
    to ``sys.path``, and anything after the current environment will be appended.


.. envvar:: KS_DEV_SITES

    A colon-delimited list of sites to look for when using the
    :ref:`dev command<dev_command>`. Any ``~`` found may refer to any requested
    user's home.

    If unset, defaults to ``~/dev:~/dev/venv/bin/python``.


API Reference
-------------

"""

from __future__ import absolute_import

import errno
import logging
import os
import stat
import sys
import traceback
import warnings

from .utils import get_environ_list


log = logging.getLogger(__name__)


# TODO: Derive this for more platforms.
site_package_postfix = os.path.join('lib', 'python%d.%d' % sys.version_info[:2], 'site-packages')


class Site(object):

    def __init__(self, path):

        try:
            self.path = os.path.normpath(path)
            self.stat = os.stat(path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
            raise ValueError('site does not exist')

        if stat.S_ISDIR(self.stat.st_mode):
            self.is_venv = False

        elif os.path.basename(self.path) in ('python', 'python%s.%s' % sys.version_info[:2]):
            prefix = os.path.abspath(self.path)
            while prefix and prefix != '/':
                prefix = os.path.dirname(prefix)
                if os.path.exists(os.path.join(prefix, site_package_postfix)):
                    self.is_venv = True
                    self.prefix = prefix
                    break
            else:
                raise ValueError('file is not within a virtualenv')

        else:
            raise ValueError('expected directory or Python executable')

    @property
    def bin_path(self):
        return os.path.join(self.prefix, 'bin') if self.is_venv else None

    @property
    def python_path(self):
        return os.path.join(self.prefix, site_package_postfix) if self.is_venv else self.path

    def __str__(self):
        return self.path

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return str(self) == str(other)


class SysPathInserter(object):
    """Class to insert a series of paths into :data:`sys.path` incrementally."""
    
    def __init__(self, index=None):

        self.index = None

        if isinstance(index, int):
            self.index = index
        elif isinstance(index, basestring):
            try:
                self.index = sys.path.index(index)
            except ValueError:
                warnings.warn('%r was not found on sys.path' % index)
        
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

        if self.index is not None:
            sys.path.insert(self.index, path)
            self.index += 1
        else:
            sys.path.append(path)


_processed_pths = set()


def _process_pth(path, base, file_name):
    """Process a ``.pth`` file similar to site.addpackage(...)."""
    
    pth_path = os.path.abspath(os.path.join(base, file_name))
    
    # This is for `exec` below, as some packages (e.g. virtualenvwrapper)
    # assume that `site.addpackage` is running them.
    sitedir = os.path.dirname(base)

    # Only process this once.
    if pth_path in _processed_pths:
        return
    _processed_pths.add(pth_path)    
    
    log.log(1, '_process_pth(..., %r, %r)', base, file_name)
    
    try:
        fh = open(pth_path)
    except IOError as e:
        log.log(1, '_process_path IOError %s' % e)
        return
    
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

            log.log(1, '_process_pth exec %s' % line)
            exec line
            continue
        
        # Add it.
        path.add(os.path.join(base, line))


def add_site_list(dir_list):
    """Add a list of pseudo site-packages to :data:`python:sys.path`.

    This centers the list on ``sys.path`` around the current environment.
    I.e. if this environment is in the list, then directories before it in the
    list will be prepended to ``sys.path``, and directories after it will
    be appended to ``sys.path``.

    """
    
    our_site_packages = os.path.abspath(os.path.join(sys.prefix, site_package_postfix))
    dir_list = [os.path.abspath(x) for x in dir_list]

    prepend = SysPathInserter(0)
    append = SysPathInserter()

    try:
        our_index = dir_list.index(our_site_packages)
    except ValueError:
        our_index = None

    for i, dir_name in enumerate(dir_list):
        if our_index is None or i < our_index:
            add_site_dir(dir_name, _path=prepend)
        else:
            add_site_dir(dir_name, _path=append)


def add_site_dir(dir_name, before=None, _path=None):
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
    
    path = _path or SysPathInserter(index=before)
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

    sites = []
    for site_path in get_environ_list('KS_SITES'):
        try:
            site = Site(site_path)
        except ValueError as e:
            log.log(5, 'invalid site %s: %s' % (site_path, e.args[0]))
        sites.append(site.python_path)

    try:
        add_site_list(sites)
    except Exception:
        warnings.warn('Error while adding sites %s:\n%s' % (sites, traceback.format_exc().rstrip()))

