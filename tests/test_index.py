import pytest


@pytest.parametrize("source,number", [("AKARI", 64), ("M4ST", 123)])
def test_number_of_spectra(source, number):
    """Ensure that the right number of spectra per source is cached."""


def test_ensure_unique_filenames():
    """Ensure that there are no duplicated filenames in index."""


def test_ensure_non_NaN():
    N, wave_min, wave_max, source, filename, module
