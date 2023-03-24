import sys

if sys.version_info[1] < 9:
    # this PyPI package is required for 3.7 and 3.8
    import importlib_resources as resources
else:
    import importlib.resources as resources
import pickle

import numpy as np
import pandas as pd
import rocks
from sklearn.mixture import GaussianMixture

from classy import cache
from classy import gmm
from classy.log import logger

SOURCES = [
    "Gaia",
    "SMASS",
    "AKARI",
    "ECAS",
]


# ------
# Spectra
def load_spectra(name, source):
    """Load spectra of a given asteroid either from cache or from an online repository.

    Parameters
    ----------
    name : str
        The name of the asteroid.
    source : list of str
        List of online repositories to check. Must be complete or subset of data.SOURCES.

    Returns
    -------
    list of classy.Spectrum
    """

    index_spectra = pd.DataFrame()

    for s in source:
        index = cache.load_index(s)
        index = index.loc[index["name"] == name]

        if not index.empty:
            N = len(index)
            logger.info(f"Found {N} spectr{'a' if N > 1 else 'um'} in {s}")

        index["source"] = s
        index_spectra = pd.concat([index_spectra, index])

    if index_spectra.empty:
        logger.info(f"Did not find any spectra in repositories: {', '.join(source)} ")
        return []

    return cache.load_spectra(index_spectra)


# ------
# Products of Mahlke+ 2022
def load(resource, cluster=None):
    """Load a classy package resource.

    Parameters
    ----------
    resource : str
        Type of resource to load. Choose from ['classy', 'gmm', 'mcfa', 'mixnorm'].

    cluster : int
        If loading a GMM, specify which cluster should be loaded. Default is None.
    """

    if resource == "classy":
        return _load_classy()

    elif resource == "gmm":
        if not isinstance(cluster, int) and cluster != "emp":
            raise ValueError(
                "The cluster number has to be specified when loading a GMM."
            )
        return _load_gmm(cluster)

    elif resource == "mcfa":
        return _load_mcfa()

    elif resource == "mixnorm":
        return _load_mixnorm()


def _get_path_data():
    """Return the absolute path to the classy data directory."""
    return resources.files(__package__) / "data"


def _load_classy():
    """Load the classified classy data.

    Returns
    -------
    pd.DataFrame
        The classified classy data.
    """
    return pd.read_csv(_get_path_data() / f"classy/classy_data.csv")


def _load_mcfa():
    """Load the trained MCFA model of the classy taxonomy.

    Returns
    -------
    mcfa.MCFA
        The MCFA model instance trained for the classy taxonomy.
    """
    import mcfa  # skip the heavy tensorflow import if it can be avoided

    return mcfa.from_file(_get_path_data() / "mcfa/mcfa.pkl")


def _load_gmm(cluster):
    """Load a trained GMM for the decision tree.

    Parameters
    ----------
    cluster : int or str
        The cluster whose GMM should be loaded

    Returns
    -------
    tuple of sklearn.mixtures.GaussianMixture, list
       The trained GMM instance and a list mapping the model components to the corresponding classes.
    """

    props = gmm.GMM[cluster]

    gmm_ = GaussianMixture(
        n_components=props["n_components"],
        covariance_type=props["covariance_type"],
        tol=props["tol"],
        reg_covar=props["reg_covar"],
        max_iter=props["max_iter"],
        n_init=props["n_init"],
        init_params=props["init_params"],
        weights_init=props["weights_init"],
        means_init=props["means_init"],
        precisions_init=props["precisions_init"],
        random_state=props["random_state"],
        warm_start=props["warm_start"],
        verbose=props["verbose"],
        verbose_interval=props["verbose_interval"],
    )
    gmm_.weights_ = props["weights_"]
    gmm_.means_ = props["means_"]
    gmm_.covariances_ = props["covariances_"]
    gmm_.precisions_ = props["precisions_"]
    gmm_.precisions_cholesky_ = props["precisions_cholesky_"]
    gmm_.n_iter_ = props["n_iter_"]
    gmm_.lower_bound_ = props["lower_bound_"]

    classes = gmm.GMM[cluster]["classes"]

    return gmm_, classes


