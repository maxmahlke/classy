import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

REFERENCES = {
    "CLARKETAL1995": ["1995Icar..113..387C", "Clark+ 1995"],
}

# SCAS effective wavelengths from Clark+ 1993 LPI abstract
# 1.63 is estimated from Fig 2, the other points are mentioned in the text
WAVE = np.array([0.913, 1.05, 1.3, 1.55, 1.63, 2.16, 2.3])
COLORS = ["BA", "CA", "DA", "EA", "FA", "GA"]


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    # Iterate over index file
    scas = _load_scas(PATH_REPO / "data/scas.tab")

    entries = []
    for _, row in scas.iterrows():
        if pd.isna(row.number):
            continue  # not including phobos and deimos here

        # Identify asteroid
        id_ = row.number
        name, number = rocks.id(id_)

        ref = "CLARKETAL1995"
        bibcode, shortbib = REFERENCES[ref]

        # Extract spectrum metadata
        file_ = PATH_REPO / "data" / f"scas.tab"

        # Create index entry
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "date_obs": np.nan,
                "wave_min": WAVE.min(),
                "wave_max": WAVE.max(),
                "N": len(WAVE),
                "shortbib": shortbib,
                "bibcode": bibcode,
                "filename": str(file_).split("/classy/")[1],
                "source": "SCAS",
                "host": "pds",
                "collection": "scas",
                "public": True,
            },
            index=[0],
        )
        entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)


def _load_scas(PATH_REPO):
    """Load the SCAS data file.

    Returns
    -------
    pd.DataFrame
    """
    data = pd.read_fwf(
        PATH_REPO,
        columns=[
            (0, 6),
            (6, 12),
            (12, 19),
            (19, 25),
            (25, 32),
            (32, 38),
            (38, 45),
            (45, 51),
            (51, 58),
            (58, 64),
            (64, 71),
            (71, 77),
            (77, 84),
            (84, 92),
            (92, 98),
        ],
        names=[
            "number",
            "BA",
            "BA_ERROR",
            "CA",
            "CA_ERROR",
            "DA",
            "DA_ERROR",
            "EA",
            "EA_ERROR",
            "FA",
            "FA_ERROR",
            "GA",
            "GA_ERROR",
            "B_D",
            "B_D_ERROR",
        ],
    )
    return data


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame

    """
    scas = _load_scas(config.PATH_CACHE / meta.filename)
    scas = scas.loc[scas.number == meta.number]

    # Convert colours to reflectances
    refl = [1] + [np.power(10, -0.4 * (1 - c)) for c in scas[COLORS].values[0]]
    refl_err = [0] + [
        np.abs(scas[color].values[0])
        * np.abs(0.4 * np.log(10) * scas[f"{color}_ERROR"].values[0])
        for color in COLORS
    ]

    # Convert color indices to reflectance
    data = pd.DataFrame(data={"wave": WAVE, "refl": refl, "refl_err": refl_err})
    return data
