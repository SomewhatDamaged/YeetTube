import logging

from redbot.core import data_manager


def create_logging(name):

    log = logging.getLogger(f"red.{name}")
    log.setLevel(logging.DEBUG)

    logfile_path = data_manager.cog_data_path(raw_name=name) / f"{name}.log"

    if len(log.handlers) == 0:
        fhandler = logging.handlers.RotatingFileHandler(  # type: ignore
            filename=str(logfile_path),
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
