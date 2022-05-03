import pickle

import classy
from sklearn.mixture import GaussianMixture


def load_mixture_models():
    """Load the trained GMM mixture models used in the classification.

    Returns
    -------
    dict
        Dict containing the cluster number : trained GMM instances
    dict
        Dict containing the cluster number : classes in this cluster, in order
        of the corresponding GMM cluster component.

    Notes
    -----
    Fits the models using the original classy data if the files are not present.
    """
    GMMS, CLASSES = {}, {}

    for (
        cluster,
        gmm_function,
    ) in FIT_CLUSTER_FUNCTIONS.items():

        PATH_GMM = classy.PATH_DATA / f"gmm/gmm_{cluster}.pkl"

        if not PATH_GMM.exists():
            gmm, classes = gmm_function()

            with PATH_GMM.open("wb") as file_:
                pickle.dump((gmm, classes), file_)

        else:
            with PATH_GMM.open("rb") as file_:
                gmm, classes = pickle.load(file_)

        GMMS[cluster] = gmm
        CLASSES[cluster] = classes

    return GMMS, CLASSES


def fit_cluster_4():
    """Fit a GMM to resolve objects in cluster 4 into classes L and S.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()

    gmm_23_40 = GaussianMixture(n_components=2, random_state=17).fit(
        data.loc[data.cluster.isin([23, 40]), ["z2", "z3"]]
    )  # Fit cluster 23 and 40 in z2, z3 (0-indexed)

    CLASSES = (
        ["S", "L"] if gmm_23_40.means_[0][1] > gmm_23_40.means_[1][1] else ["L", "S"]
    )  # S have larger z3
    return gmm_23_40, CLASSES


def fit_cluster_8():
    """Fit a GMM to resolve objects in cluster 8 into classes D and S.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()

    gmm_0_34 = GaussianMixture(n_components=2, random_state=17).fit(
        data.loc[data.cluster.isin([0, 34]), ["z1", "z3"]]
    )  # Fit cluster 0 and 34 in z1, z3 (0-indexed)

    CLASSES = (
        ["S", "D"] if gmm_0_34.means_[0][0] > gmm_0_34.means_[1][0] else ["D", "S"]
    )  # S have larger z1
    return gmm_0_34, CLASSES


def fit_cluster_10():
    """Fit a GMM to resolve objects in cluster 10 into classes R and S.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()

    gmm = GaussianMixture(n_components=2, random_state=17).fit(
        data.loc[data.cluster.isin([10]), ["z0", "z1"]]
    )  # Fit cluster 10  in z0, z1 (0-indexed)

    # R have larger z1
    CLASSES = ["R", "S"] if gmm.means_[0][1] > gmm.means_[1][1] else ["S", "R"]
    return gmm, CLASSES


def fit_cluster_13():
    """Fit a GMM to resolve objects in cluster 13 into C, Q, O.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """

    data = classy.data.load()
    X13 = data.loc[data.cluster == 13, ["z1", "z3"]]

    gmm = GaussianMixture(n_components=3, random_state=17).fit(X13)

    # Determine which component captures which class
    CLASSES = ["", "", ""]

    for ind, class_ in zip(np.argsort(gmm.means_[:, 0]), ["C", "Q", "O"]):
        CLASSES[ind] = class_
    return gmm, CLASSES


def fit_cluster_19():
    """Fit a GMM to resolve objects in cluster 19 into C and P.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """

    data = classy.data.load()
    data = data[data.cluster == 19]

    gmm_19 = GaussianMixture(
        n_components=2,
        random_state=4,
    ).fit(data.loc[data.h == 0, ["z0", "z3"]].values)

    # C are brighter
    CLASSES = ["C", "P"] if gmm_19.means_[0][0] < gmm_19.means_[1][0] else ["P", "C"]
    return gmm_19, CLASSES


def fit_cluster_23():
    """Fit a GMM to resolve objects in cluster 23 into L and M.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """

    data = classy.data.load()
    X23 = data.loc[data.cluster == 23, ["z0", "z3"]]

    gmm_23 = GaussianMixture(
        n_components=2,
        random_state=0,
        means_init=[[-0.6, -0.4], [-0.3, -0.3]],
        max_iter=1000,
    ).fit(X23)

    # L-Types have smaller z1
    CLASSES = ["L", "M"] if gmm_23.means_[0][0] < gmm_23.means_[1][0] else ["M", "L"]
    return gmm_23, CLASSES


def fit_cluster_24():
    """Fit a GMM to resolve objects in cluster 24 into K and M.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """

    data = classy.data.load()
    X24 = data.loc[data.cluster == 24, ["z2", "z3"]]

    gmm_24 = GaussianMixture(
        n_components=2,
        random_state=0,
        means_init=[[-0.25, -0.1], [-0.0, -0.2]],
        max_iter=1000,
    ).fit(X24)

    # K-Types have larger z3
    CLASSES = ["K", "M"] if gmm_24.means_[0][1] > gmm_24.means_[1][1] else ["M", "K"]
    return gmm_24, CLASSES


def fit_cluster_29(data):
    """Fit a GMM to resolve objects in cluster 29 into many classes.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """

    CLASSES = classy.ML_SETUP.CONTINUUM_CLUSTER[29]

    means = [
        np.mean(data.loc[data.class_ == class_, ["z0", "z1"]].values, axis=0)
        for class_ in CLASSES
    ]
    precisions = [
        np.linalg.inv(
            abs(np.cov(data.loc[data.class_ == class_, ["z0", "z1"]].values.T))
        )
        for class_ in CLASSES
    ]

    gmm_29 = GaussianMixture(
        n_components=len(CLASSES),
        random_state=0,
        means_init=means,
        precisions_init=precisions,
        max_iter=1,
    ).fit(data[["z0", "z1"]])

    return gmm_29, CLASSES


def fit_cluster_31():
    """Fit a GMM to resolve objects in cluster 31 into K and L.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()
    X31 = data.loc[data.cluster.isin([23, 24]), ["z2", "z3"]]

    gmm_31 = GaussianMixture(
        n_components=2,
        random_state=0,
    ).fit(X31)

    # K-Types have larger z3
    CLASSES = ["K", "L"] if gmm_31.means_[0][1] > gmm_31.means_[1][1] else ["L", "K"]
    return gmm_31, CLASSES


