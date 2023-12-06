from pathlib import Path

import pandas as pd
import rocks

from classy import config
from classy import index
from classy import utils

SHORTBIB, BIBCODE = "Galluccio+ 2022", "2022arXiv220612174G"

DATA_KWARGS = {}

PATH = config.PATH_DATA / "gaia"


def _build_index():
    # Retrieve the spectra

    entries = []

    for idx in range(20):
        part = pd.read_csv(PATH / f"{idx:02}.csv.gz", compression="gzip", comment="#")

        PATH_PART = PATH / f"part{idx:02}"
        PATH_PART.mkdir(exist_ok=True)

        # Create list of identifiers from number and name columns
        ids = part.number_mp.fillna(part.denomination).values
        names, numbers = zip(*rocks.id(ids))

        part["name"] = names
        part["number"] = numbers

        part = part.drop_duplicates(subset="name")
        part["filename"] = part["denomination"].apply(
            lambda d: f"gaia/part{idx:02}/{d}.csv"
        )

        # Add metadata
        part["wave_min"] = 0.374
        part["wave_max"] = 1.034
        part["N"] = 16
        part["shortbib"] = SHORTBIB
        part["bibcode"] = BIBCODE
        part["date_obs"] = ""
        part["source"] = "Gaia"
        part["host"] = "Gaia"
        part["module"] = "gaia"

        entries.append(part)

    entries = pd.concat(entries)
    index.add(entries)


def _load_virtual_file(idx):
    """Make Gaia archive compatible with one-file-one-spectrum approach
    without creating 65k actual files.
    """

    # Load part and select asteroid
    part = str(Path(idx.name).parent.name).strip("part")
    part = pd.read_csv(PATH / f"{part}.csv.gz", compression="gzip", comment="#")
    part = part[(part.denomination == idx["name"]) | (part.number_mp == idx.number)]

    # Adapt to classy naming scheme
    part = part.rename(
        columns={
            "wavelength": "wave",
            "reflectance_spectrum": "refl",
            "reflectance_spectrum_err": "refl_err",
            "reflectance_spectrum_flag": "flag",
        }
    )

    part = part[~pd.isna(part.refl)]
    part.wave /= 1000  # to micron
    return part


def _transform_data(_, data):
    """Apply module-specific data transforms."""

    # Apply correction by Tinaut-Ruano+ 2023
    CORR = [1.07, 1.05, 1.02, 1.01, 1.00]
    refl = data.refl.values
    refl[: len(CORR)] *= CORR
    data.refl = refl

    # Record metadata
    meta = {
        "source_id": data.source_id.values[0],
        "number_mp": data.number_mp.values[0],
        "solution_id": data.solution_id.values[0],
        "denomination": data.denomination.values[0],
        "nb_samples": data.nb_samples.values[0],
        "num_of_spectra": data.num_of_spectra.values[0],
    }

    # Slim down data
    data = data[["wave", "refl", "refl_err", "flag"]]
    return data, meta


def _retrieve_spectra():
    """Retrieve Gaia DR3 reflectance spectra to cache."""

    # Create directory structure
    PATH_GAIA = config.PATH_DATA / "gaia"
    PATH_GAIA.mkdir(parents=True, exist_ok=True)

    # ------
    # Retrieve observations
    URL = "http://cdn.gea.esac.esa.int/Gaia/gdr3/Solar_system/sso_reflectance_spectrum/SsoReflectanceSpectrum_"

    # Observations are split into 20 parts
    for idx in range(20):
        PATH_ARCHIVE = PATH_GAIA / f"{idx:02}.csv.gz"

        if not PATH_ARCHIVE.is_file():
            utils.download.archive(
                f"{URL}{idx:02}.csv.gz", PATH_ARCHIVE, progress=False, remove=False
            )


# def _create_spectra_files(part, PATH_PART):
#     for denomination, obs in part.groupby("denomination"):
#         PATH_FILE = PATH_PART / f"{denomination}.csv"
#         if not PATH_FILE.is_file():
#             obs.to_csv(PATH_FILE, index=False)