def _load_mixnorm():
    """Load the mixnorm model fit.

    Returns
    -------
    tuple of dict, pd.DataFrame
        Dict containing the mixnorm model parameters, DataFrame containing
        the spectra to be used in the nearest-neighbour search
    """
    PATH_DATA = _get_path_data()

    with (PATH_DATA / "mixnorm/mixnorm.pkl").open("rb") as file_:
        mixnorm = pickle.load(file_)

    neighbours = pd.read_csv(PATH_DATA / "mixnorm/neighbours.csv")

    return mixnorm, neighbours


def load_gaia(id_):
    """Load the Gaia spectrum of an asteroid.

    Parameters
    ----------
    id_ : int, str
        Asteroid identifier passed to rocks.id

    Returns
    -------
    classy.Observation
        The Gaia spectrum of the asteroid.

    Notes
    -----
    All Gaia metadata is available with the Observation attributes:
        ['source_id', 'solution_id 'number_mp', 'denomination', 'nb_samples',
         'num_of_spectra', 'reflectance_spectrum', 'reflectance_spectrum_err',
         'wavelength', 'reflectance_spectrum_flag']
    """

    name, number = rocks.id(id_)

    index = cache.load_gaia_index()
    index = index.loc[index["name"] == name]

    if index.empty:
        logger.error(f"No spectrum of ({number}) {name} is in Gaia DR3.")
        return None

    return cache.load_gaia_spectrum(index.squeeze(axis=0))


