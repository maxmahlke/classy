import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds
from classy import utils

# ------
# Module definitions
WAVE = [0.337, 0.359, 0.437, 0.550, 0.701, 0.853, 0.948, 1.041]

SHORTBIB, BIBCODE = "Zellner+ 1985", "1985Icar...61..355Z"

DATA_KWARGS = {}


# ------
# Module functions
def _build_index(PATH_REPO):
    """Create index of ECAS collection. Further creates mean-colors with flags and
    PC-scores CSV files for easier look-ups in Tholen classification."""

    # _create_mean_colors_file(PATH_REPO)

    # Build index from mean-colors file
    # entries = pd.read_csv(PATH_REPO / "colors.csv")
    entries = pd.read_fwf(
        PATH_REPO / "data/ecas.tab",
        colspecs=[
            (0, 6),
            (7, 24),
            (25, 31),
            (32, 35),
            (36, 42),
            (43, 46),
            (47, 53),
            (54, 57),
            (58, 64),
            (65, 68),
            (69, 75),
            (76, 79),
            (80, 86),
            (87, 90),
            (91, 97),
            (98, 101),
            (102, 108),
            (109, 112),
            (113, 132),
            (133, 136),
            (137, 139),
        ],
        names=[
            "number",
            "name",
            "S_V",
            "S_V_STD_DEV",
            "U_V",
            "U_V_STD_DEV",
            "B_V",
            "B_V_STD_DEV",
            "V_MAG",
            "V_MAG_STD_DEV",
            "V_W",
            "V_W_STD_DEV",
            "V_X",
            "V_X_STD_DEV",
            "V_P",
            "V_P_STD_DEV",
            "V_Z",
            "V_Z_STD_DEV",
            "date_obs",
            "CYCLES",
            "NOTE",
        ],
    )

    entries = entries.replace(-9.999, np.nan)
    entries = entries.replace(-99, np.nan)
    entries = entries.replace(-9, np.nan)

    for col in [
        "S_V_STD_DEV",
        "U_V_STD_DEV",
        "B_V_STD_DEV",
        "V_W_STD_DEV",
        "V_X_STD_DEV",
        "V_P_STD_DEV",
        "V_Z_STD_DEV",
    ]:
        entries[col] /= 1000

    # Verify identification
    entries["name"], entries["number"] = zip(*rocks.id(entries.number))

    for _, spectra in entries.groupby("name"):
        for i, (_, spec) in enumerate(spectra.iterrows()):
            entries.loc[spec.name, "count"] = i

    entries["source"] = "ECAS"
    entries["host"] = "PDS"
    entries["module"] = "ecas"

    entries["bibcode"] = BIBCODE
    entries["shortbib"] = SHORTBIB

    # Split the observations into one file per spectrum
    entries["filename"] = entries.apply(
        lambda entry: PATH_REPO.relative_to(config.PATH_DATA)
        / f"data/{entry.number}_{int(entry['count'])}.csv",
        axis=1,
    )

    _create_spectra_files(entries)
    index.add(entries)


def _create_spectra_files(entries):
    """Create one file per ECAS spectrum."""

    for _, row in entries.iterrows():
        # Convert colours to reflectances
        refl, refl_err = _compute_reflectance_from_colors(row)
        # flags = _add_flags(row)

        data = pd.DataFrame(
            data={
                "refl": refl[~np.isnan(refl)],
                "refl_err": refl_err[~np.isnan(refl)],
                "wave": np.array(WAVE)[~np.isnan(refl)],
                # "flag": flags[~np.isnan(refl)],
            },
        )

        data.to_csv(config.PATH_DATA / row.filename, index=False)


def _compute_reflectance_from_colors(obs):
    refl = []
    refl_err = []

    for color in ["S_V", "U_V", "B_V"]:
        # refl_c = obs[f"{color}_MEAN"]
        refl_c = obs[f"{color}"]
        refl.append(np.power(10, -0.4 * (refl_c)))
        re = np.abs(refl_c) * np.abs(0.4 * np.log(10) * obs[f"{color}_STD_DEV"])
        refl_err.append(re)

    refl.append(1)  # v-filter
    refl_err.append(0)  # v-filter

    for color in [
        "V_W",
        "V_X",
        "V_P",
        "V_Z",
    ]:
        refl_c = obs[f"{color}"]
        refl.append(np.power(10, -0.4 * (-refl_c)))
        re = np.abs(refl_c) * np.abs(0.4 * np.log(10) * obs[f"{color}_STD_DEV"])
        refl_err.append(re)

    refl = np.array(refl)
    refl_err = np.array(refl_err)
    return refl, refl_err


