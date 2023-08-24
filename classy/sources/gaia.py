import pandas as pd
import rocks

from classy import config
from classy import index
from classy import progress
from classy import tools

SHORTBIB, BIBCODE = "Galluccio+ 2022", "2022arXiv220612174G"

DATA_KWARGS = {}

PATH = config.PATH_CACHE / "gaia"


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

        # Adapt to classy naming scheme
        part = part.rename(
            columns={
                "wavelength": "wave",
                "reflectance_spectrum": "refl",
                "reflectance_spectrum_err": "refl_err",
                "reflectance_spectrum_flag": "flag",
            }
        )

        # Use wavelenght in micron
        part.wave /= 1000

        _create_spectra_files(part, PATH_PART)

        part = part.drop_duplicates(subset="name")
        part["filename"] = part["denomination"].apply(
            lambda d: f"gaia/part{idx:02}/{d}.csv"
        )

        # Add metadata
        part["shortbib"] = SHORTBIB
        part["bibcode"] = BIBCODE
        part["date_obs"] = ""
        part["source"] = "Gaia"
        part["host"] = "Gaia"
        part["module"] = "gaia"

        entries.append(part)

    entries = pd.concat(entries)
    index.add(entries)


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
    PATH_GAIA = config.PATH_CACHE / "gaia"
    PATH_GAIA.mkdir(parents=True, exist_ok=True)

    # ------
    # Retrieve observations
    URL = "http://cdn.gea.esac.esa.int/Gaia/gdr3/Solar_system/sso_reflectance_spectrum/SsoReflectanceSpectrum_"

    # Observations are split into 20 parts
    with progress.mofn as mofn:
        task = mofn.add_task("Gaia DR3", total=20)

        for idx in range(20):
            tools.download_archive(
                f"{URL}{idx:02}.csv.gz",
                PATH_GAIA / f"{idx:02}.csv.gz",
                unpack=False,
                progress=False,
                remove=False,
            )
            mofn.update(task, advance=1)


def _create_spectra_files(part, PATH_PART):
    for denomination, obs in part.groupby("denomination"):
        PATH_FILE = PATH_PART / f"{denomination}.csv"
        if not PATH_FILE.is_file():
            obs.to_csv(PATH_FILE, index=False)
