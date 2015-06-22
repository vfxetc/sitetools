"""
Python's `stdlib logging <http://docs.python.org/2/library/logging.html>`_ is
setup as part of the sitecustomize initialization sequence. By default,
anything ``INFO`` and above will be logged to a location as determined by
:envvar:`PYTHONLOGFILE`.


Debugging via Logging
---------------------

It is highly recommended that you use ``DEBUG`` level logging instead of print statements, since they will not show up to the end users unless it is requested, and then key locations which need debugging output will already have it without having to re-determine where the trouble parts are. It is recommended to use the following pattern at the top of your files::

    import logging
    log = logging.getLogger(__name__)

    # Do stuff.

    log.debug('Something crazy is happening...')

You can then get those debug logs dumped to your terminal by using the :ref:`dev wrapper <dev_command>` in verbose mode::

    $ dev -v python -m my.awesome.module
    2013-04-07 13:48:08,416 DEBUG my.awesome.module: Something crazy is happening...


Environment Variables
---------------------

.. envvar:: KS_PYTHON_LOG_FILE

    A format string for determining where to save ``logging`` logs. Defaults
    (in the WesternX environment) to::

        /Volumes/VFX/logs/{date}/{login}@{ip}/{time}.{pid}.log

    Keys available include: ``date``, ``time``, ``login``, ``ip``, and ``pid``.

.. envvar:: KS_VERBOSE

    Set by ``-v`` flags to the :ref:`dev command <dev_command>'.

    When set to ``"1"``, ``"2"`` or ``"3"`` will request increasingly higher
    levels of verbosity. Right now that means decreasing the default logging
    threshold in Python processes to :const:`DEBUG`, :const:`TRACE` (5), and
    :const:`BLATHER` (1), respectively.

.. envvar:: KS_LOG_LEVELS

    A space-or-comma-delimited list of logger names and minimum record levels. E.g.::

        $ export KS_LOG_LEVELS=:WARNING,mayatools:DEBUG

    would set the general logging threshold to :const:`logging.WARNING`, but anything
    within ``mayatools`` to :const:`logging.DEBUG`.

    In an emergency this can effectively disable the logging system by setting::

        $ export KS_LOG_LEVELS=:100

    which is too high for any (built-in) log levels.


"""

from __future__ import absolute_import

import codecs
import datetime
import json
import logging.handlers
import os
import pwd
import re
import socket
import sys
import warnings

log = logging.getLogger(__name__)


# Our custom log levels.
BLATHER = 1
TRACE = 5


# Our log formats.
BASE_FORMAT = '%(asctime)-15s %(levelname)8s %(name)s: %(message)s'
MAYA_FORMAT = '%(name)s: %(message)s'
FULL_FORMAT = '%(asctime)-15s %(login)s@%(ip)s:%(pid)d %(levelname)s %(name)s: %(message)s'


# Replacment showwarning that backs onto loggers; nessesary since
# logging.captureWarnings is new to 2.7.
def _show_warning(message, category, filename, lineno, file=None, line=None):
    if file is not None:
        warnings._showwarning(message, category, filename, lineno, file, line)
    else:
        s = warnings.formatwarning(message, category, filename, lineno, line)
        logger = logging.getLogger("py.warnings")
        logger.warning("%s", s)


_context_start_time = datetime.datetime.now()
_context = {}
def _get_context():
    if not _context:

        # Try to get the outward-facing IP of this machine. We connect
        # to a remote IP (in this case, Google's DNS) and read out the
        # IP that the socket picked. Since we are using a DGRAM socket,
        # there really isn't any connection going on, so it doesn't
        # matter who we connect to.
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0)
            s.connect(('8.8.8.8', 53))
            ip = s.getsockname()[0]
        except Exception:
            ip = '0.0.0.0'

        # Get the current login name. We must be rather defensive about it.
        try:
            login = pwd.getpwuid(os.getuid())[0]
        except (ValueError, KeyError, OSError):
            login = os.environ.get('USER', 'unknown')

        _context.update({
            'pid': os.getpid(),
            'ip': ip,
            'login': login,
            'date': _context_start_time.strftime('%Y-%m-%d'),
            'time': _context_start_time.strftime('%H-%M-%S'),
        })

    return _context


class _NullFile(object):

    def write(self, *args):
        pass

    def flush(self):
        pass


class _FileSafetyWrapper(object):

    def __init__(self, fh):
        self._fh = fh
        for name in ('flush', 'close', 'encoding'):
            if hasattr(fh, name):
                setattr(self, name, getattr(fh, name))

    def __getattr__(self, name):
        return getattr(self._fh, name)

    def write(self, *args):
        try:
            self._fh.write(*args)
        except Exception as e:
            print '# Error while writing log:', repr(e)


