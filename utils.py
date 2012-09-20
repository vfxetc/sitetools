import sys

if hasattr(sys, 'flags') and sys.flags.verbose:
    def verbose(msg, *args, **kwargs):
        if kwargs:
            print msg % kwargs
        elif args:
            print msg % args
        else:
            print msg
else:
    def verbose(*args, **kwargs):
        pass
