The WesternX Python Environment
===============================

This package is responsible for establishing the Python execution environment for Western X. The major tasks it performs are:

* setting up uniform logging via [Python's standard loggers][pylib-logging];
* adding "super" site-packages (much like [Python's standard site-packages][pylib-addsitedir]) described by environment variables;
* resetting `os.environ` after it is mangled by programs which embed Python (e.g. Maya and Nuke);
* monkey-patching some Python bugs in older versions that are in use at Western X.

For this to function in our environment it must be directly importable, and so this package is not arranged for consumption by `easy_install` or `pip`. When placed somewhere visible by `sys.path` (e.g. via `$PYTHONPATH`) it will run at Python startup.

[Read the docs][rtd], and good luck!

[pylib-logging]: http://docs.python.org/2/library/logging.html
[pylib-addsitedir]: http://docs.python.org/2/library/site.html#site.addsitedir
[rtd]: https://westernx-sitecustomize.readthedocs.org/en/latest/
