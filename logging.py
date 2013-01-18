from __future__ import absolute_import

import logging
import os
import re
import sys


log = logging.getLogger(__name__)


def setup_logging():

    level = logging.DEBUG if os.environ.get('KS_VERBOSE') else logging.INFO
    logging.basicConfig(
        format='%(asctime)-15s %(levelname)s %(name)s: %(message)s',
        level=level,
        stream=sys.stderr,
    )

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
            log.debug('%s set to %s', name, level)
