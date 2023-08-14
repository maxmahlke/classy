from classy import core
from classy import sources

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


def load_spectrum(idx):
    """Load a cached spectrum. This general function applies host- and
    collection specific parameters defined in the colecction modules.

    Parameters
    ----------
    idx : pd.Series
        A row from the classy spectra index.

    Returns
    -------
    classy.Spectrum
        The requested spectrum.
    """

    # Resolve where to look for the data and spectrum kwargs based on host module
    host = (
        getattr(sources, idx.host.lower())
        if idx.host.lower() in ["pds", "cds"]
        else sources
    )
    module = getattr(host, idx.module.lower())

    # Load data and metadata
    data, meta = module._load_data(idx)

    # ------
    # Instantiate spectrum

    # Add list-type attributes when instantiating
    spec = core.Spectrum(name=idx["name"], **{col: data[col] for col in data.columns})
    # Add metadata from index
    for attr in ["shortbib", "bibcode", "host", "source", "date_obs", "filename"]:
        setattr(spec, attr, idx[attr])

    # Add collection-specific metadata
    for attr, value in meta.items():
        setattr(spec, attr, value)
    return spec


def _retrieve_spectra():
    """Retrieve all public spectra that classy knows about."""
    pds._retrieve_spectra()
    cds._retrieve_spectra()
    m4ast._retrieve_spectra()
    akari._retrieve_spectra()
    smass._retrieve_spectra()
    mithneos._retrieve_spectra()
    gaia._retrieve_spectra()
