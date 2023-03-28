import numpy as np


def find_nearest(array, value):
    """Return index of closest value to target value in array.

    https://stackoverflow.com/a/2566508
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


def get_numeric_columns(columns):
    """Identify numeric string elements in a list.

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
