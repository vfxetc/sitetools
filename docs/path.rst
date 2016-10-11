
How to Find the ``sys.path``
============================

Sure, there is a :envvar:`PYTHONPATH`, but how exactly does Python use it to
construct the final :data:`sys.path`?


Prefix Discovery
----------------

First, Python discovers its ``sys.prefix`` and ``sys.exec_prefix``. This is
done by ``Modules/getpath.c``, but generally it uses ``$PYTHONHOME`` if it is
set, otherwise it will:

1) start at the python executable;
2) walk up the parent directories looking for ``lib/pythonX.Y/os.py``, and save
   this directory to ``sys.prefix``;
3) walk up the parent directories looking for ``lib/pythonX.Y/lib-dynload``,
   and save this directory to ``sys.exec_prefix``.


Base interpreter
----------------

Before running anything, or even importing site.py, the interpreter sets
sys.path to the following (on my Mac)::

    [$PYTHONPATH[0]]
    [...]
    {sys.prefix}/lib/python27.zip
    {sys.prefix}/lib/python2.7/
    {sys.prefix}/lib/python2.7/plat-darwin
    {sys.prefix}/lib/python2.7/plat-mac
    {sys.prefix}/lib/python2.7/plat-mac/lib-scriptpackages
    {sys.prefix}/lib/python2.7/lib-tk
    {sys.prefix}/lib/python2.7/lib-old
    {sys.exec_prefix}/lib/python2.7/lib-dynload


site.py
-------

Then it imports ``site``, Which calls ``site.addsitedir`` on the site-packages
directory above.

Any lines which are found in a ``*.pth`` file are appended to ``sys.path``, while
those that start with ``import`` are exec-ed.

Our ``sys.path`` now looks like::
    
    $PYTHONPATH
    sys.prefix-ed stdlib
    sys.exec_prefix-ed stdlib
    site-packages
    *.pth in site-packages

Finally, it imports ``sitecustomize``, which you can hook to do whatever you want.


homebrew
--------

Homebrew provides its own ``sitecustomize.py``, which it uses to clean the
site-packages within the python tree out of the sys.path, and add one within
the homebrew prefix.

Lets say homebrew is installed at ``/brew``. Python's prefix is then
``/brew/opt/python``. If you install packages into ``/brew/opt/python/lib/pythonX.Y/site-packages``
then will be destroyed when you perform a minor upgrade. Their ``sitecustomize.py``
strips all ``/brew/opt/`` out of ``sys.path``, and replaces it with ``/brew/lib/pythonX.Y/site-packages``.

The only annoying part about this is that we lose our own sitecustomize hook.


pip
---

Pip installs packages into site-packages as "flat" (directly importable) packages
(along with *.egg-info directories) such that it does not
need to use any ``*.pth`` files.

So, our ``sys.path`` looks like::

    $PYTHONPATH
    sys.prefix-ed stdlib
    sys.exec_prefix-ed stdlib
    site-packages (including pip-installed packages)
    *.pth in site-packages


easy_install
------------

easy_install creates an ``easy_install.pth``, which is required because it chooses
to install things as eggs.

It also (ab)uses the ``*.pth`` import magic to capture everything which is appended
to sys.path and insert it at the front::

    import sys; sys.__plen = len(sys.path)
    ./Jinja2-2.7.2-py2.7.egg
    ./MarkupSafe-0.23-py2.7-macosx-10.8-x86_64.egg
    ./docutils-0.11-py2.7.egg
    ./Pygments-1.6-py2.7.egg
    import sys; new=sys.path[sys.__plen:]; del sys.path[sys.__plen:]; p=getattr(sys,'__egginsert',0); sys.path[p:p]=new; sys.__egginsert = p+len(new)

This takes the new stuff, and inserts it at ``sys.__egginsert`` (or 0). If there are
multiple ``*.pth`` files which use this scheme they seem like they will play nicely.

This places easy_install-ed packages before the ``$PYTHONPATH``, so now it looks like::

    easy_install-ed packages, via easy_install.pth in site-packages
    $PYTHONPATH
    sys.prefix-ed stdlib
    sys.exec_prefix-ed stdlib
    site-packages (including pip-installed packages)
    *.pth in site-packages

It also creates it's own site.py for whatever reason. It seems to do more
reordering of the ``sys.path``, but I can't immediately divine what it is.

