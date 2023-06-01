import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

REFERENCES = {
    "52CAS": ["1988LPI....19...57B", "Bell+ 1988"],
    "CRUIK": ["1984Sci...223..281C", "Cruikshank and Hartmann 1984"],
}

WAVE = np.array(
    [
        0.8289,
        0.8533,
        0.8776,
        0.9021,
        0.9265,
        0.9510,
        0.9755,
        1.0001,
        1.0247,
        1.0493,
        1.0740,
        1.0987,
        1.1234,
        1.1482,
        1.1730,
        1.1978,
        1.2227,
        1.2476,
        1.2726,
        1.2976,
        1.3226,
        1.3476,
        1.3727,
        1.3978,
        1.4230,
        1.4482,
        1.4734,
        1.4987,
        1.5240,
        1.5490,
        1.5747,
        1.6001,
        1.4910,
        1.5520,
        1.6150,
        1.6750,
        1.7350,
        1.7950,
        1.8530,
        1.9130,
        1.9700,
        2.0280,
        2.0840,
        2.1400,
        2.1960,
        2.2520,
        2.3060,
        2.3610,
        2.4140,
        2.4660,
        2.5190,
        2.5700,
    ]
)


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over index file
    ftcas = _load_ftcas(PATH_REPO)
    for _, row in ftcas.iterrows():
        if pd.isna(row.number):
            continue  # not including phobos and deimos here

        # Identify asteroid
        id_ = row.number
        name, number = rocks.id(id_)

        ref = "52CAS" if number not in [246, 289] else "CRUIK"
        bibcode, shortbib = REFERENCES[ref]

        # Extract spectrum metadata
        file_ = PATH_REPO / "data0" / f"52color.tab"

        # Create index entry
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "date_obs": row.date_obs,
                "wave_min": WAVE.min(),
                "wave_max": WAVE.max(),
                "N": len(WAVE),
                "shortbib": shortbib,
                "bibcode": bibcode,
                "filename": str(file_).split("/classy/")[1],
                "source": "52CAS",
                "host": "pds",
                "collection": "ftcas",
                "public": True,
            },
            index=[0],
        )

        entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)


def _load_ftcas(PATH_REPO):
    """Load the 52cas data file.

    Returns
    -------
    pd.DataFrame
    """

    # ------
    # Read reflectance values
    refl_cols = [f"REFL_{i}" for i in range(1, len(WAVE) + 1)]
    data = pd.read_csv(
        PATH_REPO / "data/data0/52color.tab",
        delimiter=r"\s+",
        names=[
            "number",
            "analog",
            "date_obs",
        ]
        + refl_cols,
    )

    # Add error values
    refl_err_cols = [f"REFL_{i}_UNC" for i in range(1, len(WAVE) + 1)]
    data_err = pd.read_csv(
        PATH_REPO / "data/data0/52error.tab",
        delimiter=r"\s+",
        names=[
            "number",
            "analog",
            "date_obs",
        ]
        + refl_err_cols,
    )
    data_err[refl_err_cols] /= 10000

    # Merge frames
    data = (
        pd.merge(  # number and date-obs are not sufficient to align but the indeces are
            data, data_err, right_index=True, left_index=True, suffixes=("", "_y")
        )
    )

    # Some cleanup
    data = data.replace(-9999, np.nan)
    data = data.replace(-0.9999, np.nan)
    return data


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame

    """
    ftcas = _load_ftcas(config.PATH_CACHE / "/".join(meta.filename.split("/")[:2]))
    ftcas = ftcas.loc[ftcas.number == meta.number]

    refl = ftcas[[f"REFL_{i}" for i in range(1, len(WAVE) + 1)]].values[0]
    refl_err = ftcas[[f"REFL_{i}_UNC" for i in range(1, len(WAVE) + 1)]].values[0]

    # Convert color indices to reflectance
    data = pd.DataFrame(data={"wave": WAVE, "refl": refl, "refl_err": refl_err})
    return data
