sitetools
=========

This package gives you some tools for setting up your Python environment at runtime. The major tasks it performs are:

* adding psuedo-site-packages (much like [Python's standard site-packages][pylib-addsitedir]) described by environment variables;
* resetting `os.environ` after it is mangled by programs which embed Python (e.g. Maya and Nuke);
* calling other packages via "sitecustomize" [`entry_points`][ep] in the package's metadata.

[Read the docs][rtd], and good luck!

[pylib-logging]: http://docs.python.org/2/library/logging.html
[pylib-addsitedir]: http://docs.python.org/2/library/site.html#site.addsitedir
[rtd]: https://sitetools.readthedocs.org/en/latest/
[ep]: https://pythonhosted.org/setuptools/setuptools.html#dynamic-discovery-of-services-and-plugins
