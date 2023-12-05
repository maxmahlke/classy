import datetime
import shutil

import pandas as pd
import pytest

import classy


def test_00build_pds():
    """Test building PDS source index."""

    # Copy cached PDS archives
    if not (pytest.PATH_TEST / "pds").is_dir():
        shutil.copytree(pytest.PATH_DATA / "index/pds", pytest.PATH_TEST / "pds")

    # And build
    classy.sources.pds._retrieve_spectra()
    classy.sources.pds._build_index()

    # Assert based on number of spectra indexed
    idx = pd.read_csv(pytest.PATH_TEST / "index.csv")

    for source, count in [
        ("S3OS2", 820),
        ("ECAS", 589),
        ("PRIMASS", 437),
        ("24CAS", 285),
        ("SCAS", 126),
        ("52CAS", 119),
    ]:
        assert len(idx[idx.source == source]) == count


def test_00build_cds():
    """Test building CDS source index."""

    # Copy cached PDS archives
    if not (pytest.PATH_TEST / "cds").is_dir():
        shutil.copytree(pytest.PATH_DATA / "index/cds", pytest.PATH_TEST / "cds")

    # And build
    classy.sources.cds._retrieve_spectra()
    classy.sources.cds._build_index()

    # Assert based on number of spectra indexed
    idx = pd.read_csv(pytest.PATH_TEST / "index.csv")

    for host, count in [("CDS", 93)]:
        assert len(idx[idx.host == host]) == count


def test_00build_m4ast():
    """Test building M4AST source index."""

    # Copy cached PDS archives
    if not (pytest.PATH_TEST / "m4ast").is_dir():
        shutil.copytree(pytest.PATH_DATA / "index/m4ast", pytest.PATH_TEST / "m4ast")

    # And build
    classy.sources.m4ast._build_index()

    # Assert based on number of spectra indexed
    idx = pd.read_csv(pytest.PATH_TEST / "index.csv")

    for source, count in [("M4AST", 123)]:
        assert len(idx[idx.source == source]) == count


def test_00build_akari():
    """Test building akari source index."""

    # Copy cached PDS archives
    if not (pytest.PATH_TEST / "akari").is_dir():
        shutil.copytree(pytest.PATH_DATA / "index/akari", pytest.PATH_TEST / "akari")

    # And build
    classy.sources.akari._retrieve_spectra()
    classy.sources.akari._build_index()

    # Assert based on number of spectra indexed
    idx = pd.read_csv(pytest.PATH_TEST / "index.csv")

    for source, count in [("AKARI", 64)]:
        assert len(idx[idx.source == source]) == count


def test_00build_smass():
    """Test building smass source index."""

    # Copy cached PDS archives
    if not (pytest.PATH_TEST / "smass").is_dir():
        shutil.copytree(pytest.PATH_DATA / "index/smass", pytest.PATH_TEST / "smass")

    # And build
    classy.sources.smass._retrieve_spectra()
    classy.sources.smass._build_index()

    # Assert based on number of spectra indexed
    idx = pd.read_csv(pytest.PATH_TEST / "index.csv")

    for source, count in [("SMASS", 2256)]:
        assert len(idx[idx.source == source]) == count


def test_00build_mithneos():
    """Test building mithneos source index."""

    # Copy cached PDS archives
    if not (pytest.PATH_TEST / "mithneos").is_dir():
        shutil.copytree(
            pytest.PATH_DATA / "index/mithneos", pytest.PATH_TEST / "mithneos"
        )

    # And build
    classy.sources.mithneos._retrieve_spectra()
    classy.sources.mithneos._build_index()

    # Assert based on number of spectra indexed
    idx = pd.read_csv(pytest.PATH_TEST / "index.csv")

    for source, count in [("MITHNEOS", 1911)]:
        assert len(idx[idx.source == source]) == count


@pytest.mark.slow
def test_00build_gaia():
    """Test building gaia source index."""

    # Copy cached PDS archives
    if not (pytest.PATH_TEST / "gaia").is_dir():
        shutil.copytree(pytest.PATH_DATA / "index/gaia", pytest.PATH_TEST / "gaia")

    # And build
    classy.sources.gaia._retrieve_spectra()
    classy.sources.gaia._build_index()

    # Assert based on number of spectra indexed
    idx = pd.read_csv(pytest.PATH_TEST / "index.csv")

    for source, count in [("Gaia", 60518)]:
        assert len(idx[idx.source == source]) == count


def test_00add_private():
    """Test adding private modules."""
    PATH = pytest.PATH_DATA / "index/fornasier2014/index.csv"
    classy.sources.private.parse_index(PATH)

    PATH = pytest.PATH_DATA / "index/demeo2009/index.csv"
    classy.sources.private.parse_index(PATH)


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
    with pytest.raises(ValueError):
        spectra = classy.index.query(unknown_column=23)
