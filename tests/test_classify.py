from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import classy


def test_export():
    """Test export functionality"""

    def mock_to_csv(*args, **kwargs):
        pass

    pd.DataFrame.to_csv = mock_to_csv

    spectra = classy.Spectra(31)
    spectra.classify()
    spectra.export("testing.csv")


PATH_TEST_DATA = Path().home() / "astro/cclassy/tests/data/"


def _create_name_expected_class_list():
    """Create list of tuples for classification-result test."""
    data = pd.read_csv(PATH_TEST_DATA / "spectra_preprocessed.csv")
    # return [(row["name"], row["class_"]) for _, row in data.iterrows()]
    return [("Nysa", "E")]


# def test_gaia():
# spec = classy.Spectra(3)[0]
# spec.classify()


@pytest.mark.parametrize(
    "name, pV, class_expected",
    [
        ("Ceres", 0.034, "G"),
        ("Pallas", 0.14, "B"),
        ("Juno", 0.23, "S"),
        ("Vesta", 0.26, "V"),
        ("Hygiea", 0.04, "C"),
        ("Psyche", 0.12, "M"),
        ("Thule", 0.04, "D"),
        ("Hestia", 0.04, "P"),
        ("Virginia", np.nan, "X"),
        ("Polana", 0.05, "F"),
        ("Nysa", 0.4, "E"),
        ("Apollo", 0.23, "Q"),
        ("Asporina", 0.25, "A"),
        ("Kassandra", 0.1, "T"),
        ("Dembowska", 0.23, "R"),
    ],
)
@pytest.mark.skip(reason="currently broken")
def test_tholen(name, pV, class_expected):
    """Classify locally stored ECAS data and verify the most-likely Tholen class."""

    # Load test data
    colors = pd.read_csv(PATH_TEST_DATA / "ecas_colors.csv")

    # Code copied from module because mocking pd.read_csv is hard
    obs = colors.loc[colors["name"] == name]
    wave = classy.sources.pds.ecas.WAVE
    refl, refl_err = classy.sources.pds.ecas._compute_reflectance_from_colors(obs)
    flags = classy.sources.pds.ecas._add_flags(obs)

    data = pd.DataFrame(
        data={
            "refl": refl[~np.isnan(refl)],
            "refl_err": refl_err[~np.isnan(refl)],
            "wave": np.array(wave)[~np.isnan(refl)],
            "flag": flags[~np.isnan(refl)],
        },
    )

    # Load spectrum and classify
    spec = classy.Spectrum(
        wave=data["wave"],
        refl=data["refl"],
        refl_err=data["refl_err"],
        name=name,
        number=0,  # prevent rocks call
        pV=pV,  # prevent rocks call
    )
    spec.classify(taxonomy="tholen")

    # Verify
    assert spec.class_tholen == class_expected


DEMEO_CLASSES = {
    "A": "",
    "B": "",
    "Cg": "",
    "Cgh": "",
    "C": "",
    "Cb": "",
    "D": "",
    "K": "",
    "L": "",
    "Q": "",
    "S": "",
    "Sa": "",
    "Sq": "",
    "Sqw": "",
    "Sr": "",
    "Srw": "",
    "Sv": "",
    "Svw": "",
    "Sw": "",
    "V": "",
    "T": "",
    "X": "",
    "Xe": "",
    "Xk": "una",
}


# @pytest.mark.parametrize("name, class_expected", DEMEO_CLASSES)
# def test_demeo_classification(name, class_expected):
#     """Classify asteroids in DeMeo+ 2009 and verify the result."""
