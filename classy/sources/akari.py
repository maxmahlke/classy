import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import core
from classy.log import logger

PREPROCESS_PARAMS = {
    "tholen": None,
    "bus": None,
    "demeo": None,
    "mahlke": None,
}


def load_index():
    """Load the AKARI reflectance spectra index."""

    PATH_INDEX = config.PATH_CACHE / "akari/AcuA_1.0/index.csv"

    if not PATH_INDEX.is_file():
        retrieve_spectra()

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


def load_spectrum(spec):
    """Load a cached AKARI spectrum.

    Parameters
    ----------
    spec : pd.Series

    Returns
    -------
    astro.core.Spectrum

    """
    PATH_SPEC = config.PATH_CACHE / f"akari/AcuA_1.0/reflectance/{spec.filename}"

    # Load spectrum
    data = pd.read_csv(
        PATH_SPEC,
        delimiter="\s+",
        names=[
            "wave",
            "refl",
            "refl_err",
            "flag_err",
            "flag_saturation",
            "flag_thermal",
            "flag_stellar",
        ],
    )

    # Add a joint flag, it's 1 if any other flag is 1
    data["flag"] = data.apply(
        lambda point: 1
        if any(
            bool(point[flag])
            for flag in ["flag_err", "flag_saturation", "flag_thermal", "flag_stellar"]
        )
        else 0,
        axis=1,
    )

    spec = core.Spectrum(
        wave=data.wave.values,
        refl=data.refl.values,
        refl_err=data.refl_err.values,
        flag=data.flag.values,
        source="AKARI",
        name=spec["name"],
        number=spec.number,
        shortbib="2019PASJ...71....1U",
        bibcode="Usui+ 2019",
        flag_err=data.flag_err.values,
        flag_saturation=data.flag_saturation.values,
        flag_thermal=data.flag_thermal.values,
        flag_stellar=data.flag_stellar.values,
    )
    spec._source = "AKARI"

    return spec


def retrieve_spectra():
    """Download the AcuA-spec archive to cache."""

    import tarfile
    import requests

    URL = "https://darts.isas.jaxa.jp/pub/akari/AKARI-IRC_Spectrum_Pointed_AcuA_1.0/AcuA_1.0.tar.gz"
    PATH_AKARI = config.PATH_CACHE / "akari"

    PATH_AKARI.mkdir(parents=True, exist_ok=True)

    # Retrieve spectra
    logger.info("Retrieving AKARI AcuA-spec reflectance spectra [1.7MB] to cache...")
    with requests.get(URL, stream=True) as file_:
        with tarfile.open(fileobj=file_.raw, mode="r:gz") as archive:
            archive.extractall(PATH_AKARI)

    # Create index
    index = pd.read_csv(
        PATH_AKARI / "AcuA_1.0/target.txt",
        delimiter="\s+",
        names=["number", "name", "obs_id", "date", "ra", "dec"],
        dtype={"number": int},
    )
    index = index.drop_duplicates("number")

    # Drop (4) Vesta and (4015) Wilson-Harrington as there are no spectra of them
    index = index[~index.number.isin([4, 15])]

    # Add filenames
    index["filename"] = index.apply(
        lambda row: f"{row.number:>04}_{row['name']}.txt", axis=1
    )

    index.to_csv(PATH_AKARI / "AcuA_1.0/index.csv", index=False)
