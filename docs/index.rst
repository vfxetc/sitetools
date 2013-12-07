.. _index:

sitetools
=========

Tools for setting up a Python execution environment at runtime. Generally useful
for extending one virtualenv_ with another.

This will take a few automatic actions at Python startup (in order):

1. All directories and virtualenvs listed within :envvar:`KS_SITES`
   will be added to :data:`sys.path`, in a similar manner as site-packages (via
   :func:`sitetools.sites.add_site_dir`).

2. Variables previously frozen via :func:`sitetools.environ.freeze` will be
   restored.

3. Any ``sitecustomize`` `entry points`_ will be called::

    from setuptools import setup
    setup(
        
        # name, description, etc..

        entry_points={
            'sitecustomize': [
                'name_of_hook = package.module:func',
            ],
        },
    )


.. _entry points: http://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
.. _virtualenv: https://pypi.python.org/pypi/virtualenv


Contents
--------

.. toctree::
    :maxdepth: 2

    sites
    environ
