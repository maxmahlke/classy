from datetime import datetime
from pathlib import Path
import tarfile
from zipfile import BadZipFile, ZipFile

import pandas as pd
import numpy as np

from .logging import logger
from . import download  # noqa
from . import progress  # noqa


def find_nearest(array, value):
    """Return index of closest value to target value in array.

    https://stackoverflow.com/a/2566508
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def unpack(PATH_ARCHIVE, encoding):
    # encoding : str
    #     The compression encoding. Default is None. Must be specified if unpack is True.
    if encoding == "tar.gz":
        with tarfile.open(PATH_ARCHIVE, mode="r:gz") as archive:
            dest = (
                PATH_ARCHIVE.parent
                if "/cds/" not in str(PATH_ARCHIVE)
                else Path(PATH_ARCHIVE.parent / Path(PATH_ARCHIVE.stem).stem)
            )
            dest.mkdir(exist_ok=True)
            archive.extractall(dest)
    elif encoding == "tar":
        with tarfile.open(PATH_ARCHIVE, mode="r") as archive:
            archive.extractall(PATH_ARCHIVE.parent)
    elif encoding == "zip":
        try:
            with ZipFile(PATH_ARCHIVE, "r") as archive:
                archive.extractall(PATH_ARCHIVE.parent)
        except BadZipFile:
            logger.critical("The returned file is not a Zip file. Try again later.")
            PATH_ARCHIVE.unlink()
            return False


def _is_int_or_float(number):
    """Like isnumeric() for str but supports float."""
    try:
        float(number)
        return True
    except ValueError:
        return False


def convert_to_isot(dates):
    """Convert list of dates to ISOT format.

    Parameters
    ----------
    dates : str or list of str
        The dates to convert.
    format : str
        The current format string of the dates.
    """
    if pd.isna(dates) or not dates:
        return ""

    if isinstance(dates, str):
        dates = dates.split(",")

    FORMATS = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d_%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]

    converted = []

    for date in dates:
        for format in FORMATS:
            try:
                date = datetime.strptime(date, format).isoformat(sep="T")
                converted.append(date)
            except ValueError:
                continue
            else:
                break
        else:
            raise ValueError(f"Unknown time format: {dates}. Expected ISO-T.")
    date_obs = ",".join(converted)
    return date_obs
