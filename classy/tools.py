import numpy as np


def find_nearest(array, value):
    """Return index of closest value to target value in array.

    https://stackoverflow.com/a/2566508
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


from functools import partial
from urllib.request import urlopen


def download_archive(URL, PATH_ARCHIVE, unpack=True, remove=True):
    """Download remote archive file to directory. Optionally unpack and remove the file.

    Parameters
    ----------
    columns : list
        List of str with column names.

    Returns
    -------
    list
        List containing all string elements which are numeric.
    """
    numeric_elements = []

    for column in columns:
        try:
            float(column)
        except ValueError:
            continue
        numeric_elements.append(column)
    return numeric_elements
