from pathlib import Path

import numpy as np
import pytest

from classy.feature import Feature
from classy import defs, Spectrum

PATH_TEST_DATA = Path().home() / "astro/cclassy/tests/data/"

SPECTRA = [
    ("smass2_13.txt", "h"),
    ("smass2_19.txt", "h"),
    ("smass2_48.txt", "h"),
    ("smass2_51.txt", "h"),
    ("smass2_130.txt", "h"),
]


def test_is_oberved():
    """Test the wavelength range check of the feature detection. Uses fake wavelength ranges."""

    # To pass, the wavelength needs to cover the entire feature range
    # and to have at least 4 datapoints inside this range.

    # Checking for one feature is sufficient
    dense = np.linspace(0.4, 0.6, 100)
    sparse = np.linspace(0.4, 0.6, 5)
    below_upper_limit = np.linspace(0.4, defs.FEATURE["e"]["upper"] - 0.05, 10)
    above_lower_limit = np.linspace(defs.FEATURE["e"]["lower"] + 0.05, 0.6, 10)

    for wave, is_observed in [
        (dense, True),
        (sparse, False),
        (below_upper_limit, False),
        (above_lower_limit, False),
    ]:
        feature = Feature("e", wave, np.ones(wave.shape))
        assert feature.is_observed == is_observed


@pytest.mark.parametrize("filename, feature", SPECTRA)
def test_is_present(filename, feature):
    """Check if feature is present in spectrum.

    Parameters
    ----------
    filename : str
        Filename of spectrum relative to tests/data
    feature : str
        Feature name, one of ('e', 'h', 'k')
    """
    data = np.loadtxt(PATH_TEST_DATA / filename)
    wave = data[:, 0]
    refl = data[:, 1]

    spec = Spectrum(wave=wave, refl=refl)
    getattr(spec, feature).fit()
    getattr(spec, feature).plot(save="/tmp/feature_fit_polynomial.png")

    getattr(spec, feature).fit(method="gaussian")
    getattr(spec, feature).plot(save="/tmp/feature_fit_gaussian.png")

    assert getattr(spec, feature).is_present
