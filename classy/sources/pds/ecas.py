import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import config
from classy import index
from classy.sources import pds
from classy import tools

WAVE = [0.337, 0.359, 0.437, 0.550, 0.701, 0.853, 0.948, 1.041]


def _create_index(PATH_REPO):
    """Create index of ECAS collection. Further creates mean-colors with flags and
    PC-scores CSV files for easier look-ups in Tholen classification."""

    _create_mean_colors_file(PATH_REPO)

    # Build index from mean-colors file
    mean = pd.read_csv(PATH_REPO / "colors.csv")
    mean = mean[["name", "number"]]

    entries = []
    for _, row in mean.iterrows():
        entry = pd.DataFrame(
            data={
                "name": row["name"],
                "number": row["number"],
                "date_obs": "",
                "shortbib": "Zellner+ 1985",
                "bibcode": "1985Icar...61..355Z",
                "host": "pds",
                "collection": "ecas",
                "source": "ECAS",
                "filename": "pds/" + PATH_REPO.name + "/colors.csv",
                "wave_min": min(WAVE),
                "wave_max": max(WAVE),
                "N": len(WAVE),
                "public": True,
            },
            index=[0],
        )
        entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame
    """
    obs = pd.read_csv(config.PATH_CACHE / meta.filename)
    obs = obs.loc[obs["name"] == meta["name"]]

    # Convert colours to reflectances
    refl, refl_err = _compute_reflectance_from_colours(obs)
    flags = _add_flags(obs)

    data = pd.DataFrame(
        data={
            "refl": refl[~np.isnan(refl)],
            "refl_err": refl_err[~np.isnan(refl)],
            "wave": np.array(WAVE)[~np.isnan(refl)],
            "flag": flags[~np.isnan(refl)],
        },
    )

    return data


def _compute_reflectance_from_colours(obs):
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
    return refl, refl_err


def _add_flags(obs):
    flags = []

    for color in ["S_V", "U_V", "B_V", "V_V", "V_W", "V_X", "V_P", "V_Z"]:
        if color == "V_V":
            flag_value = 0
        else:
            flag_value = int(obs[f"flag_{color}"].values[0])
        flags.append(flag_value)

    flags = np.array(flags)
    return flags


def _create_mean_colors_file(PATH_REPO):
    PATH_MEAN = PATH_REPO / "data/ecasmean.tab"

    mean = pd.read_fwf(
        PATH_MEAN,
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
    mean.to_csv(PATH_REPO / "colors.csv", index=False)


# def _create_pc_scores_file(PATH_REPO):
#     # TODO Add tholen classifcation resutls parsing
#     PATH_SCORES = PATH_REPO / "data/ecaspc.tab"
#     scores = pd.read_fwf(
#         PATH_SCORES,
#         colspecs=[
#             (0, 6),
#             (7, 25),
#             (26, 32),
#             (33, 39),
#             (40, 46),
#             (47, 53),
#             (54, 60),
#             (61, 67),
#             (68, 74),
#             (75, 76),
#         ],
#         names=[
#             "AST_NUMBER",
#             "AST_NAME",
#             "PC1",
#             "PC2",
#             "PC3",
#             "PC4",
#             "PC5",
#             "PC6",
#             "PC7",
#             "NOTE",
#         ],
#     )
#
#     names, numbers = zip(*rocks.identify(scores.AST_NAME))
#
#     scores["name"] = names
#     scores["number"] = numbers
#
#     for ind, row in scores.iterrows():
#         r = rocks.Rock(row["name"], datacloud="taxonomies")
#         class_ = r.taxonomies[r.taxonomies.shortbib == "Tholen+1989"]
#         try:
#             class_ = class_.class_.values[0]
#         except IndexError:
#             class_ = ""
#         scores.loc[ind, "class_"] = class_
#
#     # Remove (152) Atala as it was misidentified in ECAS and thus has NaN scores
#     scores = scores.replace(-9.999, np.nan).dropna(subset="PC1")
# scores.to_csv(PATH_REPO / "ecas_scores.csv", index=False)
