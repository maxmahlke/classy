import datetime

import pandas as pd
import pytest

import classy


@pytest.mark.parametrize(
    "source,number", [("AKARI", 64), ("M4AST", 123), ("SMASS", 2256)]
)
def test_number_of_spectra(source, number):
    """Ensure that the right number of spectra per source is cached."""
    idx = classy.index.load()

    assert len(idx[idx.source == source]) == number


def test_ensure_unique_filenames():
    """Ensure that there are no duplicated filenames in index."""
    idx = classy.index.load()

    assert len(idx.index.unique()) == len(idx)


@pytest.mark.parametrize(
    "prop", ["N", "wave_min", "wave_max", "source", "module", "shortbib", "bibcode"]
)
def test_ensure_non_NaN(prop):
    """Ensure that properties are all non-NaN and/or positive."""
    idx = classy.index.load()

    assert idx[idx.isna()][prop].count() == 0

    if prop in ["N", "wave_min", "wave_max"]:
        assert (idx[prop] > 0).all()


def test_date_obs():
    """Ensure that all observation dates are in ISOT format and occured before today."""
    idx = classy.index.load()

    for date_obs in idx.loc[~pd.isna(idx.date_obs), "date_obs"].values:
        for date in date_obs.split(","):
            try:
                date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                print(date_obs)
                assert False

            assert datetime.datetime.today() > date
