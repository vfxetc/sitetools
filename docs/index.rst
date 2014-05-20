.. _index:

sitetools - WesternX's Python Setup
===================================

Tools for setting up WesternX's Python execution environment at runtime.
Generally useful for extending one Python prefix (or virtualenv_) with another.

When ``sitetools._startup`` is imported (by ``sitecustomize`` in our environment),
this will take a few automatic actions:

1. The standard library logging_ will be setup.

2. All directories and virtualenvs listed within :envvar:`KS_SITES`
   will be added to :data:`sys.path`, in a similar manner as site-packages (via
   :func:`sitetools.sites.add_site_dir`), but extended to support multi-platform
   builts and self-describing tools.

3. Variables previously frozen via :func:`sitetools.environ.freeze` will be restored.

4. Monkey-patch :func:`os.chflags` to not error on our NFS (by ignoring the
   error) for Python2.6.


.. warning:: Be extremely careful while modifying this package and test it very
    thoroughly, since being able to locate any other packages is dependent on it
    running successfully.


Additionally, there are :ref:`a set of scripts <dev>` to assist in local development.


.. _logging: https://docs.python.org/2/library/logging.html
.. _virtualenv: https://pypi.python.org/pypi/virtualenv


Contents
--------

.. toctree::
    :maxdepth: 2

    dev
    sites
    environ
    logging
