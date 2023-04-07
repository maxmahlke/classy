import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import core
from classy.log import logger


PREPROCESS_PARAMS = {
    "tholen": {"smooth_method": None},
    "demeo": None,
    "mahlke": {
        "smooth_method": None,
        "resample_params": {"bounds_error": False, "fill_value": (np.nan, np.nan)},
    },
}


def load_index():
    """Load the Gaia DR3 reflectance spectra index."""

    PATH_INDEX = config.PATH_CACHE / "ecas/ecas_mean.csv"

    if not PATH_INDEX.is_file():
        retrieve_spectra()

    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


def load_spectrum(spec):
    """Load a cached ECAS spectrum.

    Parameters
    ----------
    spec : pd.Series

    Returns
    -------
    astro.core.Spectrum
    """
    PATH_SPEC = config.PATH_CACHE / f"ecas/ecas_mean.csv"

    obs = pd.read_csv(PATH_SPEC)
    obs = obs.loc[obs["name"] == spec["name"]]

    # Convert colours to reflectances
    wave = [0.337, 0.359, 0.437, 0.550, 0.701, 0.853, 0.948, 1.041]
    refl = []
    refl_err = []

    for color in ["S_V", "U_V", "B_V"]:
        refl_c = obs[f"{color}_MEAN"].values[0]
        refl.append(np.power(10, -0.4 * (refl_c)))
        re = np.abs(refl_c) * np.abs(
            0.4 * np.log(10) * obs[f"{color}_STD_DEV"].values[0]
        )
        refl_err.append(re)

    refl.append(1)  # v-filter
    refl_err.append(0)  # v-filter

    for color in [
        "V_W",
        "V_X",
        "V_P",
        "V_Z",
    ]:
        refl_c = obs[f"{color}_MEAN"].values[0]
        refl.append(np.power(10, -0.4 * (-refl_c)))
        re = np.abs(refl_c) * np.abs(
            0.4 * np.log(10) * obs[f"{color}_STD_DEV"].values[0]
        )
        refl_err.append(re)

    refl = np.array(refl)

    refl_err = np.array(refl_err)

    spec = core.Spectrum(
        wave=wave,
        refl=refl,
        refl_err=refl_err,
        name=spec["name"],
        number=spec.number,
        nights=obs["NIGHTS"].values[0],
        note=obs["NOTE"].values[0],
        shortbib="Zellner+ 1985",
        bibcode="1985Icar...61..355Z",
        source="ECAS",
    )

    flags = []

    for color in ["S_V", "U_V", "B_V", "V_V", "V_W", "V_X", "V_P", "V_Z"]:
        if color == "V_V":
            flag_value = 0
        else:
            flag_value = int(obs[f"flag_{color}"].values[0])
        setattr(spec, f"flag_{color}", flag_value)
        flags.append(flag_value)

    spec.flag = np.array(flags)
    spec.flag = spec.flag[~np.isnan(refl)]
    spec._source = "ECAS"
    return spec


