.. _index:

sizecutomize
============

Overview
--------

Common tasks for setting up a Python execution environment.

Variables previously frozen via :func:`sitecustomize.environ.freeze` will be
restored.

All directories listed within :envvar:`PYTHONSITES` and the directory
from which this was imported from will be added to :data:`sys.path`, in a
similar manner as site-packages via :func:`python:site.addsitedir`. We
reimplemented that functionality because:

1. Our NFS was throwing some wierd errors with :func:`site.addsitedir` (due to ``._*`` files).
2. We added ``__site__.pth`` files to packages to allow them to describe themselves
   and keep their ``.pth`` file in their own repository.

.. warning:: Be extremely careful while modifying this package and test it very
    thoroughly, since being able to locate any other packages is dependant on it
    running successfully.


Contents
--------

.. toctree::
    :maxdepth: 2

    sites
    environ
