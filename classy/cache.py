"""Cache management for classy."""

from pathlib import Path

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy.log import logger
from classy import core
from classy import sources


# ------
# Indeces of spectra
def load_index(source):
    """Load an index file."""
    if source not in sources.SOURCES:
        raise ValueError(
            f"Unknown spectra source '{source}'. Choose one of {sources.SOURCES}."
        )

    return getattr(sources, source.lower()).load_index()


def load_mahlke_index():
    """Load the index of spectra from Mahlke+ 2022."""
    PATH_INDEX = config.PATH_CACHE / "mahlke/index.csv"
    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


# ------
# Load spectra from cache
def load_spectra(idx_spectra):
    """Load a spectrum from a known source.

    Returns
    -------
    list of classy.core.Spectrum
    """

    spectra = [
        getattr(sources, spec.source.lower()).load_spectrum(spec)
        for _, spec in idx_spectra.iterrows()
    ]

    return spectra
