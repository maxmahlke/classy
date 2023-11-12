import datetime

import pandas as pd
import pytest

import classy


# ------
# Index creation
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


# ------
# Index access and query
def test_query():
    """Test query results of index."""

    # Get spectra of a numbered asteroid
    spectra = classy.index.query(number=221)
    assert (spectra["number"] == 221).all()

    # Get spectra matching wavelength range, where wave_min and wave_max
    # are interpreted as lower and upper bounds respectively
    spectra = classy.index.query(wave_min=1.4, wave_max=2)
    assert (spectra.wave_min <= 1.4).all() and (spectra.wave_max >= 2).all()
    assert (spectra.wave_max > 2).any()

    # Get all spectra with wave_max between 2.4 and 3.0
    spectra = classy.index.query(query="2.4 < wave_max < 3")
    assert (2.4 < spectra.wave_max).all() and (3 > spectra.wave_max).all()

    # Get spectra based on shortbib and name
    spectra = classy.index.query(shortbib="Fornasier+ 2014", name="Zelinda")
    assert all(spectra["shortbib"] == "Fornasier+ 2014") and all(
        spectra["name"] == "Zelinda"
    )

    # Use comma-separated parameter limits
    spectra = classy.index.query(shortbib="Fornasier+ 2014,Marsset+ 2014")
    assert len(spectra) > 0
    assert all(s in ["Fornasier+ 2014", "Marsset+ 2014"] for s in spectra["shortbib"])

    spectra = classy.index.query(shortbib="Fornasier+ 2014", N="800,")
    assert len(spectra) > 0
    assert all(s in ["Fornasier+ 2014"] for s in spectra["shortbib"])
    assert all(N >= 800 for N in spectra["N"])

    spectra = classy.index.query(shortbib="Fornasier+ 2014", N="800,900")
    assert len(spectra) > 0
    assert all(s in ["Fornasier+ 2014"] for s in spectra["shortbib"])
    assert all(800 <= N <= 900 for N in spectra["N"])

    spectra = classy.index.query(shortbib="Fornasier+ 2014", N=",800")
    assert len(spectra) > 0
    assert all(s in ["Fornasier+ 2014"] for s in spectra["shortbib"])
    assert all(N <= 800 for N in spectra["N"])

    # Fail if unknown column is provided
    with pytest.raises(KeyError):
        spectra = classy.index.query(unknown_column=23)
