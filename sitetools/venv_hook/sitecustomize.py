"""
This file serves as a hook into virtualenvs that do NOT have sitetools
installed.

It is added to the $PYTHONPATH by the `dev` command so that new virtualenvs
can refer to the sitetools from the old virtualenv.

It tries to play nice by looking for the next sitecustomize module.

"""

import imp
import os
import sys
import warnings


try:

    try:
        import sitetools._startup
    except ImportError:
        
        # Pull in the sitetools that goes with this sitecustomize.
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # Let this ImportError raise.
        import sitetools._startup

except Exception as e:
    warnings.warn("Error while importing sitetools._startup: %s" % e)


# Be a good citizen and find the next sitecustomize module.
my_path = os.path.dirname(os.path.abspath(__file__))
clean_path = [x for x in sys.path if os.path.abspath(x) != my_path]
try:
    args = imp.find_module('sitecustomize', clean_path)
except ImportError:
    pass
else:
    imp.load_module('sitecustomize', *args)
