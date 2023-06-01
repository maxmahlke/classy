import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

REFERENCES = {
    "CHAPMAN1972": ["1972PhDT.........5C", "Chapman 1972"],
    "CHAPMAN&GAFFEY1979A": ["1979aste.book..655C", "Chapman and Gaffey 1979"],
    1: ["1979aste.book.1064C", "Chapman and Gaffey 1979"],
    2: ["1984Icar...59...25M", "McFadden+ 1984"],
}

WAVE = np.array(
    [
        0.33,
        0.34,
        0.355,
        0.4,
        0.43,
        0.47,
        0.5,
        0.54,
        0.57,
        0.6,
        0.635,
        0.67,
        0.7,
        0.73,
        0.765,
        0.8,
        0.83,
        0.87,
        0.9,
        0.93,
        0.95,
        0.97,
        1.0,
        1.03,
        1.06,
        1.1,
    ]
)


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over index file
    tfcas = _load_tfcas(PATH_REPO / "data/data0/24color.tab")
    for _, row in tfcas.iterrows():
        if pd.isna(row.number):
            continue  # not including phobos and deimos here

        # Identify asteroid
        id_ = row.number
        name, number = rocks.id(id_)

        ref = row.ref
        bibcode, shortbib = REFERENCES[ref]

        # Extract spectrum metadata
        file_ = PATH_REPO / "data/data0/24color.tab"

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
                "source": "24CAS",
                "host": "pds",
                "collection": "tfcas",
                "public": True,
            },
            index=[0],
        )

        entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)


def _load_tfcas(PATH):
    """Load the 24cas data file.

    Returns
    -------
    pd.DataFrame
    """
    refl_cols = zip(
        [f"REFL_{i}" for i in range(1, 27)], [f"REFL_{i}_UNC" for i in range(1, 27)]
    )
    refl_cols = [r for tup in refl_cols for r in tup]

    data = pd.read_fwf(
        PATH,
        colspecs=[
            (0, 6),
            (6, 17),
            (17, 23),
            (23, 28),
            (28, 34),
            (34, 39),
            (39, 45),
            (45, 50),
            (50, 56),
            (56, 61),
            (61, 67),
            (67, 72),
            (72, 78),
            (78, 83),
            (83, 89),
            (89, 94),
            (94, 100),
            (100, 105),
            (105, 111),
            (111, 116),
            (116, 122),
            (122, 127),
            (127, 133),
            (133, 138),
            (138, 144),
            (144, 149),
            (149, 155),
            (155, 160),
            (160, 166),
            (166, 171),
            (171, 177),
            (177, 182),
            (182, 188),
            (188, 193),
            (193, 199),
            (199, 204),
            (204, 210),
            (210, 215),
            (215, 221),
            (221, 226),
            (226, 232),
            (232, 237),
            (237, 243),
            (243, 248),
            (248, 254),
            (254, 259),
            (259, 265),
            (265, 270),
            (270, 276),
            (276, 281),
            (281, 287),
            (287, 292),
            (292, 298),
            (298, 303),
            (303, 314),
            (314, 316),
            (316, 318),
        ],
        names=[
            "number",
            "prov_id",
        ]
        + refl_cols
        + ["date_obs", "ref", "note"],
    )
    data = data.replace(-9.99, np.nan)
    data = data.replace(9.99, np.nan)

    return data


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame

    """
    tfcas = _load_tfcas(config.PATH_CACHE / meta.filename)
    tfcas = tfcas.loc[tfcas.number == meta.number]

    # Convert colours to reflectances
    refl = tfcas[[f"REFL_{i}" for i in range(1, 27)]].values[0]
    refl_err = tfcas[[f"REFL_{i}_UNC" for i in range(1, 27)]].values[0]

    # Convert color indices to reflectance
    data = pd.DataFrame(data={"wave": WAVE, "refl": refl, "refl_err": refl_err})
    return data
