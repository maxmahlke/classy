import os
import logging

from rich.logging import RichHandler

FORMAT = "%(message)s"


def init_logging(level):
    """
    Set the global logging level.

    Parameters
    ----------
    level : int
        The logging level, logging everything [0] to nothing [5]. Default is 2.",
    """
    logging.basicConfig(
        level=level * 10,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False, show_time=False)],
    )

    # Set the same logging level for tensorflow
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = str(level)
