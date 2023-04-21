PDS_REPOSITORIES = {
    "vilas": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.vilas.spectra.zip",
    "SAWYER": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.sawyer.spectra_V1_0.zip",
    "FORNASIER": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast-m-type.fornasier.spectra.zip",
}

import io
import zipfile

import pandas as pd
import requests
import rocks

from classy import config
from classy import core
from classy.log import logger
from classy import tools


def load_index():
    """Load the PDS reflectance spectra index."""

    PATH_INDEX = config.PATH_CACHE / "pds/index.csv"

    if not PATH_INDEX.is_file():
        retrieve_spectra()

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


def load_spectrum(spec):
    """Load a cached PDS spectrum."""
    spec = getattr(classy.sources, f"pds_{collection}").load_spectrum()
    spec._source = "PDS"
    return spec


def retrieve_spectra():
    """Retrieve all PDS spectra to pds/ the cache directory."""

    # Create directory structure and check if the spectrum is already cached
    PATH_PDS = config.PATH_CACHE / "pds/"
    PATH_PDS.mkdir(parents=True, exist_ok=True)

    logger.info("Retrieving PDS reflectance spectra to cache...")
    index = pd.DataFrame()

    for collection, url in PDS_REPOSITORIES.items():
        PATH_ARCHIVE = PATH_PDS / url.split("/")[-1]

        # Download repository
        tools.download(url, PATH_ARCHIVE)

        # Extract to cache
        files = zipfile.ZipFile(PATH_ARCHIVE)
        files.extractall(PATH_PDS)

        # Remove the zip
        PATH_ARCHIVE.unlink()

        # Append to index
        # index = getattr(classy.sources, f"pds_{collection}").compute_index()

    # All done
    # index["number"] = index["number"].astype("Int64")
    # index.to_csv(PATH_PDS / "index.csv", index=False)
