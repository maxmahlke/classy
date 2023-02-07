"""Cache management for classy."""

from pathlib import Path

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy.logging import logger


# ------
# Indeces of spectra
def load_index(which):
    """Load an index file."""
    if which == "Gaia":
        return load_gaia_index()
    elif which == "SMASS":
        return load_smass_index()
    else:
        raise ValueError(f"Unknown index '{which}'. Choose one of ['SMASS', 'Gaia'].")


def load_gaia_index():
    """Load the Gaia DR3 reflectance spectra index."""

    PATH_INDEX = config.PATH_CACHE / "gaia/index.csv"

    if not PATH_INDEX.is_file():
        retrieve_gaia_spectra()

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


def load_smass_index():
    """Load the SMASS reflectance spectra index."""

    PATH_INDEX = config.PATH_CACHE / "smass/index.csv"

    # if not PATH_INDEX.is_file():
    #     retrieve_gaia_spectra()

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


# ------
# Load spectra from cache
def load_spectrum(spec):
    """Load a spectrum from a known source."""

    if spec.source == "Gaia":
        return load_gaia_spectrum(spec)
    elif spec.source == "SMASS":
        return load_smass_spectrum(spec)


def load_gaia_spectrum(spec):
    """Load a cached Gaia spectrum."""
    PATH_SPEC = config.PATH_CACHE / f"gaia/{spec.filename}.csv"

    obs = pd.read_csv(PATH_SPEC, dtype={"reflectance_spectrum_flag": int})
    obs = obs.loc[obs["name"] == spec["name"]]

    data = np.array(
        [
            obs.wavelength.values,
            obs.reflectance_spectrum.values,
            obs.reflectance_spectrum_err.values,
            obs.reflectance_spectrum_flag.values,
        ]
    )
    return data


def load_smass_spectrum(spec):
    """Load a cached SMASS spectrum."""
    PATH_SPEC = config.PATH_CACHE / f"smass/{spec.run}/{spec.filename}"

    if not PATH_SPEC.is_file():
        retrieve_smass_spectrum(spec)

    return np.loadtxt(PATH_SPEC, delimiter=",", skiprows=1)


# ------
# Downloading spectra from source
def retrieve_gaia_spectra():
    """Retrieve Gaia DR3 reflectance spectra to cache."""

    logger.info("Retrieving Gaia DR3 reflectance spectra [13MB] to cache...")

    # Create directory structure
    PATH_GAIA = config.PATH_CACHE / "gaia"
    PATH_GAIA.mkdir(parents=True, exist_ok=True)

    # Retrieve observations
    URL = "http://cdn.gea.esac.esa.int/Gaia/gdr3/Solar_system/sso_reflectance_spectrum/SsoReflectanceSpectrum_"

    index = {}

    # Observations are split into 20 parts
    for idx in range(20):

        # Retrieve the spectra
        part = pd.read_csv(f"{URL}{idx:02}.csv.gz", compression="gzip", comment="#")

        # Create list of identifiers from number and name columns
        ids = part.number_mp.fillna(part.denomination).values
        names, numbers = zip(*rocks.id(ids))

        part["name"] = names
        part["number"] = numbers

        # Add to index for quick look-up
        for name, entries in part.groupby("name"):

            # Use the number for identification if available, else the name
            number = entries.number.values[0]
            asteroid = number if number else name

            index[asteroid] = f"SsoReflectanceSpectrum_{idx:02}"

        # Store to cache
        part.to_csv(PATH_GAIA / f"SsoReflectanceSpectrum_{idx:02}.csv", index=False)

    # Convert index to dataframe, store to cache
    names, numbers = zip(*rocks.identify(list(index.keys())))
    index = pd.DataFrame(
        data={"name": names, "number": numbers, "filename": list(index.values())}
    )
    index.to_csv(PATH_GAIA / "index.csv", index=False)


def retrieve_smass_spectrum(spec):
    """Retrieve a SMASS spectra from smass.mit.edu.

    Parameters
    ----------
    spec : pd.Series
        Entry of the SMASS index containing metadata of spectrum to retrieve.

    Notes
    -----
    Spectrum is stored in the cache directory.
    """

    URL_BASE = "http://smass.mit.edu/data/spex"

    # Create directory structure and check if the spectrum is already cached
    PATH_OUT = config.PATH_CACHE / f"smass/{spec.run}/{spec.filename}"

    # Ensure directory structure exists
    PATH_OUT.parent.mkdir(parents=True, exist_ok=True)

    # Download spectrum
    URL = f"{URL_BASE}/{spec.run}/{spec.filename}"
    spec = pd.read_csv(URL, delimiter="\s+", names=["wave", "refl", "err", "flag"])

    # Store to file
    spec.to_csv(PATH_OUT, index=False)
    logger.info(f"Retrieved spectrum {spec.run}/{spec.filename} from SMASS")
