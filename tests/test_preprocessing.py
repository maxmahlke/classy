import numpy as np
import pytest

import classy


def test_normalize():
    """Test normalization methods."""

    spectra = classy.Spectra("Chloe", shortbib="DeMeo+ 2009")
    spec = spectra[0]

    spec.normalize(at=spec.wave[10])
    assert spec.refl[10] == 1

    spec.normalize(method="l2")
    assert np.linalg.norm(spec.refl) == 1


def test_truncate():
    """Test truncation method."""

    spectra = classy.Spectra("Chloe", shortbib="DeMeo+ 2009")
    spec = spectra[0]

    spec.truncate(wave_min=0.9)
    spec.truncate(wave_max=1.2)

    assert spec.wave.min() > 0.9
    assert spec.wave.max() < 1.2


def test_smooth():
    """Test smoothing"""

    # TODO:
    # Test parameter loading
    # Test parameter storing
    # Test command line interface


def test_resampling():
    """Test resampling of spectrum."""

    spectra = classy.Spectra("Chloe", shortbib="DeMeo+ 2009")
    spec = spectra[0]

    wave_new = classy.taxonomies.demeo.WAVE
    spec.resample(wave_new)

    assert spec[0] == wave_new[0]
    assert spec[-1] == wave_new[-1]

    assert spec.refl_err is None


def test_slope_removal():
    """Test removing slope of spectrum."""

    spectra = classy.Spectra("Chloe", shortbib="DeMeo+ 2009")
    spec = spectra[0]

    spec.remove_slope()
    assert hasattr(spec, "slope")
    assert spec.slope[0] == pytest.approx(0.068)
