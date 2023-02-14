import sys

if sys.version_info[1] < 9:
    # this PyPI package is required for 3.7 and 3.8
    import importlib_resources as resources
else:
    import importlib.resources as resources
import pickle

import pandas as pd
import rocks
from sklearn.mixture import GaussianMixture

from classy import cache
from classy import gmm
from classy.logging import logger

SOURCES = ["Gaia", "SMASS"]

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
    "tholen": {
        "wave": {  # Table 1, Tholen 1984
            "s": 0.337,
            "u": 0.359,
            "b": 0.437,
            "v": 0.550,
            "w": 0.701,
            "x": 0.853,
            "P": 0.948,
            "z": 1.041,
        },  # Table 4, Tholen 1984
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
    }
}

# should be function of spec
def convert_to_ecas_colours():
    R = [  # reflectances at subwxpz
        0.5485295139412031,
        0.6742174675762443,
        0.8774047879567534,
        1.081433951297938,
        0.8566432555816557,
        0.7812679345516048,
        1.003690930920097,
    ]
    refl_v = 1

    colors = []

    for filt in ["s", "u", "b"]:
        refl = R.pop(0)
        colors.append(-2.5 * np.log10(refl / refl_v))
    for filt in ["w", "x", "p", "z"]:
        refl = R.pop(0)
        colors.append(-2.5 * np.log10(refl_v / refl))


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
