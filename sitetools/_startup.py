import traceback
import warnings


def import_and_call(mod_name, func_name, *args, **kwargs):

    try:
        mod = __import__(mod_name, fromlist=['.'])
    except (ImportError, SyntaxError), e:
        warnings.warn('Error while importing %s to call %s\n%s' % (mod_name, func_name, traceback.format_exc()))
        return

    func = getattr(mod, func_name, None)
    if not func:
        warnings.warn('%s.%s does not exist' % (mod_name, func_name))
        return

    try:
        func(*args, **kwargs)
    except Exception, e:
        warnings.warn('Error while calling %s.%s\n%s' % (mod_name, func_name, traceback.format_exc()))


# We don't need to guard against this only running once since it is a module
# and should only eval once.
import_and_call('sitetools.logging', '_setup')
import_and_call('sitetools.logging', '_setup_maya')
import_and_call('sitetools.sites', '_setup')
import_and_call('sitetools.monkeypatch', '_setup')
import_and_call('sitetools.environ', '_setup')
import_and_call('sitetools.hooks', '_setup')
