import re

import pandas as pd
import rocks

from classy import config
from classy import core
from classy import index
from classy.log import logger
from classy import tools


def load_spectrum(spec):
    """Load a cached SMASS spectrum."""
    PATH_SPEC = config.PATH_CACHE / spec.filename

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
        host="smass",
        date_obs=spec.date_obs,
        filename=spec.filename,
        classy_id=spec.name,  # the classy index index
    )
    return spec


def load_obslog():
    PATH_LOG = config.PATH_CACHE / "smass/obslog.csv"
    if not PATH_LOG.is_file():
        tools._retrieve_from_github(host="smass", which="obslog", path=PATH_LOG)
    return pd.read_csv(PATH_LOG)


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
        try:
            match = number.group(0)
        except AttributeError:
            return None
    return match


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
    "au2005JE46n1": "2005 JE46",
    "au2005JE46n": "2005 JE46",
    "au2005JE46n2": "2005 JE46",
    "au2007DT103n1": "2007 DT103",
    "au2007DT103n2": "2007 DT103",
    "a175706-obsA": 175706,
    "a175706-obsB": 175706,
}


def _retrieve_spectra():
    """Retrieve all SMASS spectra to smass/ the cache directory."""

    URL = "http://smass.mit.edu/data/smass"

    # Create directory structure and check if the spectrum is already cached
    PATH_SMASS = config.PATH_CACHE / "smass/"
    PATH_SMASS.mkdir(parents=True, exist_ok=True)

    logger.info("Retrieving all SMASS reflectance spectra to cache...")

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

    for file_, _, _, _ in ARCH_DIR_REF_BIB:
        url_archive = f"{URL}/{file_}.tar.gz"
        tools.download_archive(url_archive, PATH_SMASS)

    # Add to global spectra index.
    entries = []
    logger.info("Indexing SMASS spectra...")

    log = load_obslog()
    for _, dir, ref, bib in ARCH_DIR_REF_BIB:
        PATH_DIR = PATH_SMASS / dir

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

            data = _load_data(file_, dir, name)
            wave = data["wave"]

            entry = log[(log["name"] == name) & (log["shortbib"] == ref)]

            if entry.empty:
                date_obs = ""
            else:
                format = (
                    "%Y-%m-%d"
                    if ref not in ["Burbine and Binzel 2002", "Binzel+ 2004"]
                    else "%Y-%m-%d %H:%M"
                )
                date_obs = index.convert_to_isot(entry.date_obs.values, format=format)

            # ------
            # Append to index
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "filename": f"smass/{dir}/{file_.name}",
                    "shortbib": ref,
                    "bibcode": bib,
                    "wave_min": min(wave),
                    "wave_max": max(wave),
                    "N": len(wave),
                    "date_obs": date_obs,
                    "source": "SMASS",
                    "host": "smass",
                    "collection": "smass",
                    "public": True,
                },
                index=[0],
            )
            entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)
    logger.info(f"Added {len(entries)} SMASS spectra to the classy index.")


def _load_data(PATH, dir, name):
    data = pd.read_csv(PATH, names=["wave", "refl", "refl_err"], delimiter=r"\s+")

    if dir == "smass1":
        if name != "Schiaparelli":
            data["wave"] /= 10000
    return data
