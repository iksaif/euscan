import logging


class FakeLogger(object):
    def __getattr__(self, key):
        return lambda *x, **y: None


def set_verbosity_level(logger, verbosity):
    try:
        verbosity = int(verbosity)
    except (ValueError, TypeError):
        return logger

    levels = {
        0: logging.DEBUG,
        1: logging.INFO,
        2: logging.WARNING,
        3: logging.ERROR,
        4: logging.CRITICAL
    }

    if verbosity < 0:
        verbosity = 0

    if verbosity > 4:
        verbosity = 4

    logger.setLevel(levels[verbosity])

    return logger
