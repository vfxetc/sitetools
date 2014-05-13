.. _dev:

Development Scripts
===================

.. _dev_install:

The `dev-install` Command
-------------------------

A ``dev-install`` command exists to assist in the installation of tools for local development. It will first assert that a virtualenv_ exists in your home, clone the tool, and finally install it into your virtualenv.

The first time you run ``dev-install`` (or ``dev``) on a platform, you will be prompted to create your venv::

    $ dev true
    Could not find existing development virtualenv.
    A virtualenv can be created in these locations:
        1) ~/dev/venv-osx/bin/python
        2) ~/key_tools/venv-osx/bin/python
    Which one do you want to create? (1): 1
    New python executable in /home/mboers/dev/venv-osx/bin/python
    Installing setuptools, pip...done.

Now you can install tools::

    $ dev-install --list
    < big list of tools and their repos >

    $ dev-install sgfs
    < snip >
    Successfully installed sgfs
    Cleaning up...


.. _dev_status:

The `dev-status` Command
------------------------

A ``dev-status`` command exists to help you figure out how your local tools relate to those in production::

    $ dev-status
        WARNING: You are behind by 6 commits.
    ==> sgsession
        Working directory is dirty.
    ==> sgfs
        Up to date.

Here we can see that my copy of ``key_base`` is behind by 6 commits, I have uncommitted work on ``sgsession``, and my ``sgfs`` is up to date.

We can have ``dev-status`` bring everything up to date for us::

    
    $ dev-status -nu
    ==> key_base
    Updating 05eb284..fc9c4f8
    Fast-forward
        Up to date.
    ==> sgsession
        Working directory is dirty.
    ==> sgfs
        Up to date.


.. _dev_command:

The `dev` Command Wrapper
-------------------------

A ``dev`` command exists that will run any other command from within an automatically constructed development environment. Effectively, any Python imports will use your local packages, and any executables will be sourced from your local paths. Any packages or executables not found locally will fall back on the production tools.

It does this by searching for development tools in :envvar:`KS_DEV_SITES`, and appends those that exist to :envvar:`KS_SITES`. It also looks across the standard ``PATH`` for directories that fall within the production environment, and prepends the development versions of those paths.

Lets look at some examples. I can bring up a Python shell in the development environment::

    $ dev python
    Python 2.6.6 (r266:84292, Nov  1 2010, 12:40:26) 
    [GCC 4.2.1 (Apple Inc. build 5646)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import ks
    >>> ks
    <module 'ks' from '/home/mboers/dev/key_base/python/ks.py'>

Notice how the ``ks`` package was located in my home directory. I can also launch the development version of the toolbox::

    $ dev which toolbox
    /home/mboers/dev/key_base/2d/bin/toolbox
    $ dev toolbox

To drop into a development shell::

    $ dev bash
    $ which toolbox
    /home/mboers/dev/key_base/2d/bin/toolbox

You can also use other developer's environments!

::

    $ dev -u mreid which toolbox
    /home/mreid/dev/key_base/2d/bin/toolbox

See ``dev --help`` for all of the options.

