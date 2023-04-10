import tarfile
import re
from urllib.request import urlretrieve

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import core
from classy.log import logger

PREPROCESS_PARAMS = {
    "tholen": {},
    "demeo": {},
    "mahlke": {
        "smooth": {},
        "resample": {"bounds_error": False, "fill_value": (np.nan, np.nan)},
    },
}


def load_index():
    """Load the SMASS reflectance spectra index."""

    PATH_INDEX = config.PATH_CACHE / "smass/index.csv"

    if not PATH_INDEX.is_file():
        retrieve_spectra()

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


def load_spectrum(spec):
    """Load a cached SMASS spectrum."""
    PATH_SPEC = config.PATH_CACHE / f"smass/{spec.filename}"

    data = pd.read_csv(
        PATH_SPEC, names=["wave", "refl", "err", "flag"], delimiter="\s+"
    )

    if "smass1/" in spec.filename:
        data.wave /= 10000

    # 2 - reject. This is flag 0 in SMASS
    flags = [0 if f != 0 else 2 for f in data["flag"].values]

    spec = core.Spectrum(
        wave=data["wave"],
        refl=data["refl"],
        refl_err=data["err"],
        flag=flags,
        source="SMASS",
        run=spec.filename.split("."),
        name=spec["name"],
        number=spec.number,
        bibcode=spec.bibcode,
        shortbib=spec.shortbib,
    )
    spec._source = "SMASS"
    return spec


def retrieve_spectra():
    """Retrieve all SMASS spectra to smass/ the cache directory."""

    URL = "http://smass.mit.edu/data/smass"

    # Create directory structure and check if the spectrum is already cached
    PATH_SMASS = config.PATH_CACHE / "smass/"
    PATH_SMASS.mkdir(parents=True, exist_ok=True)

    FILE_REF_BIB = [
        ("smass1data_new", "Xu+ 1995", "1995Icar..115....1X"),
        ("smass2data", "Bus and Binzel+ 2002", "2002Icar..158..106B"),
        ("smassirdata", "Burbine and Binzel 2002", "2002Icar..159..468B"),
        ("smassneodata", "Binzel+ 2001", "2001Icar..151..139B"),
        ("smassref5", "Binzel+ 2001", "2001M&PS...36.1167B"),
        ("smassref6", "Binzel+ 2004", "2004P&SS...52..291B"),
        ("smassref7", "Binzel+ 2004", "2004M&PS...39..351B"),
        ("smassref8", "Binzel+ 2004", "2004Icar..170..259B"),
        ("smassref9", "Rivkin+ 2004", "2004Icar..172..408R"),
    ]

    logger.info("Retrieving all SMASS reflectance spectra [2.8MB] to cache...")

    for file_, ref, bib in FILE_REF_BIB:
        url_archive = f"{URL}/{file_}.tar.gz"
        urlretrieve(url_archive, PATH_SMASS / f"{file_}.tar.gz")

        with tarfile.open(PATH_SMASS / f"{file_}.tar.gz", mode="r:gz") as archive:
            archive.extractall(PATH_SMASS)

    # Create index
    index = pd.DataFrame()

    DIR_REF_BIB = [
        ("smass1", "Xu+ 1995", "1995Icar..115....1X"),
        ("smass2", "Bus and Binzel+ 2002", "2002Icar..158..106B"),
        ("smassir", "Burbine and Binzel 2002", "2002Icar..159..468B"),
        ("smassneo", "Binzel+ 2001", "2001Icar..151..139B"),
        ("sf36ref5", "Binzel+ 2001", "2001M&PS...36.1167B"),
        ("meudonnereusref6", "Binzel+ 2004", "2004P&SS...52..291B"),
        ("neotargetsref7", "Binzel+ 2004", "2004M&PS...39..351B"),
        ("smassneoref8", "Binzel+ 2004", "2004Icar..170..259B"),
        ("hermesref9", "Rivkin+ 2004", "2004Icar..172..408R"),
    ]

    for dir, ref, bib in DIR_REF_BIB:
        PATH_DIR = PATH_SMASS / dir

        for file_ in PATH_DIR.iterdir():
            # Skip splined fit ones
            if "spfit" in file_.name:
                continue

            # ------
            # Extract target from filename
            id_smass = file_.name.split(".")[0]

            # Asteroid Unnumbered: extract designation
            if id_smass.startswith("au"):
                id_smass = id_smass.lstrip("au")
                designation = re.match(
                    r"([1A][8-9][0-9]{2}[ _]?[A-Za-z]{2}[0-9]{0,3})|"
                    r"(20[0-9]{2}[_ ]?[A-Za-z]{2}[0-9]{0,3})",
                    id_smass,
                )
                match = designation.group(0)
            # Asteroid: extract number
            elif id_smass.startswith("a"):
                id_smass = id_smass.lstrip("a")
                number = re.match(r"(\d\d\d\d\d\d)", id_smass)
                match = number.group(0)

            # typo in the filename
            if "hermesref9" in str(file_):
                if match == "069320":
                    match = 69230

            name, number = rocks.id(match)

            # ------
            # Append to index
            entry = pd.DataFrame(
                {
                    "name": name,
                    "number": number,
                    "filename": f"{dir}/{file_.name}",
                    "shortbib": ref,
                    "bibcode": bib,
                },
                index=[0],
            )
            index = pd.concat([index, entry], ignore_index=True)

    index["number"] = index["number"].astype("Int64")
    index.to_csv(PATH_SMASS / "index.csv", index=False)
