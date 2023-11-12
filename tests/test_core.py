import numpy as np
import pytest
import classy


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
    assert len(spectra) == 1
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

           >>> classy.Spectra(4)
            >>> classy.Spectra("vesta")                  # (4) Vesta
            >>> classy.Spectra([12, 21])                 # (12) Victoria, (21) Lutetia
            >>> classy.Spectra(["julia", "sylvia", 283]) # (87) Sylvia, (89) Julia, (283) Emma
            >>> classy.Spectra(albedo="0.03,0.04")
            >>> classy.Spectra(phase=',10')
           >>> classy.Spectra(22, wave_min=0.45, wave_max=2.45)
            >>> classy.Spectra(albedo="0.1,", taxonomy="B,C")
           >>> classy.Spectra(wave_min=0.3, taxonomy="B,C")
           >>> classy.Spectra(query="wave_min < 0.3 & (taxonomy == 'B' | taxonomy == 'C')") # equivalent
            >>> classy.Spectra(family="Tirela,Watsonia", query="taxonomy != 'L'")
           >>> classy.Spectra(family="Polana", feature="h")
            >>> classy.Spectra(query='moid.EMB.value <= 0.05', H=',22')

# ------
# User creates spectrum
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
