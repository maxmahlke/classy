import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import core
from classy.log import logger
from classy import index


def load_spectrum(spec):
    """Load a cached Gaia spectrum.

    Parameters
    ----------
    spec : pd.Series

    Returns
    -------
    astro.core.Spectrum

    """
    PATH_SPEC = config.PATH_CACHE / spec.filename

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
        reflectance_spectrum_err=obs.reflectance_spectrum_err.values,
        flag=obs.reflectance_spectrum_flag.values,
        reflectance_spectrum_flag=obs.reflectance_spectrum_flag.values,
        source="Gaia",
        shortbib="Galluccio+ 2022",
        bibcode="2022arXiv220612174G",
        name=spec["name"],
        number=spec.number,
        source_id=obs.source_id.tolist()[0],
        number_mp=obs.source_id.tolist()[0],
        solution_id=obs.solution_id.tolist()[0],
        denomination=obs.denomination.tolist()[0],
        nb_samples=obs.nb_samples.tolist()[0],
        num_of_spectra=obs.num_of_spectra.tolist()[0],
        host="gaia",
        classy_id=spec.name,  # the classy index index
    )

    return spec


def _retrieve_spectra():
    """Retrieve Gaia DR3 reflectance spectra to cache."""

    logger.info(
        "Retrieving Gaia DR3 reflectance spectra [13MB] to cache and creating index..."
    )

    # Create directory structure
    PATH_GAIA = config.PATH_CACHE / "gaia"
    PATH_GAIA.mkdir(parents=True, exist_ok=True)

    # Retrieve observations
    URL = "http://cdn.gea.esac.esa.int/Gaia/gdr3/Solar_system/sso_reflectance_spectrum/SsoReflectanceSpectrum_"
    N_gaia = 20  # 20 separate gaia archives

    archives = {}

    # Observations are split into 20 parts
    from rich.progress import (
        BarColumn,
        DownloadColumn,
        Progress,
        TextColumn,
        MofNCompleteColumn,
    )

    progress = Progress(
        TextColumn("{task.description}", justify="right"),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
    )
    with progress:
        task = progress.add_task("Gaia DR3", total=N_gaia)
        for idx in range(N_gaia):
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

            # Store to cache
            part.to_csv(PATH_GAIA / f"SsoReflectanceSpectrum_{idx:02}.csv", index=False)
            progress.update(task, advance=1)

    # Convert index to dataframe, store to cache
    names, numbers = zip(*rocks.identify(list(archives.keys())))

    entries = []
    shortbib, bibcode = "Galluccio+ 2022", "2022arXiv220612174G"

    Nentries = len(names)

    entries = pd.DataFrame(
        data={
            "name": names,
            "number": numbers,
            "filename": [
                "gaia/" + filename + ".csv" for filename in list(archives.values())
            ],
        },
        index=[0] * Nentries,
    )

    entries["shortbib"] = shortbib
    entries["bibcode"] = bibcode
    entries["wave_min"] = 0.374
    entries["wave_max"] = 1.034
    entries["N"] = 16
    entries["date_obs"] = ""
    entries["source"] = "Gaia"
    entries["host"] = "gaia"
    entries["collection"] = "gaia"
    entries["public"] = True
    # for name, number, filename in zip(names, numbers, list(archives.values())):
    #     entry = pd.DataFrame(
    #         data={
    #             "name": name,
    #             "number": number,
    #             "filename": "gaia/" + filename + ".csv",
    #             "shortbib": shortbib,
    #             "bibcode": bibcode,
    #             "wave_min": 0.374,
    #             "wave_max": 1.034,
    #             "N": 16,
    #             "date_obs": "",
    #             "source": "Gaia",
    #             "host": "gaia",
    #             "collection": "gaia",
    #         },
    #         index=[0],
    #     )
    #     entries.append(entry)

    # index.to_csv(PATH_GAIA / "index.csv", index=False)
    # entries = pd.concat(entries)
    index.add(entries)
    logger.info(f"Added {len(entries)} Gaia spectra to the classy index.")