TAXONOMIES = {
    "mahlke": {
        "wave_limits": [0.45, 2.45],
    },
    "tholen": {
        "wave_limits": [0.337, 1.041],
        "wave": {  # Table 1, Tholen 1984
            "s": 0.337,
            "u": 0.359,
            "b": 0.437,
            "v": 0.550,
            "w": 0.701,
            "x": 0.853,
            "P": 0.948,
            "z": 1.041,
        },  # Table 2, Tholen 1984
        "pc_mean": {
            "A": [5.22025, -3.3075, -1.04225, -0.39475, -0.0965, 0.0505, -0.01025],
            "B": [-3.2565, -1.11117, -0.2475, -0.06533, 0.08867, -0.06567, -0.00383],
            "C": [-1.93297, -0.42958, 0.30007, -0.12481, 0.0397, -0.0047, -0.01122],
            "D": [1.87344, 3.46416, 0.02376, -0.05424, 0.00416, -0.03652, 0.0382],
            "E": [-0.777, 0.90238, -0.06238, 0.20475, -0.07125, 0.10662, 0.084],
            "F": [-3.52331, -0.02215, -0.61477, 0.18785, 0.05023, 0.00854, -0.01738],
            "G": [-1.548, -1.5596, 0.7428, -0.4462, -0.0218, -0.0746, -0.0678],
            "M": [-1.02795, 1.29676, -0.1079, 0.06176, -0.1161, 0.00867, 0.0599],
            "P": [-0.92983, 1.30317, -0.18726, 0.06713, 0.01178, 0.088, -0.02913],
            "Q": [-0.898, -4.338, -0.362, 0.204, 0.363, -0.042, 0.294],
            "R": [0.972, -4.237, -0.039, 1.327, -0.191, -0.076, 0.063],
            "S": [2.10517, -0.69103, -0.01393, 0.07399, -0.00031, 0.0001, -0.00612],
            "T": [1.38525, 1.32625, 0.07375, -0.392, 0.07625, 0.10875, -0.01125],
            "V": [-1.557, -4.371, 0.922, 1.957, 0.231, -0.013, 0.143],
            "X": [-0.90924, 1.014, -0.09833, 0.10633, -0.05595, -0.00829, -0.00257],
        },
        "data_mean": {
            "s-v": 0.325,
            "u-v": 0.234,
            "b-v": 0.089,
            "v-w": 0.091,
            "v-x": 0.105,
            "v-p": 0.103,
            "v-z": 0.111,
        },
        "data_std": {
            "s-v": 0.221,
            "u-v": 0.173,
            "b-v": 0.092,
            "v-w": 0.081,
            "v-x": 0.091,
            "v-p": 0.104,
            "v-z": 0.120,
        },
        # Table 4, Tholen 1984
        "eigenvalues": [4.737, 1.879, 0.180, 0.118, 0.045, 0.032, 0.010],
        "eigenvectors": [
            # s-v, u-v, b-v, v-w, v-x, v-p, v-z
            [0.346, 0.373, 0.415, 0.433, 0.399, 0.336, 0.330],
            [-0.463, -0.416, -0.289, 0.000, 0.320, 0.475, 0.448],
            [0.231, 0.207, 0.028, -0.622, -0.290, -0.002, 0.657],
            [-0.207, -0.103, 0.028, 0.586, -0.399, -0.460, 0.481],
            [0.442, 0.044, -0.707, 0.094, 0.398, -0.347, 0.124],
            [-0.303, -0.039, 0.398, -0.271, 0.580, -0.574, 0.100],
            [0.531, -0.795, 0.292, -0.016, -0.010, -0.022, 0.031],
        ],
    },
    "demeo": {
        "wave": np.arange(0.45, 2.5, 0.05),
        "data_mean": [
            0.8840578,
            0.94579985,
            1.04016798,
            1.07630094,
            1.10387232,
            1.10729138,
            1.07101476,
            1.02252107,
            0.99167561,
            0.98766575,
            1.00292349,
            1.02223844,
            1.04660108,
            1.07201578,
            1.08967345,
            1.10014259,
            1.11101667,
            1.12359452,
            1.13128556,
            1.13642896,
            1.13467689,
            1.12810013,
            1.11471935,
            1.09802574,
            1.07842635,
            1.06127665,
            1.04536074,
            1.03360292,
            1.02395605,
            1.01587389,
            1.01034821,
            1.00915786,
            1.01078308,
            1.01245031,
            1.01298133,
            1.01314109,
            1.01236654,
            1.01140562,
            1.01090655,
            1.00955344,
        ],
        "eigenvectors": [
            [
                -0.0766,
                -0.0391,
                0.0438,
                0.0876,
                0.1256,
                0.1466,
                0.1271,
                0.0888,
                0.0680,
                0.0857,
                0.1371,
                0.1921,
                0.2322,
                0.2566,
                0.2704,
                0.2787,
                0.2849,
                0.2852,
                0.2782,
                0.2641,
                0.2427,
                0.2154,
                0.1841,
                0.1531,
                0.1247,
                0.1002,
                0.0804,
                0.0665,
                0.0570,
                0.0513,
                0.0502,
                0.0538,
                0.0607,
                0.0690,
                0.0778,
                0.0859,
                0.0934,
                0.0997,
                0.1050,
                0.1090,
            ],
            [
                -0.0643,
                -0.0279,
                0.0176,
                0.0343,
                0.0471,
                0.0096,
                -0.1186,
                -0.2673,
                -0.3645,
                -0.3743,
                -0.2899,
                -0.1527,
                -0.0381,
                0.0306,
                0.0708,
                0.1053,
                0.1385,
                0.1598,
                0.1645,
                0.1520,
                0.1192,
                0.0689,
                0.0089,
                -0.0514,
                -0.1069,
                -0.1532,
                -0.1884,
                -0.2136,
                -0.2283,
                -0.2317,
                -0.2233,
                -0.2023,
                -0.1706,
                -0.1302,
                -0.0852,
                -0.0406,
                0.0023,
                0.0438,
                0.0832,
                0.1177,
            ],
            [
                -0.2724,
                -0.1270,
                0.1128,
                0.2104,
                0.2726,
                0.2475,
                0.1486,
                0.0420,
                -0.0385,
                -0.1168,
                -0.2083,
                -0.2809,
                -0.2747,
                -0.2169,
                -0.1713,
                -0.1427,
                -0.1031,
                -0.0407,
                0.0243,
                0.0930,
                0.1562,
                0.2021,
                0.2231,
                0.2215,
                0.2043,
                0.1784,
                0.1508,
                0.1225,
                0.0923,
                0.0617,
                0.0346,
                0.0136,
                -0.0038,
                -0.0229,
                -0.0447,
                -0.0678,
                -0.0911,
                -0.1153,
                -0.1389,
                -0.1580,
            ],
            [
                0.3046,
                0.1525,
                -0.1486,
                -0.2677,
                -0.3386,
                -0.3284,
                -0.2392,
                -0.1453,
                -0.0921,
                -0.0505,
                -0.0289,
                -0.0277,
                -0.0160,
                0.0077,
                0.0304,
                0.0450,
                0.0608,
                0.0842,
                0.1104,
                0.1387,
                0.1609,
                0.1752,
                0.1804,
                0.1714,
                0.1550,
                0.1421,
                0.1279,
                0.1095,
                0.0868,
                0.0610,
                0.0358,
                0.0103,
                -0.0162,
                -0.0476,
                -0.0838,
                -0.1225,
                -0.1644,
                -0.2068,
                -0.2445,
                -0.2708,
            ],
            [
                -0.5174,
                -0.1876,
                0.0593,
                0.0754,
                0.0523,
                -0.0231,
                -0.1466,
                -0.2569,
                -0.2293,
                -0.0657,
                0.1077,
                0.1717,
                0.1685,
                0.1611,
                0.1463,
                0.1061,
                0.0533,
                0.0090,
                -0.0429,
                -0.0868,
                -0.1188,
                -0.1250,
                -0.1158,
                -0.0940,
                -0.0757,
                -0.0525,
                -0.0271,
                0.0104,
                0.0473,
                0.0785,
                0.1050,
                0.1249,
                0.1241,
                0.0916,
                0.0354,
                -0.0327,
                -0.1126,
                -0.1993,
                -0.2884,
                -0.3767,
            ],
        ],
    },
}


