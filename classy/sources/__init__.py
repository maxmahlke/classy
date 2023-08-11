import pandas as pd

from . import akari, cds, gaia, m4ast, mithneos, pds, private, smass
from .pds import ecas, primass, s3os2

SOURCES = [
    "24CAS",
    "52CAS",
    "AKARI",
    "CDS",
    "ECAS",
    "Gaia",
    "M4AST",
    "MITHNEOS",
    "Misc",
    "PRIMASS",
    "S3OS2",
    "SCAS",
    "SMASS",
]


def load_spectrum(spec):
    """Load a cached spectrum.

    Parameters
    ----------
    spec : pd.Series

    Returns
    -------
    astro.core.Spectrum
    """
    PATH_SPEC = config.PATH_CACHE / f"{spec.filename}"

    data = _load_data(PATH_SPEC)
    spec = core.Spectrum(
        wave=data.wave.values,
        refl=data.refl.values,
        refl_err=data.refl_err.values,
        flag=data.flag.values,
        source="AKARI",
        name=spec["name"],
        number=spec.number,
        shortbib="Usui+ 2019",
        bibcode="2019PASJ...71....1U",
        flag_err=data.flag_err.values,
        flag_saturation=data.flag_saturation.values,
        flag_thermal=data.flag_thermal.values,
        flag_stellar=data.flag_stellar.values,
        host="akari",
    )

    return spec


def _load_data(PATH_SPEC, **kwargs):
    """Load spectrum from file.

    Parameters
    ----------
    PATH_SPEC : pathlib.Path
        The path to the spectrum.

    Returns
    -------
    pd.DataFrame
        The spectrum.

    Notes
    -----
    kwargs are passed to pd.read_csv.
    """
    data = pd.read_csv(PATH_SPEC, **kwargs)
    return data


def _retrieve_spectra():
    """Retrieve all public spectra that classy knows about."""
    # pds._retrieve_spectra()
    # cds._retrieve_spectra()
    m4ast._retrieve_spectra()
    # akari._retrieve_spectra()
    # smass._retrieve_spectra()
    # mithneos._retrieve_spectra()
    # gaia._retrieve_spectra()
