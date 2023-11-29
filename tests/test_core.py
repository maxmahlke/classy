import numpy as np
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

    # NaN wavelength -> remove
    wave = [np.nan, 2, 3, 4]
    refl = [1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl)
    assert spec.wave.size == 3
    assert spec.refl.size == 3

    # Negative reflectance -> works
    wave = [1, 2, 3, 4]
    refl = [-1, 2, 3, 4]
    spec = classy.Spectrum(wave, refl)
    assert spec.wave.size == 4
    assert spec.refl.size == 4

    # NaN reflectance -> remove
    wave = [1, 2, 3, 4]
    refl = [np.nan, 2, 3, 4]
    spec = classy.Spectrum(wave, refl)
    assert spec.wave.size == 3
    assert spec.refl.size == 3


def test_create_with_nans():
    """Create spectrum with NaN wavelengths and reflectances."""
    wave = [np.nan, 2, 3, 4]
    refl = [1, np.nan, 3, 4]
    spec = classy.Spectrum(wave, refl)

    # Negative values should be removed -> two points in spectrum gone
    # TODO: Think about what should happen here
    assert spec.wave.size == 2
    assert spec.refl.size == 2


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


def test_compute_phase_anlge():
    """Test phase angle query from Miriade"""


# ------
# Spectra from index query
def test_spectra_with_single_id():
    """Test creating a Spectra instance by passing an asteroid identifier."""
    spectra = classy.Spectra(1, source="Gaia")
    assert len(spectra) == 1
    assert spectra[0].name == "Ceres"


def test_spectra_with_many_id():
    """Test creating a Spectra instance by passing an asteroid identifier."""
    spectra = classy.Spectra([1, "vesta", 22], source="Gaia")
    assert len(spectra) == 3
    assert spectra[0].name == "Ceres"


def test_spectra_with_no_id():
    """Test creating a Spectra instance by passing an asteroid identifier."""
    spectra = classy.Spectra(source="AKARI")
    assert len(spectra) > 0


def test_spectra_from_index():
    """Test creating a Spectra instance from the classy index."""
    idx = classy.index.load()
    idx = idx.loc[(idx.source == "SMASS") & (idx.name == 5534)]
    classy.Spectra(idx)


def test_spectra_from_invalid():
    """Test creating a Spectra instance from an empty list."""

    # TODO: Assert the correct errors here
    classy.Spectra([])
    classy.Spectra(None)
    classy.Spectra(np.nan)


def test_doc_scenarios():
    """Examples given in selecting-spectra chapter."""
    # TODO: Merge with other unit tests
    # >>> classy.Spectra(4)
    # >>> classy.Spectra("vesta")                  # (4) Vesta
    # >>> classy.Spectra([12, 21])                 # (12) Victoria, (21) Lutetia
    # >>> classy.Spectra(["julia", "sylvia", 283]) # (87) Sylvia, (89) Julia, (283) Emma
    # >>> classy.Spectra(albedo="0.03,0.04")
    # >>> classy.Spectra(phase=',10')
    # >>> classy.Spectra(22, wave_min=0.45, wave_max=2.45)
    # >>> classy.Spectra(albedo="0.1,", taxonomy="B,C")
    # >>> classy.Spectra(wave_min=0.3, taxonomy="B,C")
    # >>> classy.Spectra(query="wave_min < 0.3 & (taxonomy == 'B' | taxonomy == 'C')") # equivalent
    # >>> classy.Spectra(family="Tirela,Watsonia", query="taxonomy != 'L'")
    # >>> classy.Spectra(family="Polana", feature="h")
    # >>> classy.Spectra(query='moid.EMB.value <= 0.05', H=',22')


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
