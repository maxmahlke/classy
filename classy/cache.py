"""Cache management for classy."""

from pathlib import Path

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy.logging import logger
from classy import core


# ------
# Indeces of spectra
def load_index(which):
    """Load an index file."""
    if which == "Gaia":
        return load_gaia_index()
    elif which == "SMASS":
        return load_smass_index()
    elif which == "Mahlke":
        return load_mahlke_index()
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

    if not PATH_INDEX.is_file():
        logger.info("Retrieving index of SMASS spectra...")

        URL_INDEX = "https://raw.githubusercontent.com/maxmahlke/classy/main/data/smass/index.csv"
        index = pd.read_csv(URL_INDEX)
        PATH_INDEX.parent.mkdir(parents=True, exist_ok=True)
        index.to_csv(PATH_INDEX, index=False)

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


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

    spectra = []

    for _, spec in idx_spectra.iterrows():

        if spec.source == "Gaia":
            spec = load_gaia_spectrum(spec)
        elif spec.source == "SMASS":
            spec = load_smass_spectrum(spec)

        spectra.append(spec)

    return spectra


def load_gaia_spectrum(spec):
    """Load a cached Gaia spectrum.

    Parameters
    ----------
    spec : pd.Series

    Returns
    -------
    astro.core.Spectrum

    """
    PATH_SPEC = config.PATH_CACHE / f"gaia/{spec.filename}.csv"

    obs = pd.read_csv(PATH_SPEC, dtype={"reflectance_spectrum_flag": int})
    obs = obs.loc[obs["name"] == spec["name"]]

    # Apply correction by Tinaut-Ruano+ 2023
    corr = [1.07, 1.05, 1.02, 1.01, 1.00]
    refl = obs.reflectance_spectrum.values
    refl[: len(corr)] *= corr

    spec = core.Spectrum(
        wave=obs.wavelength.values / 1000,
        wavelength=obs.wavelength.values / 1000,
        refl=refl,
        reflectance_spectrum=refl,
        refl_err=obs.reflectance_spectrum_err.values,
        flag=obs.reflectance_spectrum_flag.values,
        reflectance_spectrum_flag=obs.reflectance_spectrum_flag.values,
        source="Gaia",
        name=f"Gaia",
        asteroid_name=spec["name"],
        asteroid_number=spec.number,
        source_id=obs.source_id.tolist()[0],
        number_mp=obs.source_id.tolist()[0],
        solution_id=obs.solution_id.tolist()[0],
        denomination=obs.denomination.tolist()[0],
        nb_samples=obs.nb_samples.tolist()[0],
        num_of_spectra=obs.num_of_spectra.tolist()[0],
    )

    return spec


def load_smass_spectrum(spec):
    """Load a cached SMASS spectrum."""
    PATH_SPEC = config.PATH_CACHE / f"smass/{spec.inst}/{spec.run}/{spec.filename}"

    if not PATH_SPEC.is_file():
        retrieve_smass_spectrum(spec)

    data = pd.read_csv(PATH_SPEC)

    if spec.run == "smass1":
        data.wave /= 10000

    # 2 - reject. This is flag 0 in SMASS
    flags = [0 if f != 0 else 2 for f in data["flag"].values]

    spec = core.Spectrum(
        wave=data["wave"],
        refl=data["refl"],
        refl_err=data["err"],
        flag=flags,
        source="SMASS",
        run=spec.run,
        inst=spec.inst,
        name=f"{spec.inst}/{spec.run}",
        filename=spec.filename,
        asteroid_name=spec["name"],
        asteroid_number=spec.number,
    )
    return spec


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
    logger.info("Creating index of Gaia spectra...")
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

    URL_BASE = "http://smass.mit.edu/data"

    # Create directory structure and check if the spectrum is already cached
    PATH_OUT = config.PATH_CACHE / f"smass/{spec.inst}/{spec.run}/{spec.filename}"

    # Ensure directory structure exists
    PATH_OUT.parent.mkdir(parents=True, exist_ok=True)

    # Download spectrum
    URL = f"{URL_BASE}/{spec.inst}/{spec.run}/{spec.filename}"
    obs = pd.read_csv(URL, delimiter="\s+", names=["wave", "refl", "err", "flag"])

    # Store to file
    obs.to_csv(PATH_OUT, index=False)
    logger.info(f"Retrieved spectrum {spec.run}/{spec.filename} from SMASS")