class PatternedFileHandler(logging.FileHandler):

    def _open(self):

        # E.g.: /Volumes/VFX/logs/{date}/{login}@{ip}/{time}.{pid}.log
        #       /Volumes/VFX/logs/2013-01-22/mboers@10.2.200.1/11-15-15.12345.log

        file_path = self.baseFilename.format(**_get_context())
        dir_path = os.path.dirname(file_path)
        umask = os.umask(0)
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST: # File exists.
                warnings.warn('Error while creating log directory: %r' % e)
                return _NullFile()
        finally:
            os.umask(umask)

        return _FileSafetyWrapper(open(file_path, 'ab'))


class ContextInfoFilter(logging.Filter):

    def filter(self, record):
        record.__dict__.update(_get_context())
        return True


def _patch_file_handler():

    # Older than 2.6.2, the "delay" kwarg to a FileHandler would result
    # in one of the superclasses not getting initialized.
    if sys.version_info < (2, 6, 2):
        old = logging.FileHandler.__init__
        def new(self, *args, **kwargs):
            old(self, *args, **kwargs)
            if not hasattr(self, 'filters'):
                logging.Handler.__init__(self)
        logging.FileHandler.__init__ = new


def _setup():

    # Fix some bugs in the stdlib.
    _patch_file_handler()

    # Hook warnings into logging. In Python2.7 we could use
    # logging.captureWarnings, but we are supporting earlier versions.
    warnings.showwarning = _show_warning

    # Setup extra levels.
    logging.BLATHER = BLATHER
    logging.addLevelName(BLATHER, 'BLATHER')
    logging.TRACE = TRACE
    logging.addLevelName(TRACE, 'TRACE')

    # Determine the level to use.
    verbosity = os.environ.get('KS_VERBOSE', '0')
    level = {
        '0': logging.INFO,
        '1': logging.DEBUG,
        '2': logging.TRACE,
        '3': logging.BLATHER,
    }.get(verbosity, logging.DEBUG)

    # Ignore all DeprecationWarnings unless we are atleast slightly verbose
    if level >= logging.INFO:
        warnings.simplefilter('ignore', DeprecationWarning)

    # Do the basic config, dumping to stderr.
    root = logging.getLogger()
    root.setLevel(level)
    handler = logging.StreamHandler(_FileSafetyWrapper(sys.stderr))
    handler.setFormatter(logging.Formatter(BASE_FORMAT))
    root.addHandler(handler)

    log.log(BLATHER, 'root logging setup')

    # Set the levels on a few (verbose) loggers.
    for name, level in (
        ('pymel', logging.WARNING),
        ('paramiko.transport', logging.WARNING),
    ):
        logging.getLogger(name).setLevel(level)
    
    # Setup specially requested levels, usually from `dev --log name:LEVEL`
    requested_levels = os.environ.get('KS_LOG_LEVELS')
    if requested_levels:
        requested_levels = [x.strip() for x in re.split(r'[\s,]+', requested_levels)]
        requested_levels = [x for x in requested_levels if x]

        for spec in requested_levels:

            parts = spec.split(':')
            if len(parts) != 2:
                log.error('%r is invalid log specification; try \'name:level\'', spec)
                continue

            name, level = parts
            name = name.strip() or None
            try:
                level = int(level)
            except ValueError:
                level = getattr(logging, level.upper(), None)
            if not isinstance(level, int):
                log.error('%r is invalid log level', level)
                continue

            logger = logging.getLogger(name)
            logger.setLevel(level)
            log.log(TRACE, '%s set to %s', name, level)

    # Setup logging to a file, if requested.
    pattern = os.environ.get('KS_PYTHON_LOG_FILE')
    if pattern:
        handler = PatternedFileHandler(pattern, delay=True)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(FULL_FORMAT))
        handler.addFilter(ContextInfoFilter())
        logging.getLogger().addHandler(handler)
        
    # log to graylog
    class GraylogHandler(logging.handlers.DatagramHandler):
        def makePickle(self, record):
            return json.dumps(dict(
                version='1.1',
                host=socket.gethostname(),
                short_message=self.format(record),
                _application='python.logging',
                _pid=record.process,
                _python_log_name=record.name,
                _python_log_level=record.levelno,
            ))
    handler = GraylogHandler('graylog.westernx', 12201)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(levelname)8s %(name)s: %(message)s'))
    root.addHandler(handler)



def _setup_maya():
    """Setup Maya logging, but be *really* defensive about it."""

    try:
        import maya.utils
    except ImportError:
        return

    # Remove the shell handler; we have created one ourselves.
    if hasattr(maya.utils, 'shellLogHandler'):
        maya_handler = logging.getLogger(os.environ.get('MAYA_DEFAULT_LOGGER_NAME'))
        maya_handler.removeHandler(maya.utils.shellLogHandler())

    # Change the default format on the UI handler.
    # TODO: Get some safety wrapping arounc this handler.
    if hasattr(maya.utils, 'guiLogHandler'):
        format = os.environ.get('MAYA_GUI_LOGGER_FORMAT')
        if not format:
            maya.utils.guiLogHandler().setFormatter(logging.Formatter(MAYA_FORMAT))


