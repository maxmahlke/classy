import numpy as np
import pandas as pd

from classy import config
from classy import core
from classy import sources

from . import akari, cds, gaia, m4ast, mithneos, pds, private, smass

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
    """Retrieve all public spectra that classy knows about."""
    for module in [pds, cds, m4ast, akari, smass, mithneos, gaia]:
        module._retrieve_spectra()


def load_data(idx):
    """Load data and metadata of a cached spectrum.

    Parameters
    ----------
    idx : pd.Series
        A row from the classy spectra index.

    Returns
    -------
    pd.DataFrame, dict
        The data and metadata. List-like attributes are in the dataframe,
        single-value attributes in the dictionary.
    """

    host = (
        getattr(sources, idx.host.lower())
        if idx.host.lower() in ["pds", "cds"]
        else sources
    )
    module = getattr(host, idx.module.lower())

    # Load spectrum data file
    PATH_DATA = config.PATH_CACHE / idx.name

    if module is not private:
        data = pd.read_csv(PATH_DATA, **module.DATA_KWARGS)
    else:
        data = _load_private_data(PATH_DATA)
    data = data[data.wave > 0]

    # Apply module specific data transforms and get metadata if necessary
    if hasattr(module, "_transform_data"):
        data, meta = module._transform_data(idx, data)
    else:
        meta = {}

    return data, meta


def _load_private_data(PATH):
    # Try two different delimiters
    try:
        data = np.loadtxt(PATH)
    except ValueError:
        data = np.loadtxt(PATH, delimiter=",")

    data = pd.DataFrame(data)

    # Rename the columns that are present
    COLS = ["wave", "refl", "refl_err", "flag"]
    data = data.rename(columns={col: COLS.pop(0) for col in data.columns})
    return data


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

    # Load data and metadata
    data, meta = load_data(idx)

    # Add list-type attributes when instantiating
    spec = core.Spectrum(name=idx["name"], **{col: data[col] for col in data.columns})

    # Add metadata from index
    for attr in ["shortbib", "bibcode", "host", "source", "date_obs"]:
        setattr(spec, attr, idx[attr])

    spec.filename = idx.name

    # Add collection-specific metadata
    for attr, value in meta.items():
        setattr(spec, attr, value)
    return spec


def _add_spectra_properties(entries):
    """Add the spectral range properties to a dataframe of index entries."""

    for ind, entry in entries.iterrows():
        data, _ = load_data(entry)
        entries.loc[ind, "wave_min"] = min(data["wave"])
        entries.loc[ind, "wave_max"] = max(data["wave"])
        entries.loc[ind, "N"] = len(data)

    return entries
