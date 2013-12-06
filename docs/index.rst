.. _index:

sitetools
=========

Tools for setting up a Python execution environment at runtime. Generally useful
for extending one virtualenv_ with another.

This will take a few automatic actions at Python startup (in order):

1. All directories listed within :envvar:`KS_SITES` will be added to
   :data:`sys.path`, in a similar manner as site-packages (via
   :func:`sitetools.sites.add_site_dir`).

2. All virtual environments listed within :envvar:`KS_PYTHON_VENVS` will have their
   ``lib/pythonX.Y/site-packages`` directory added to :data:`sys.path` as above.

3. Variables previously frozen via :func:`sitetools.environ.freeze` will be
   restored.

4. Any ``sitecustomize`` `entry points`_ will be called::

    from setuptools import setup
    setup(
        
        # name, description, etc..

        entry_points={
            'sitecustomize': [
                'name_of_hook = package.module:func',
            ],
        },
    )


.. note::
    This package **MUST** be installed in the Python environment that is
    being initialized. If this is installed in the system site-packages it
    will not work in a virtualenv_.


.. _entry points: http://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _virtualenv: https://pypi.python.org/pypi/virtualenv


Contents
--------

.. toctree::
    :maxdepth: 2

    sites
    environ
