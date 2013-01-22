from __future__ import absolute_import

import codecs
import datetime
import logging
import os
import re
import socket
import sys
import warnings

log = logging.getLogger(__name__)


BLATHER = 1
TRACE = 5


BASE_FORMAT = '%(asctime)-15s %(levelname)s %(name)s: %(message)s'
FULL_FORMAT = '%(asctime)-15s %(login)s@%(ip)s:%(pid)d %(levelname)s %(name)s: %(message)s'

def _show_warning(message, category, filename, lineno, file=None, line=None):
    if file is not None:
        warnings._showwarning(message, category, filename, lineno, file, line)
    else:
        s = warnings.formatwarning(message, category, filename, lineno, line)
        logger = logging.getLogger("py.warnings")
        logger.warning("%s", s)


_context_start_time = datetime.datetime.utcnow()
_context = {}
def _get_context():
    if not _context:

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        ip = s.getsockname()[0]

        _context.update({
            'pid': os.getpid(),
            'ip': ip,
            'login': os.getlogin(),
            'date': _context_start_time.strftime('%Y-%m-%d'),
            'time': _context_start_time.strftime('%H-%M-%S'),
        })
    return _context


class PatternedFileHandler(logging.FileHandler):

    def _open(self):

        # E.g.: /Volumes/VFX/logs/{date}/{login}.{ip}/{time}.{pid}.log
        # /Volumes/VFX/logs/2013-01-22/mboers.10.2.200.1/11-15-15.12345.log

        file_path = self.baseFilename.format(**_get_context())
        dir_path = os.path.dirname(file_path)
        umask = os.umask(0)
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno != 17: # File exists.
                raise
        finally:
            os.umask(umask)

        return open(file_path, 'ab')


class ContextInfoFilter(logging.Filter):

    def filter(self, record):
        record.__dict__.update(_get_context())
        return True


def _setup():


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

    # Do the basic config, dumping to stderr.
    logging.basicConfig(
        format=BASE_FORMAT,
        level=level,
        stream=sys.stderr,
    )

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
            log.log(5, '%s set to %s', name, level)

    # Setup logging to a file, if requested.
    pattern = os.environ.get('KS_PYTHON_LOG_FILE')
    if pattern:
        handler = PatternedFileHandler(pattern, delay=True)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(FULL_FORMAT))
        handler.addFilter(ContextInfoFilter())
        logging.getLogger().addHandler(handler)

