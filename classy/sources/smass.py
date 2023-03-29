import numpy as np
import pandas as pd

from classy import config
from classy import core
from classy.log import logger

PREPROCESS_PARAMS = {
    "tholen": {"smooth_method": None},
    "demeo": None,
    "mahlke": {
        "smooth_method": None,
        "resample_params": {"bounds_error": False, "fill_value": (np.nan, np.nan)},
    },
}


def load_index():
    """Load the SMASS reflectance spectra index."""

    PATH_INDEX = config.PATH_CACHE / "smass/index.csv"

    if not PATH_INDEX.is_file():
        logger.info("Retrieving index of SMASS spectra...")

        URL_INDEX = "https://raw.githubusercontent.com/maxmahlke/classy/main/data/smass/index.csv"
        index = pd.read_csv(URL_INDEX)
        PATH_INDEX.parent.mkdir(parents=True, exist_ok=True)
        index.to_csv(PATH_INDEX, index=False)

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


def load_spectrum(spec):
    """Load a cached SMASS spectrum."""
    PATH_SPEC = config.PATH_CACHE / f"smass/{spec.inst}/{spec.run}/{spec.filename}"

    if not PATH_SPEC.is_file():
        retrieve_spectrum(spec)

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
    spec._source = "SMASS"
    return spec


def retrieve_spectrum(spec):
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
