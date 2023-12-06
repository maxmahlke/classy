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

from classy.taxonomies.mahlke import gmm
from classy.utils.logging import logger
from classy import index

import shutil

import rich

from classy import config
from classy import sources
from classy import utils


# ------
# Spectra
# def load_spectra(name, source):
#     """Load spectra of a given asteroid either from cache or from an online repository.
#
#     Parameters
#     ----------
#     name : str
#         The name of the asteroid.
#     source : list of str
#         List of online repositories to check. Must be complete or subset of data.SOURCES.
#
#     Returns
#     -------
#     list of classy.Spectrum
#     """
#     classy_index = index.load()
#     index_spectra = classy_index[
#         (classy_index["name"] == name) & classy_index["source"].isin(source)
#     ]
#
#     if index_spectra.empty:
#         name, number = rocks.id(name)
#         logger.warning(
#             f"Did not find any spectra of ({number}) {name} in {', '.join(source)} "
#         )
#         return []
#
#     return cache.load_spectra(index_spectra)


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
    return resources.files(__package__) / "../data"


def _load_classy():
    """Load the classified classy data.

    Returns
    -------
    pd.DataFrame
        The classified classy data.
    """
    return pd.read_csv(_get_path_data() / "classy/classy_data.csv")


def _load_mcfa():
    """Load the trained MCFA model of the classy taxonomy.

    Returns
    -------
    mcfa.MCFA
        The MCFA model instance trained for the classy taxonomy.
    """
    import tensorflow as tf

    tf.get_logger().setLevel("ERROR")

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


def load_mahlke_index():
    """Load the index of spectra from Mahlke+ 2022."""
    PATH_INDEX = config.PATH_DATA / "mahlke/index.csv"
    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


# ------
# Load spectra from cache
def load_spectra(idx_spectra, skip_target):
    """Load a spectrum from a known source.

    Returns
    -------
    list of classy.core.Spectrum
    """
    spectra = [
        sources.load_spectrum(spec, skip_target) for _, spec in idx_spectra.iterrows()
    ]

    return spectra


def remove():
    """Remove the cache directory."""
    shutil.rmtree(config.PATH_DATA)


def echo_inventory():
    """Echo inventory statistics based on the classy spectra index."""
    idx = index.load()
    sources_ = list(idx.source.unique())

    all_public = idx[idx.host == "Private"].empty
    legend = "[[bold]public[/bold]|[dim]private[/dim]]" if not all_public else ""

    rich.print(
        f"""\nContents of {config.PATH_DATA}:

    {len(idx)} asteroid reflectance spectra from {len(sources_)} sources {legend}
      """
    )

    if sources_:
        for i, (source, obs) in enumerate(
            idx.sort_values("source").groupby("source"), 1
        ):
            public = obs.host.values[0] != "Private"
            highlight = "dim" if not public else "bold"

            rich.print(
                f"    [{highlight}]{source:<8}[/{highlight}] {len(obs):>5}",
                end="",
            )

            if not i % 4:
                rich.print()
        else:
            rich.print("\n")


def load_cat(host, which):
    PATH_CAT = config.PATH_DATA / f"{host}/{which}.csv"
    if not PATH_CAT.is_file():
        utils.download.from_github(host, which, path=PATH_CAT)
    return pd.read_csv(PATH_CAT)
