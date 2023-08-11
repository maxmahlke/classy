import numpy as np
import pytest
import classy


def test_create_spectrum():
    """Create a single spectrum instance including rocks data look-up."""
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl)
    assert len(spec) == 4


def test_create_spectrum_invalid_data():
    """Create a single spectrum instance passing invalid refl and wave values."""
    wave = [-1, 2, 3, 4]
    refl = [1, -2, 3, 4]
    spec = classy.Spectrum(wave, refl, name=1)

    # Negative values should be removed -> two points in spectrum gone
    assert spec.wave.size == 2
    assert spec.refl.size == 2


def test_create_spectrum_with_rocks():
    """Create a single spectrum instance including rocks data look-up."""
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl, number=1)
    assert spec.name == "Ceres"


def test_spectra_from_id():
    """Test creating a Spectra instance by passing an asteroid identifier."""
    spectra = classy.Spectra(1, source="Gaia")
    assert len(spectra) == 1
    assert spectra[0].name == "Ceres"


def test_spectra_from_index():
    """Test creating a Spectra instance from the classy index."""
    idx = classy.index.load()
    idx = idx.loc[(idx.source == "SMASS") & (idx.name == 5534)]
    classy.Spectra(idx)


def test_spectra_from_list():
    """Test creating a Spectra instance from a list of Spectrum instances."""
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]

    spec_a = classy.Spectrum(wave, refl)
    spec_b = classy.Spectrum(wave, refl)

    classy.Spectra([spec_a, spec_b])


def test_adding_spectra():
    """Test different spectra addition cases.

    Spectrum + Spectrum -> Spectra
    Spectra + Spectrum -> Spectra
    Spectra + Spectra -> Spectra
    """
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]

    spec_a = classy.Spectrum(wave, refl)
    spec_b = classy.Spectrum(wave, refl)

    spectra = spec_a + spec_b
    assert isinstance(spectra, classy.Spectra)

    spectra = spectra + spec_a
    assert isinstance(spectra, classy.Spectra)
    assert len(spectra) == 3

    spectra = spectra + spectra
    assert isinstance(spectra, classy.Spectra)
    assert len(spectra) == 6
