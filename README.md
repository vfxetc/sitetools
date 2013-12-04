sitecustomize
=============

This package is responsible for building a Python execution environment, and providing hooks for others to augment the process. The major tasks it performs are:

* adding "super" site-packages (much like [Python's standard site-packages][pylib-addsitedir]) described by environment variables;
* resetting `os.environ` after it is mangled by programs which embed Python (e.g. Maya and Nuke);
* calling other packages via "sitecustomize" [`entry_points`][ep] in the package's metadata.

[Read the docs][rtd], and good luck!

[pylib-logging]: http://docs.python.org/2/library/logging.html
[pylib-addsitedir]: http://docs.python.org/2/library/site.html#site.addsitedir
[rtd]: https://sitecustomize.readthedocs.org/en/latest/
[ep]: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
