import pandas as pd

from classy import config
from classy import index
from classy.utils.logging import logger
from classy import utils

# ------
# Module definitions
SHORTBIB, BIBCODE = "Usui+ 2019", "2019PASJ...71....1U"

PATH = config.PATH_DATA / "akari"

DATA_KWARGS = {
    "delimiter": r"\s+",
    "names": [
        "wave",
        "refl",
        "refl_err",
        "flag_err",
        "flag_saturation",
        "flag_thermal",
        "flag_stellar",
    ],
}


# ------
# Module functions
def _retrieve_spectra():
    """Download the AcuA-spec archive to cache."""
    PATH.mkdir(parents=True, exist_ok=True)

    URL = "https://darts.isas.jaxa.jp/pub/akari/AKARI-IRC_Spectrum_Pointed_AcuA_1.0/AcuA_1.0.tar.gz"
    PATH_ARCHIVE = PATH / "AcuA_1.0.tar.gz"

    if PATH_ARCHIVE.is_file():
        logger.debug(f"akari - Using cached archive file at \n{PATH_ARCHIVE}")
        success = True
    else:
        success = utils.download.archive(URL, PATH_ARCHIVE)

    if success:
        utils.unpack(PATH_ARCHIVE, encoding="tar.gz")


def _build_index():
    """Add the AKARI spectra to the classy spectra index."""

    # Catch if download failed
    if not (PATH / "AcuA_1.0/target.txt").is_file():
        return

    # Create index based on target file
    entries = pd.read_csv(
        PATH / "AcuA_1.0/target.txt",
        delimiter=r"\s+",
        names=["number", "name", "obs_id", "date", "ra", "dec"],
        dtype={"number": int},
    )
    entries = entries.drop_duplicates("number")

    # Drop (4) Vesta and (4015) Wilson-Harrington as there are no spectra of them
    entries = entries[~entries.number.isin([4, 4015])]

    # Add filenames
    entries["filename"] = entries.apply(
        lambda row: f"akari/AcuA_1.0/reflectance/{row.number:>04}_{row['name']}.txt",
        axis=1,
    )

    entries["shortbib"] = SHORTBIB
    entries["bibcode"] = BIBCODE
    entries["date_obs"] = entries.date
    entries["source"] = "AKARI"
    entries["host"] = "AKARI"
    entries["module"] = "akari"

    # Et voila
    index.add(entries)


def _transform_data(_, data):
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

    # No metadata to record
    meta = {}
    return data, meta