def fit_cluster_37():
    """Fit a GMM to resolve objects in cluster 37 into L and M.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()
    X37 = data.loc[data.cluster.isin([23, 46]), ["z1", "z3"]]

    gmm_37 = GaussianMixture(
        n_components=2,
        random_state=4,
    ).fit(X37)

    # Find out which component captures which class
    CLASSES = ["L", "M"] if gmm_37.means_[0][0] > gmm_37.means_[1][0] else ["M", "L"]
    return gmm_37, CLASSES


def fit_cluster_41():
    """Fit a GMM to resolve objects in cluster 41 into B and V.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()
    X41 = data.loc[data.cluster == 41, ["z0", "z1"]]

    gmm_41 = GaussianMixture(
        n_components=2,
        random_state=17,
    ).fit(X41)

    # B-Types have smaller z1
    CLASSES = ["B", "V"] if gmm_41.means_[0][1] < gmm_41.means_[1][1] else ["V", "B"]
    return gmm_41, CLASSES


def fit_cluster_43():
    """Fit a GMM to resolve objects in cluster 43 into D and S.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()
    X43 = data.loc[data.cluster == 43, ["z1", "z3"]]

    gmm_43 = GaussianMixture(
        n_components=2,
        random_state=17,
    ).fit(X43)

    # D-Types have smaller z3
    CLASSES = ["D", "S"] if gmm_43.means_[0][1] < gmm_43.means_[1][1] else ["S", "D"]
    return gmm_43, CLASSES


def fit_cluster_44():
    """Fit a GMM to resolve objects in cluster 44 into E and S.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the latent scores.
    list
        The classes represented in order by the model components.
    """
    data = classy.data.load()
    X44 = data.loc[data.cluster == 44]
    X44 = X44.loc[~pd.isna(data_cluster.pV), "pV"].values.reshape(-1, 1)

    gmm_44 = GaussianMixture(
        n_components=2,
        random_state=17,
    ).fit(X44)

    # E-Types have larger pV
    CLASSES = ["E", "S"] if gmm_44.means_[0] > gmm_44.means_[1] else ["S", "E"]
    return gmm_44, CLASSES


def fit_complex_emp():
    """Fit the X complex cluster using a Gaussian mixture model with three components.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the X complex albedo distribution.
    dict
        Dictionary containing E, M, P as keys and their mean and std as values
    """

    # Get original classy input data
    data = classy.data.load()
    data_x = data.loc[data.cluster.isin(classy.ML_SETUP.X_COMPLEX)]
    x_pV = data_x.loc[~pd.isna(data_x.pV), "pV"].values

    # Fit E, M, P
    gmm = GaussianMixture(n_components=3, random_state=17).fit(x_pV.reshape(-1, 1))

    # Find out which component captures which class
    CLASSES = ["", "", ""]

    for ind, class_ in zip(np.argsort(gmm.means_.flatten()), ["P", "M", "E"]):
        CLASSES[ind] = class_

    return gmm, CLASSES


FIT_CLUSTER_FUNCTIONS = {
    4: fit_cluster_4,
    8: fit_cluster_8,
    10: fit_cluster_10,
    13: fit_cluster_13,
    19: fit_cluster_19,
    23: fit_cluster_23,
    24: fit_cluster_24,
    31: fit_cluster_31,
    37: fit_cluster_37,
    41: fit_cluster_41,
    43: fit_cluster_43,
    44: fit_cluster_44,
    "emp": fit_complex_emp,
}
