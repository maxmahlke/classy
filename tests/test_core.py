import numpy as np
import pandas as pd
import pytest

import classy


# ------
# User creates spectrum
def test_create_spectrum():
    """Create a single spectrum instance and test basic functionality."""
    wave = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
    refl = [0.85, 0.94, 1, 1.05, 1.02, 1.02, 1.04, 1.07, 1.1]

    spec = classy.Spectrum(wave, refl)
    assert len(spec) == 9

    refl_err = [0.85, 0.94, 1, 1.05, 1.02, 1.02, 1.04, 1.07, 1.1]
    spec.refl_err = refl_err

    spec.date_obs = "2020-02-01T00:00:00"  # adding metadata to existing spectrum
    assert spec.date_obs == "2020-02-01T00:00:00"


def test_create_spectrum_invalid_data():
    """Create a single spectrum instance passing invalid refl and wave values."""

    # Negative wavelength -> remove
    wave = [-1, 2, 3, 4]
    refl = [1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl)
    assert spec.wave.size == 3
    assert spec.refl.size == 3
    assert (spec.mask_valid == np.array([False, True, True, True])).all()

    # NaN wavelength -> remove
    wave = [np.nan, 2, 3, 4]
    refl = [1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl)
    assert spec.wave.size == 3
    assert spec.refl.size == 3
    assert (spec.mask_valid == np.array([False, True, True, True])).all()

    # Negative reflectance -> works
    wave = [1, 2, 3, 4]
    refl = [-1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl)
    assert spec.wave.size == 4
    assert spec.refl.size == 4
    assert (spec.mask_valid == np.array([True, True, True, True])).all()

    # NaN reflectance -> remove
    wave = [1, 2, 3, 4]
    refl = [np.nan, 2, np.nan, 4]
    spec = classy.Spectrum(wave, refl)
    assert spec.wave.size == 2
    assert spec.refl.size == 2
    assert (spec.mask_valid == np.array([False, True, False, True])).all()


def test_create_spectrum_with_target():
    """Create a single spectrum instance including rocks data look-up."""
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]

    spec = classy.Spectrum(wave, refl, target=1)
    assert spec.target.name == "Ceres"

    spec.set_target(2)
    assert spec.target.name == "Pallas"


def test_create_spectrum_with_arbitrary_arg():
    """Create a single spectrum instance including rocks data look-up."""
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl, arbitrary=1)
    assert spec.arbitrary == 1


# ------
# Spectra from index query
def test_spectra_with_single_id():
    """Test creating a Spectra instance by passing an asteroid identifier."""
    spectra = classy.Spectra(1, source="Gaia")
    assert len(spectra) == 1
    assert spectra[0].target.name == "Ceres"

    vesta1 = classy.Spectra(4)
    assert all(s.target.name == "Vesta" for s in vesta1)

    vesta2 = classy.Spectra("vesta")
    assert all(s.target.name == "Vesta" for s in vesta2)

    spectra = classy.Spectra(22, wave_min=0.45, wave_max=2.45)
    assert all(s.target.name == "Kalliope" and s.wave.min() < 0.45 for s in spectra)


def test_spectra_with_many_id():
    """Test creating a Spectra instance by passing an asteroid identifier."""
    spectra = classy.Spectra([1, "vesta", 22], source="Gaia")
    assert len(spectra) == 3
    assert spectra[0].target.name == "Ceres"

    spectra = classy.Spectra([12, 21])
    assert all(s.target.name in ["Victoria", "Lutetia"] for s in spectra)

    spectra = classy.Spectra(["julia", "sylvia", 283])
    assert all(s.target.name in ["Sylvia", "Julia", "Emma"] for s in spectra)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"source": "AKARI"},
        {"albedo": "0.03,0.031", "skip_target": True},
        # {"phase": ",10", "skip_target": True},
        {"albedo": "0.1,0.101", "taxonomy": "B,C", "skip_target": True},
        {"wave_min": 0.35, "taxonomy": "B,C", "skip_target": True},
        {
            "query": "wave_min < 0.35 & (taxonomy == 'B' | taxonomy == 'C')",
            "skip_target": True,
        },
        {
            "family": "Tirela,Watsonia",
            "query": "taxonomy != 'L'",
            "wave_max": 2,
            "skip_target": True,
        },
        # TODO: Reenable once feature index is available online
        # {"family": "Themis", "feature": "h", "skip_target": True},
        {"query": "moid.EMB.value <= 0.05", "H": ",22", "skip_target": True},
    ],
)
def test_spectra_with_no_id(kwargs):
    """Test creating a Spectra instance by passing an asteroid identifier."""
    spectra = classy.Spectra(**kwargs)
    assert len(spectra) > 0


# ------
# Spectra interoperability
def test_spectra_from_list():
    """Test creating a Spectra instance from a list of Spectrum instances."""
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]

    spec_a = classy.Spectrum(wave, refl)
    spec_b = classy.Spectrum(wave, refl)

    classy.Spectra([spec_a, spec_b])


def test_adding_spectra():
    """Test different spectra addition cases."""
    wave = [1, 2, 3, 4]
    refl = [1, 2, 3, 4]

    spec_a = classy.Spectrum(wave, refl)
    spec_b = classy.Spectrum(wave, refl)

    # Spectrum + Spectrum -> Spectra
    spectra = spec_a + spec_b
    assert isinstance(spectra, classy.Spectra)
    assert len(spectra) == 2

    # Spectra + Spectrum -> Spectra
    spectra = spectra + spec_a
    assert isinstance(spectra, classy.Spectra)
    assert len(spectra) == 3

    # Spectra + Spectra -> Spectra
    spectra = spectra + spectra
    assert isinstance(spectra, classy.Spectra)
    assert len(spectra) == 6


# ------
# Spectra functionality
def test_export():
    """Test export functionality"""

    def mock_to_csv(*args, **kwargs):
        pass

    pd.DataFrame.to_csv = mock_to_csv

    spectra = classy.Spectra(31)
    spectra.classify()
    spectra.export("testing.csv")
