import logging


def create_logging(name):

    log = logging.getLogger(f"red.{name.lower()}")
    log.setLevel(logging.DEBUG)
    return log


def add_logger(log, path) -> logging.Logger:
    if len(log.handlers) == 0:
        fhandler = logging.handlers.RotatingFileHandler(  # type: ignore
            filename=str(path),
            encoding="utf-8",
            mode="a",
            maxBytes=10**7,
            backupCount=5,
        )
        fmt = logging.Formatter(
            "%(asctime)s %(levelname)s %(module)s %(funcName)s %(lineno)d: %(message)s",
            datefmt="[%d/%m/%Y %H:%M]",
        )
        fhandler.setFormatter(fmt)
        log.addHandler(fhandler)
    return log
