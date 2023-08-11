import pandas as pd
import rocks

from classy import config
from classy import index
from classy import progress

SHORTBIB, BIBCODE = "Galluccio+ 2022", "2022arXiv220612174G"


def _load_data(idx):
    """Load data and metadata of a cached Gaia spectrum.

    Parameters
    ----------
    idx : pd.Series
        A row from the classy spectra index.

    Returns
    -------
    pd.DataFrame, dict
        The data and metadata. List-like attributes are in the dataframe,
        single-value attributes in the dictionary.
    """

    # Load spectrum data file
    PATH_DATA = config.PATH_CACHE / idx.filename
    data = pd.read_csv(PATH_DATA, dtype={"flag": int})

    # Select asteroid of index and rename columns to fit classy scheme
    data = data.loc[data["name"] == idx["name"]]

    # Apply correction by Tinaut-Ruano+ 2023
    CORR = [1.07, 1.05, 1.02, 1.01, 1.00]
    data.refl[: len(CORR)] *= CORR

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
    archives = {}

    # Observations are split into 20 parts
    with progress.mofn as mofn:
        task = mofn.add_task("Gaia DR3", total=20)

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

                archives[asteroid] = f"SsoReflectanceSpectrum_{idx:02}"

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

            # Store to cache
            part.to_csv(PATH_GAIA / f"SsoReflectanceSpectrum_{idx:02}.csv", index=False)
            mofn.update(task, advance=1)

    # ------
    # Convert index of asteroids in archives to dataframe, append to classy index
    names, numbers = zip(*rocks.identify(list(archives.keys())))

    entries = pd.DataFrame(
        data={
            "name": names,
            "number": numbers,
            "filename": [
                "gaia/" + filename + ".csv" for filename in list(archives.values())
            ],
        },
        index=[0] * len(names),
    )

    # Add metadata
    entries["shortbib"] = SHORTBIB
    entries["bibcode"] = BIBCODE
    entries["wave_min"] = 0.374
    entries["wave_max"] = 1.034
    entries["N"] = 16
    entries["date_obs"] = ""
    entries["source"] = "Gaia"
    entries["host"] = "Gaia"
    entries["module"] = "gaia"

    index.add(entries)
