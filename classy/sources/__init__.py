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


def _retrieve_spectra():
    """Retrieve all spectra that classy knows about."""
    # pds._retrieve_spectra()
    # cds._retrieve_spectra()
    m4ast._retrieve_spectra()
    # akari._retrieve_spectra()
    # smass._retrieve_spectra()
    # mithneos._retrieve_spectra()
    # gaia._retrieve_spectra()
