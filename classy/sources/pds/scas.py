import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import index

# ------
# Module definitions
SHORTBIB, BIBCODE = "Clark+ 1995", "1995Icar..113..387C"

# SCAS effective wavelengths from Clark+ 1993 LPI abstract
# 1.63 is estimated from Fig 2, the other points are mentioned in the text
WAVE = np.array([0.913, 1.05, 1.3, 1.55, 1.63, 2.16, 2.3])
COLORS = ["BA", "CA", "DA", "EA", "FA", "GA"]

DATA_KWARGS = {}


# ------
# Module functions
def _build_index(PATH_REPO):
    """Create index of spectra collection."""

    # Iterate over index file
    entries = _load_scas(PATH_REPO / "data/scas.tab")
    entries["name"], entries["number"] = zip(*rocks.identify(entries.number))

    entries["date_obs"] = ""
    entries["source"] = "SCAS"
    entries["host"] = "PDS"
    entries["module"] = "scas"

    entries["shortbib"] = SHORTBIB
    entries["bibcode"] = BIBCODE

    # Split the observations into one file per spectrum
    entries["filename"] = entries["number"].apply(
        lambda number: PATH_REPO.relative_to(config.PATH_DATA) / f"data/{number}.csv"
    )

    _create_spectra_files(entries)
    index.add(entries)


def _create_spectra_files(entries):
    """Create one file per SCAS spectrum."""

    for _, row in entries.iterrows():
        # Convert colours to reflectances
        refl = [1] + [np.power(10, -0.4 * (1 - c)) for c in row[COLORS]]
        refl_err = [0] + [
            np.abs(row[color]) * np.abs(0.4 * np.log(10) * row[f"{color}_ERROR"])
            for color in COLORS
        ]

        # Convert color indices to reflectance
        data = pd.DataFrame(data={"wave": WAVE, "refl": refl, "refl_err": refl_err})
        data.to_csv(config.PATH_DATA / row.filename, index=False)


def _load_scas(PATH_REPO):
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
