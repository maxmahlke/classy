import re

import pandas as pd
import rocks

from classy import config
from classy import index
from classy.utils.logging import logger
from classy import utils

# ------
# Module definitions
ARCH_DIR_REF_BIB = [
    ("smass1data_new", "smass1", "Xu+ 1995", "1995Icar..115....1X"),
    ("smass2data", "smass2", "Bus and Binzel 2002", "2002Icar..158..106B"),
    ("smassirdata", "smassir", "Burbine and Binzel 2002", "2002Icar..159..468B"),
    ("smassneodata", "smassneo", "Binzel+ 2001", "2001Icar..151..139B"),
    ("smassref5", "sf36ref5", "Binzel+ 2001", "2001M&PS...36.1167B"),
    ("smassref6", "meudonnereusref6", "Binzel+ 2004", "2004P&SS...52..291B"),
    ("smassref7", "neotargetsref7", "Binzel+ 2004", "2004M&PS...39..351B"),
    ("smassref8", "smassneoref8", "Binzel+ 2004", "2004Icar..170..259B"),
    ("smassref9", "hermesref9", "Rivkin+ 2004", "2004Icar..172..408R"),
]

AMBIGUOUS = {
    # from MITHNEOS
    "a099942subm": 99942,
    "a385343n2": 385343,
    "a154244n1": 154244,
    "a154244n3": 154244,
    "a385343n1": 385343,
    "a001862n1": 1862,
    "a001862n2": 1862,
    "a001862n": 1862,
    "a538": 538,
    "aPluto": 134340,
    "au2005JE46n1": "2005 JE46",
    "au2005JE46n": "2005 JE46",
    "au2005JE46n2": "2005 JE46",
    "au2007DT103n1": "2007 DT103",
    "au2007DT103n2": "2007 DT103",
    "a175706-obsA": 175706,
    "a175706-obsB": 175706,
}

PATH = config.PATH_DATA / "smass/"

DATA_KWARGS = {"names": ["wave", "refl", "refl_err", "flag"], "delimiter": r"\s+"}


# ------
# Module functions
def _retrieve_spectra():
    """Retrieve all SMASS spectra to smass/ the cache directory."""

    URL = "http://smass.mit.edu/data/smass"

    # Create directory structure and check if the spectrum is already cached
    PATH.mkdir(parents=True, exist_ok=True)

    for file_, _, _, _ in ARCH_DIR_REF_BIB:
        url_archive = f"{URL}/{file_}.tar.gz"
        PATH_ARCHIVE = PATH / f"{file_}.tar.gz"
        if PATH_ARCHIVE.is_file():
            logger.debug(f"smass - Using cached archive file at \n{PATH_ARCHIVE}")
        else:
            utils.download.archive(url_archive, PATH_ARCHIVE)
        utils.unpack(PATH_ARCHIVE, encoding="tar.gz")


def _build_index():
    # Add to global spectra index.
    rocks.set_log_level("CRITICAL")
    entries = []

    log = index.data.load_cat(host="smass", which="obslog")

    for _, dir, ref, bib in ARCH_DIR_REF_BIB:
        PATH_DIR = PATH / dir

        for file_ in PATH_DIR.iterdir():
            # Skip splined fit ones
            if "spfit" in file_.name:
                continue

            if file_.name in [
                "README",
                "SMASSIR.files.txt",
                "DIRECTORY",
                "a025143model.5",
            ]:
                continue

            # ------
            # Extract target from filename
            id_ = get_id_from_filename(file_)

            if id_ is None:
                continue

            # typo in the filename
            if "hermesref9" in str(file_):
                if id_ == "069320":
                    id_ = 69230

            name, number = rocks.id(id_)

            entry = log[(log["name"] == name) & (log["shortbib"] == ref)]

            if entry.empty:
                date_obs = ""
            else:
                date_obs = ",".join(entry.date_obs.values)

            # ------
            # Append to index
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "filename": f"smass/{dir}/{file_.name}",
                    "shortbib": ref,
                    "bibcode": bib,
                    "date_obs": date_obs,
                    "source": "SMASS",
                    "host": "smass",
                    "module": "smass",
                },
                index=[0],
            )

            entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)


def _transform_data(idx, data):
    data["flag"] = [0 if f != 0 else 2 for f in data["flag"]]

    # Adapt wavelength of smass1
    if "/smass1/" in idx.name:
        if idx["name"] != "Schiaparelli":
            data["wave"] /= 10000

    # No metadata to record
    meta = {}
    return data, meta


def get_id_from_filename(file_):
    id_ = file_.name.split(".")[0]
    id_ = id_.split("_")[0]

    if id_ in AMBIGUOUS:
        return AMBIGUOUS[id_]

    if id_.endswith("visir8"):
        id_ = id_[: -len("visir8")]
    if id_.endswith("ir8"):
        id_ = id_[: -len("ir8")]

    # Asteroid Unnumbered: extract designation
    match = None
    if id_.startswith("au"):
        id_ = id_.lstrip("au")
        designation = re.match(
            r"([1A][8-9][0-9]{2}[ _]?[A-Za-z]{2}[0-9]{0,3})|"
            r"(20[0-9]{2}[_ ]?[A-Za-z]{2}[0-9]{0,3})",
            id_,
        )
        match = designation.group(0)
    # Asteroid: extract number
    elif id_.startswith("a"):
        id_ = id_.lstrip("a")
        number = re.match(r"(\d\d\d\d\d\d)", id_)
        if number:
            match = number.group(0)
    else:
        match = id_
    return match
