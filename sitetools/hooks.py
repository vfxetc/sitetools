import traceback
from pkg_resources import iter_entry_points
from warnings import warn


def _setup():
    for ep in sorted(iter_entry_points('sitecustomize'), key=lambda ep: ep.name):
        callback = ep.load()
        try:
            callback()
        except Exception as e:
            warn('%s during sitecustomize hook: %s\n%s' % (e.__class__.__name__, e, traceback.format_exc()))

