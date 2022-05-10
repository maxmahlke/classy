import importlib.resources
import pickle

import pandas as pd


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
    return importlib.resources.files(__package__) / "data"


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
    tuple of sklearn.mixtures.GaussianMixtureModel, list
       The trained GMM instance and a list mapping the model components to the corresponding classes.
    """

    PATH_GMM = _get_path_data() / f"gmm/gmm_{cluster}.pkl"

    if not PATH_GMM.exists():
        return None, None

    with PATH_GMM.open("rb") as file_:
        gmm, classes = pickle.load(file_)

    return gmm, classes


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
