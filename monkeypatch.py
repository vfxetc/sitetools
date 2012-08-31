import sys
import functools


def patch(to_patch, name=None, must_exist=True, max_version=None):
    """Monkey patching decorator.
    
    :param to_patch: The object to patch.
    :param str name: The attribute of the object to patch; defaults to name of
        the patch function.
    :param bool must_exist: Must the original exist for the patch to be applied?
    :param tuple max_version: The maximum Python version to apply this patch to.
    
    :return: A decorator which takes a function and applies the patch, returning
        the patched version.
    
    Usage::
    
        # Patch os.listdir to return all lowercase.
        @patch(os)
        def listdir(original, path):
            return [x.lower() for x in original(path)]
        
        # It is patched in place.    
        os.listdir('.')
        
        # The new function still refers to the original.
        listdir('.')
        
        # Patch chflags to do nothing in Python up to 2.6.
        @patch(os, 'chflags', max_version=(2, 6))
        def patched_chflags(func, *args, **kwargs):
            pass
    
    """
    
    # Build a decorator which will apply the patch.
    def _decorator(func):
        
        # Get the name we are replacing.
        attrname = name or func.__name__
        
        # The thing we are replacing.
        func.__monkeypatched__ = original = getattr(to_patch, attrname, None)
        
        # A function to actually call the patch.
        def _patch_wrapper(*args, **kwargs):
            return func(func.__monkeypatched__, *args, **kwargs)
        
        # Make it look like the original.
        _patch_wrapper.__name__ = original.__name__ if original else func.__name__
        _patch_wrapper.__doc__ = '\n\n--- Monkey-Patched ---\n\n'.join(filter(None, [
            func.__doc__,
            original.__doc__ if original else 'Original %r does not exist.' % attrname,
        ])) or None
        
        # Bail if we don't want to apply the patch.
        if max_version and sys.version[:len(max_version)] > max_version:
            if sys.flags.verbose:
                print '# %s NOT patching %r.%s with %r; version > %r' % (__name__, to_patch, attrname, func, max_version)
            return _patch_wrapper
        
        # Bail if it doesn't exist.
        if must_exist and not original:
            if sys.flags.verbose:
                print '# %s NOT patching %r.%s with %r; original does not exist' % (__name__, to_patch, attrname, func)
            return _patch_wrapper
            
        # Install the patch.
        if sys.flags.verbose:
            print '# %s patching %r.%s with %r' % (__name__, to_patch, attrname, func)
        setattr(to_patch, attrname, _patch_wrapper)
        
        # Return the *patched* function.
        return _patch_wrapper
    
    # Return the patch building decorator.
    return _decorator


if __name__ == '__main__':
    
    import os
    
    @patch(os)
    def listdir(func, path):
        return [x.upper() for x in func(path)]
    
    print '\n'.join(os.listdir('.'))