def retrieve_spectra():
    """Download the Eight Color Asteroid Survey results from PDS to cache."""
    from io import BytesIO
    from zipfile import ZipFile

    import requests

    PATH_ECAS = config.PATH_CACHE / "ecas"
    PATH_ECAS.mkdir(parents=True, exist_ok=True)

    URL = "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.ecas.phot.zip"
    logger.info("Retrieving Eight Color Asteroid Survey results [130kB] to cache...")

    content = requests.get(URL)

    # unzip the content
    f = ZipFile(BytesIO(content.content))

    # extract mean colors
    mean = "gbo.ast.ecas.phot/data/ecasmean.tab"
    scores = "gbo.ast.ecas.phot/data/ecaspc.tab"

    f.extract(mean, PATH_ECAS)
    f.extract(scores, PATH_ECAS)
    path_mean = PATH_ECAS / mean
    path_scores = PATH_ECAS / scores

    mean = pd.read_fwf(
        path_mean,
        colspecs=[
            (0, 6),
            (7, 24),
            (24, 30),
            (31, 34),
            (35, 41),
            (42, 45),
            (46, 52),
            (53, 56),
            (57, 63),
            (64, 67),
            (68, 74),
            (75, 78),
            (79, 85),
            (86, 89),
            (90, 96),
            (97, 100),
            (101, 102),
            (103, 105),
        ],
        names=[
            "AST_NUMBER",
            "AST_NAME",
            "S_V_MEAN",
            "S_V_STD_DEV",
            "U_V_MEAN",
            "U_V_STD_DEV",
            "B_V_MEAN",
            "B_V_STD_DEV",
            "V_W_MEAN",
            "V_W_STD_DEV",
            "V_X_MEAN",
            "V_X_STD_DEV",
            "V_P_MEAN",
            "V_P_STD_DEV",
            "V_Z_MEAN",
            "V_Z_STD_DEV",
            "NIGHTS",
            "NOTE",
        ],
    )

    names, numbers = zip(*rocks.id(mean.AST_NUMBER))

    mean["name"] = names
    mean["number"] = numbers

    # Set saturated or missing colors to NaN
    mean = mean.replace(-9.999, np.nan)
    mean["flag"] = 0

    for unc in [
        "S_V_STD_DEV",
        "U_V_STD_DEV",
        "B_V_STD_DEV",
        "V_W_STD_DEV",
        "V_X_STD_DEV",
        "V_P_STD_DEV",
        "V_Z_STD_DEV",
    ]:
        mean[unc] /= 1000

    mean.loc[
        (mean.S_V_STD_DEV > 0.095)
        | (mean.U_V_STD_DEV > 0.074)
        | (mean.B_V_STD_DEV > 0.039)
        | (mean.V_W_STD_DEV > 0.034)
        | (mean.V_X_STD_DEV > 0.039)
        | (mean.V_P_STD_DEV > 0.044)
        | (mean.V_Z_STD_DEV > 0.051),
        "flag",
    ] = 1

    for color, limit in zip(
        [
            "S_V_STD_DEV",
            "U_V_STD_DEV",
            "B_V_STD_DEV",
            "V_W_STD_DEV",
            "V_X_STD_DEV",
            "V_P_STD_DEV",
            "V_Z_STD_DEV",
        ],
        [0.095, 0.074, 0.039, 0.034, 0.039, 0.044, 0.051],
    ):
        mean.loc[mean[color] > limit, f"flag_{color[:3]}"] = 1
        mean.loc[mean[color] <= limit, f"flag_{color[:3]}"] = 0
    # Add quality flag following Tholen+ 1984
    mean.to_csv(PATH_ECAS / "ecas_mean.csv", index=False)

    # TODO Add tholen classifcation resutls parsing
    scores = pd.read_fwf(
        path_scores,
        colspecs=[
            (0, 6),
            (7, 25),
            (26, 32),
            (33, 39),
            (40, 46),
            (47, 53),
            (54, 60),
            (61, 67),
            (68, 74),
            (75, 76),
        ],
        names=[
            "AST_NUMBER",
            "AST_NAME",
            "PC1",
            "PC2",
            "PC3",
            "PC4",
            "PC5",
            "PC6",
            "PC7",
            "NOTE",
        ],
    )

    names, numbers = zip(*rocks.identify(scores.AST_NAME))

    scores["name"] = names
    scores["number"] = numbers

    for ind, row in scores.iterrows():
        r = rocks.Rock(row["name"], datacloud="taxonomies")
        class_ = r.taxonomies[r.taxonomies.shortbib == "Tholen+1989"]
        class_ = class_.class_.values[0]
        scores.loc[ind, "class_"] = class_

    # Remove (152) Atala as it was misidentified in ECAS and thus has NaN scores
    scores = scores.replace(-9.999, np.nan).dropna(subset="PC1")
    scores.to_csv(PATH_ECAS / "ecas_scores.csv", index=False)
