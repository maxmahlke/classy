from . import akari, gaia, mithneos, pds, private, smass
from .pds import ecas, primass, s3os2

from classy import index

SOURCES = [
    "24CAS",
    "52CAS",
    "AKARI",
    "ECAS",
    "Gaia",
    "MITHNEOS",
    "Misc",
    "PRIMASS",
    "S3OS2",
    "SCAS",
    "SMASS",
]


def _retrieve_spectra():
    """Retrieve all spectra that classy knows about."""
    pds._retrieve_spectra()
    akari._retrieve_spectra()
    smass._retrieve_spectra()
    mithneos._retrieve_spectra()
    gaia._retrieve_spectra()
