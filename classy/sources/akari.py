import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import core
from classy.log import logger
from classy import index
from classy import tools


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
    PATH_SPEC = config.PATH_CACHE / f"{spec.filename}"

    data = _load_data(PATH_SPEC)
    spec = core.Spectrum(
        wave=data.wave.values,
        refl=data.refl.values,
        refl_err=data.refl_err.values,
        flag=data.flag.values,
        source="AKARI",
        name=spec["name"],
        number=spec.number,
        shortbib="Usui+ 2019",
        bibcode="2019PASJ...71....1U",
        flag_err=data.flag_err.values,
        flag_saturation=data.flag_saturation.values,
        flag_thermal=data.flag_thermal.values,
        flag_stellar=data.flag_stellar.values,
        host="akari",
        classy_id=spec.name,  # the classy index index
    )

    return spec


def _retrieve_spectra():
    """Download the AcuA-spec archive to cache."""

    import tarfile
    import requests

    URL = "https://darts.isas.jaxa.jp/pub/akari/AKARI-IRC_Spectrum_Pointed_AcuA_1.0/AcuA_1.0.tar.gz"
    PATH_AKARI = config.PATH_CACHE / "akari"

    PATH_AKARI.mkdir(parents=True, exist_ok=True)

    # Retrieve spectra
    logger.info("Retrieving AKARI AcuA-spec reflectance spectra to cache...")
    tools.download_archive(URL, PATH_AKARI)
    # with requests.get(URL, stream=True) as file_:
    #     with tarfile.open(fileobj=file_.raw, mode="r:gz") as archive:
    # archive.extractall(PATH_AKARI)

    # Create index
    akari = pd.read_csv(
        PATH_AKARI / "AcuA_1.0/target.txt",
        delimiter="\s+",
        names=["number", "name", "obs_id", "date", "ra", "dec"],
        dtype={"number": int},
    )
    akari = akari.drop_duplicates("number")

    # Drop (4) Vesta and (4015) Wilson-Harrington as there are no spectra of them
    akari = akari[~akari.number.isin([4, 4015])]

    # Add filenames
    akari["filename"] = akari.apply(
        lambda row: f"{row.number:>04}_{row['name']}.txt", axis=1
    )

    akari = akari.drop(columns=["ra", "dec"])

    entries = []
    for _, row in akari.iterrows():
        name, number = row["name"], row.number

        filename = f"akari/AcuA_1.0/reflectance/{row.filename}"
        date_obs = row.date

        shortbib = "Usui+ 2019"
        bibcode = "2019PASJ...71....1U"

        data = _load_data(config.PATH_CACHE / filename)
        wave = data["wave"]

        # ------
        # Append to index
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "filename": filename,
                "shortbib": shortbib,
                "bibcode": bibcode,
                "wave_min": min(wave),
                "wave_max": max(wave),
                "N": len(wave),
                "date_obs": date_obs,
                "source": "AKARI",
                "host": "akari",
                "collection": "AcuA",
                "public": True,
            },
            index=[0],
        )
        entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)
    logger.info(f"Added {len(entries)} AKARI spectra to the classy index.")


def _load_data(PATH_SPEC):
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
    return data