# should be method of Spectrum
def convert_to_ecas_colors(refl):
    # R = [  # reflectances at subwxpz
    #     0.5485295139412031,
    #     0.6742174675762443,
    #     0.8774047879567534,
    #     1.081433951297938,
    #     0.8566432555816557,
    #     0.7812679345516048,
    #     1.003690930920097,
    # ]
    R = list(refl)
    refl_v = 1

    colors = []

    for filt in ["s", "u", "b"]:
        refl = R.pop(0)
        colors.append(-2.5 * np.log10(refl / refl_v))
    R.pop(0)
    for filt in ["w", "x", "p", "z"]:
        refl = R.pop(0)
        colors.append(-2.5 * np.log10(refl_v / refl))
    return np.array(colors)


ecas = {
    "ceres": {
        "s-v": 0.43,
        "u-v": 0.263,
        "b-v": 0.047,
        "v-w": 0,
        "v-x": -0.005,
        "v-p": -0.022,
        "v-z": -0.031,
    },
    "vesta": {
        "s": 0.652,
        "u": 0.428,
        "b": 0.142,
        "w": 0.085,
        "x": -0.168,
        "p": -0.268,
        "z": 0.004,
    },
}
tholen_pc = (
    pd.read_csv("/home/mmahlke/astro/cclassy/develop/tholen.csv")
    .replace(-9.999, np.nan)
    .dropna(subset="PC1")
    .reset_index()
)
