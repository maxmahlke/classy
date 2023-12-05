"""Test source retrieval and access."""
import numpy as np
import pytest

import classy


def test_no_nan_names():
    """No NaN values in asteroid names."""
    idx = classy.index.load()
    any_null = idx["name"].isnull().values.any()
    assert not any_null


@pytest.mark.parametrize("column", ["N", "wave_min", "wave_max"])
def test_wave_parameters(column):
    """Ensure that wave parameters in index make sense."""
    idx = classy.index.load()

    assert all(idx[column] > 0)
    assert not idx[column].isnull().values.any()

    if column == "N":
        assert np.array_equal(idx[column], idx[column].astype(int))


def create_one_of_each():
    """Create list of one asteroid per shortbib in classy index."""
    idx = classy.index.load()

    idx = idx.drop_duplicates("shortbib")
    return [(row["name"], row.shortbib) for _, row in idx.iterrows()]


# @pytest.mark.parametrize("name, shortbib", create_one_of_each())
# def test_access(name, shortbib):
#     """For each shortbib, access one spectrum and some metadata."""
#
#     classy.Spectra(name, shortbib=shortbib)
