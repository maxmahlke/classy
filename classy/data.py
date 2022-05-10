import importlib.resources
import pandas as pd


def load_resource(which):
    """Load package resource

    Parameters
    ----------
    which

    Returns
    -------

    """

    PATH_DATA = importlib.resources.files(__package__) / "data"


def load_model():
    """Load the trained MCFA model of the classy taxonomy.

    Returns
    -------
    mcfa.MCFA
        The MCFA model instance trained for the classy taxonomy.
    """
    import mcfa  # skip the heavy tensorflow import if it can be avoided

    return mcfa.from_file(classy.PATH_DATA / "mcfa/mcfa.pkl")


def load_gmm_29():

        PATH_GMM = classy.PATH_DATA / f"gmm/gmm_{cluster}.pkl"

        if not PATH_GMM.exists():
            gmm, classes = gmm_function()

            with PATH_GMM.open("wb") as file_:
                pickle.dump((gmm, classes), file_)

        else:
            with PATH_GMM.open("rb") as file_:
                gmm, classes = pickle.load(file_)

    PATH_GMM29 = classy.PATH_DATA / "gmm/gmm_29.pkl"

    if not PATH_GMM29.exists():
        GMM_29, CLASSES_29 = classy.decision_tree.resolve_cluster_29(data)

        with open(PATH_GMM29, "wb") as file_:
            pickle.dump((GMM_29, CLASSES_29), file_)

    else:
        with open(PATH_GMM29, "rb") as file_:
            GMM_29, CLASSES_29 = pickle.load(file_)


def _load_mixnorm():
    """Load the mixnorm model fit."""
    with (classy.PATH_DATA / "mixnorm/mixnorm.pkl").open("rb") as file_:
        return pickle.load(file_)


def _load_neighbours():
    """Load the classy spectra to use in the closest neighbour search."""
    return pd.read_csv((classy.PATH_DATA / "mixnorm/neighbours.csv"))


def load(which="classified"):
    """
    Load the original classy data.

    Parameters
    ----------
    which : str
        Which data to load. Choose from ['preprocessed', 'classified']. Default is 'classified'.
    """
    return pd.read_csv(classy.PATH_DATA / f"data/classy_data_{which}.csv")
