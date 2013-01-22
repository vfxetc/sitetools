from __future__ import absolute_import

import logging
import os
import re
import sys
import warnings

log = logging.getLogger(__name__)


BLATHER = 1
TRACE = 5


def _show_warning(message, category, filename, lineno, file=None, line=None):
    if file is not None:
        warnings._showwarning(message, category, filename, lineno, file, line)
    else:
        s = warnings.formatwarning(message, category, filename, lineno, line)
        logger = logging.getLogger("py.warnings")
        logger.warning("%s", s)


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
        format='%(asctime)-15s %(levelname)s %(name)s: %(message)s',
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