# def _add_flags(refl, refl_err):
#     flags = []
#
#     for color in ["S_V", "U_V", "B_V", "V_V", "V_W", "V_X", "V_P", "V_Z"]:
#         if color == "V_V":
#             flag_value = 0
#             continue
#         else:
#             flag_value = int(obs[f"flag_{color}"])
#
#     mean.loc[
#         (mean.S_V_STD_DEV > 0.095)
#         | (mean.U_V_STD_DEV > 0.074)
#         | (mean.B_V_STD_DEV > 0.039)
#         | (mean.V_W_STD_DEV > 0.034)
#         | (mean.V_X_STD_DEV > 0.039)
#         | (mean.V_P_STD_DEV > 0.044)
#         | (mean.V_Z_STD_DEV > 0.051),
#         "flag",
#     ] = 1
#
#     for color, limit in zip(
#         [
#             "S_V_STD_DEV",
#             "U_V_STD_DEV",
#             "B_V_STD_DEV",
#             "V_W_STD_DEV",
#             "V_X_STD_DEV",
#             "V_P_STD_DEV",
#             "V_Z_STD_DEV",
#         ],
#         [0.095, 0.074, 0.039, 0.034, 0.039, 0.044, 0.051],
#     ):
#         mean.loc[mean[color] > limit, f"flag_{color[:3]}"] = 1
#         mean.loc[mean[color] <= limit, f"flag_{color[:3]}"] = 0
#     flags.append(flag_value)
#
# flags = np.array(flags)
# return flags


# def _create_mean_colors_file(PATH_REPO):
#     PATH_MEAN = PATH_REPO / "data/ecasmean.tab"
#
#     mean = pd.read_fwf(
#         PATH_MEAN,
#         colspecs=[
#             (0, 6),
#             (7, 24),
#             (24, 30),
#             (31, 34),
#             (35, 41),
#             (42, 45),
#             (46, 52),
#             (53, 56),
#             (57, 63),
#             (64, 67),
#             (68, 74),
#             (75, 78),
#             (79, 85),
#             (86, 89),
#             (90, 96),
#             (97, 100),
#             (101, 102),
#             (103, 105),
#         ],
#         names=[
#             "AST_NUMBER",
#             "AST_NAME",
#             "S_V_MEAN",
#             "S_V_STD_DEV",
#             "U_V_MEAN",
#             "U_V_STD_DEV",
#             "B_V_MEAN",
#             "B_V_STD_DEV",
#             "V_W_MEAN",
#             "V_W_STD_DEV",
#             "V_X_MEAN",
#             "V_X_STD_DEV",
#             "V_P_MEAN",
#             "V_P_STD_DEV",
#             "V_Z_MEAN",
#             "V_Z_STD_DEV",
#             "NIGHTS",
#             "NOTE",
#         ],
#     )
#
#     names, numbers = zip(*rocks.id(mean.AST_NUMBER))
#
#     mean["name"] = names
#     mean["number"] = numbers
#
#     # Set saturated or missing colors to NaN
#     mean = mean.replace(-9.999, np.nan)
#     mean["flag"] = 0
#
#     for unc in [
#         "S_V_STD_DEV",
#         "U_V_STD_DEV",
#         "B_V_STD_DEV",
#         "V_W_STD_DEV",
#         "V_X_STD_DEV",
#         "V_P_STD_DEV",
#         "V_Z_STD_DEV",
#     ]:
#         mean[unc] /= 1000
#
#     mean.loc[
#         (mean.S_V_STD_DEV > 0.095)
#         | (mean.U_V_STD_DEV > 0.074)
#         | (mean.B_V_STD_DEV > 0.039)
#         | (mean.V_W_STD_DEV > 0.034)
#         | (mean.V_X_STD_DEV > 0.039)
#         | (mean.V_P_STD_DEV > 0.044)
#         | (mean.V_Z_STD_DEV > 0.051),
#         "flag",
#     ] = 1
#
#     for color, limit in zip(
#         [
#             "S_V_STD_DEV",
#             "U_V_STD_DEV",
#             "B_V_STD_DEV",
#             "V_W_STD_DEV",
#             "V_X_STD_DEV",
#             "V_P_STD_DEV",
#             "V_Z_STD_DEV",
#         ],
#         [0.095, 0.074, 0.039, 0.034, 0.039, 0.044, 0.051],
#     ):
#         mean.loc[mean[color] > limit, f"flag_{color[:3]}"] = 1
#         mean.loc[mean[color] <= limit, f"flag_{color[:3]}"] = 0
#
#     # Add quality flag following Tholen+ 1984
#     mean.to_csv(PATH_REPO / "colors.csv", index=False)
