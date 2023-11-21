import pickle

import numpy as np
from sklearn.mixture import GaussianMixture

import classy

import warnings

# Hide harmless warning by sklearn
warnings.filterwarnings("ignore", message="X has feature names")


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

        gmm, classes = classy.data.load("gmm", cluster=cluster)

        # Not sure that we should be refitting if files are missing
        # Possibly better to throw an error

        # if gmm is None:
        #     gmm, classes = gmm_function()

        #     with PATH_GMM.open("wb") as file_:
        #         pickle.dump((gmm, classes), file_)

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
    29: fit_cluster_29,
    31: fit_cluster_31,
    37: fit_cluster_37,
    41: fit_cluster_41,
    43: fit_cluster_43,
    44: fit_cluster_44,
    "emp": fit_complex_emp,
}

GMM = {
    4: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.7211166, 0.2788834]),
        "means_": np.array([[-0.1056937, -0.0161601], [-0.21268019, -0.35185828]]),
        "covariances_": np.array(
            [
                [[0.00709845, -0.0056863], [-0.0056863, 0.00941784]],
                [[0.00271878, 0.00132316], [0.00132316, 0.00322383]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[11.86911581, 11.487474], [0.0, 14.34030559]],
                [[19.17843942, -9.58162189], [0.0, 19.68794058]],
            ]
        ),
        "precisions_": np.array(
            [
                [[272.83796902, 164.73388768], [164.73388768, 205.64436442]],
                [[459.62001673, -188.64240251], [-188.64240251, 387.61500436]],
            ]
        ),
        "n_iter_": 6,
        "lower_bound_": 1.9363577976713742,
        "classes": ["S", "L"],
    },
    8: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.71491736, 0.28508264]),
        "means_": np.array([[0.23219367, -0.15056513], [-0.33063635, -0.18298176]]),
        "covariances_": np.array(
            [
                [[0.00824365, -0.00092853], [-0.00092853, 0.00346154]],
                [[0.01692522, -0.00146735], [-0.00146735, 0.00124619]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[11.0138782, 1.94404148], [0.0, 17.2594753]],
                [[7.68657369, 2.59171782], [0.0, 29.89435528]],
            ]
        ),
        "precisions_": np.array(
            [
                [[125.08481035, 33.55313594], [33.55313594, 297.88948746]],
                [[65.80041633, 77.47773317], [77.47773317, 893.6724779]],
            ]
        ),
        "n_iter_": 2,
        "lower_bound_": 1.867457601830532,
        "classes": ["S", "D"],
    },
    10: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.65313849, 0.34686151]),
        "means_": np.array([[0.03829537, 0.43809247], [0.01418301, 0.0484349]]),
        "covariances_": np.array(
            [
                [[0.01142504, -0.00634132], [-0.00634132, 0.01180958]],
                [[0.01126896, -0.00599787], [-0.00599787, 0.0070489]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[9.3555889, 6.09603168], [0.0, 10.9831039]],
                [[9.42015733, 8.57064954], [0.0, 16.10275986]],
            ]
        ),
        "precisions_": np.array(
            [
                [[124.68864582, 66.95334929], [66.95334929, 120.62857135]],
                [[162.1953977, 138.01111144], [138.01111144, 259.29887517]],
            ]
        ),
        "n_iter_": 2,
        "lower_bound_": 1.2892371816256614,
        "classes": ["R", "S"],
    },
    13: {
        "n_components": 3,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.4448521, 0.44513169, 0.11001621]),
        "means_": np.array(
            [
                [0.15870393, 0.39826079],
                [-0.21482756, 0.11172012],
                [0.58539938, 0.79744303],
            ]
        ),
        "covariances_": np.array(
            [
                [[0.06214277, -0.02879292], [-0.02879292, 0.05085928]],
                [[0.04802479, -0.01846741], [-0.01846741, 0.04872641]],
                [[0.01371203, 0.02253366], [0.02253366, 0.03772069]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[4.01148067, 2.39206151], [0.0, 5.16270375]],
                [[4.56317638, 1.8847923], [0.0, 4.90143269]],
                [[8.53982657, -62.56107944], [0.0, 38.06924871]],
            ]
        ),
        "precisions_": np.array(
            [
                [[21.81393545, 12.34950494], [12.34950494, 26.65351005]],
                [[24.3750207, 9.2381826], [9.2381826, 24.02404237]],
                [[3986.81729859, -2381.65329304], [-2381.65329304, 1449.26769768]],
            ]
        ),
        "n_iter_": 8,
        "lower_bound_": -0.22500206036739426,
        "classes": ["Q", "C", "O"],
    },
    19: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 4,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.5328365, 0.4671635]),
        "means_": np.array([[-0.40520325, 0.09147796], [-0.18314098, -0.04670646]]),
        "covariances_": np.array(
            [
                [[0.01080164, -0.00374168], [-0.00374168, 0.00279024]],
                [[0.01332408, -0.00336178], [-0.00336178, 0.00249049]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[9.62177459, 8.96155749], [0.0, 25.87061804]],
                [[8.66326044, 6.22599577], [0.0, 24.67610364]],
            ]
        ),
        "precisions_": np.array(
            [
                [[172.88805881, 231.84103078], [231.84103078, 669.28887766]],
                [[113.81510482, 153.63331678], [153.63331678, 608.91009075]],
            ]
        ),
        "n_iter_": 4,
        "lower_bound_": 2.1270578328027447,
        "classes": ["C", "P"],
    },
    23: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 1000,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 0,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": np.array([[-0.6, -0.4], [-0.3, -0.3]]),
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.53776527, 0.46223473]),
        "means_": np.array([[-0.6087688, -0.3723638], [-0.24827723, -0.32997764]]),
        "covariances_": np.array(
            [
                [[0.03851111, -0.00583931], [-0.00583931, 0.00264067]],
                [[0.02649454, -0.00628346], [-0.00628346, 0.00270168]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[5.09573656, 3.61911459], [0.0, 23.86859912]],
                [[6.14358464, 6.81369314], [0.0, 28.73029313]],
            ]
        ),
        "precisions_": np.array(
            [
                [[39.06452149, 86.38319537], [86.38319537, 569.71002412]],
                [[84.17004638, 195.75940108], [195.75940108, 825.42974312]],
            ]
        ),
        "n_iter_": 9,
        "lower_bound_": 1.5288709025173883,
        "classes": ["L", "M"],
    },
    24: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 1000,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 0,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": np.array([[-0.25, -0.1], [-0.0, -0.2]]),
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.60891254, 0.39108746]),
        "means_": np.array([[-0.20247505, -0.11798039], [-0.10295211, -0.17997708]]),
        "covariances_": np.array(
            [
                [[0.00249241, -0.00144336], [-0.00144336, 0.00383961]],
                [[0.00144166, -0.00123541], [-0.00123541, 0.00256751]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[20.03041001, 10.56631578], [0.0, 18.24601267]],
                [[26.3371182, 22.06088754], [0.0, 25.74405107]],
            ]
        ),
        "precisions_": np.array(
            [
                [[512.86435449, 192.79313153], [192.79313153, 332.91697823]],
                [[1180.32655453, 567.93661561], [567.93661561, 662.75616559]],
            ]
        ),
        "n_iter_": 7,
        "lower_bound_": 2.911964502989549,
        "classes": ["K", "M"],
    },
    29: {
        "n_components": 9,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 1,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 0,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": np.array(
            [
                [2.0386143, 0.04955636],
                [-1.56448175, -0.34882175],
                [-0.70625912, -0.44531369],
                [1.44004601, -0.40051904],
                [0.12543876, -0.16758023],
                [0.05483219, -0.4922519],
                [-0.56658777, 0.25133016],
                [0.19548804, 0.22470332],
                [-0.27216598, 0.91158394],
            ]
        ),
        "precisions_init": np.array(
            [
                [[1.84394153, -3.80252439], [-3.80252439, 38.32649303]],
                [[9.68320564, -9.9310649], [-9.9310649, 30.26038902]],
                [[11.1954219, -9.28547717], [-9.28547717, 87.66713605]],
                [[9.01427595, -16.48154221], [-16.48154221, 70.98563429]],
                [[7.92257691, -9.02339434], [-9.02339434, 89.44367449]],
                [[8.71430844, -0.66043721], [-0.66043721, 78.83325074]],
                [[12.88999441, -2.50538581], [-2.50538581, 50.47007678]],
                [[4.56655064, -0.71810379], [-0.71810379, 41.36351014]],
                [[3.41240473, -0.13271888], [-0.13271888, 28.3671353]],
            ]
        ),
        "n_features_in_": 2,
        "converged_": False,
        "weights_": np.array(
            [
                0.03967816,
                0.05249065,
                0.11636656,
                0.05898632,
                0.12579116,
                0.08566675,
                0.16514093,
                0.26676314,
                0.08911632,
            ]
        ),
        "means_": np.array(
            [
                [1.55477339, 0.06038656],
                [-1.24996815, -0.19421475],
                [-0.65951031, -0.45678704],
                [1.46124677, -0.44492014],
                [0.09318872, -0.12445942],
                [-0.04232157, -0.49536275],
                [-0.35774105, 0.23446454],
                [0.26792699, 0.24086304],
                [-0.16582471, 0.82819217],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[1.16186857, 0.28659047], [0.0, 4.70601621]],
                [[2.2028083, -0.85492707], [0.0, 5.23163344]],
                [[3.30968329, -0.48715048], [0.0, 9.6010345]],
                [[1.95713776, -0.24678597], [0.0, 6.28355221]],
                [[2.80610126, -0.38917397], [0.0, 7.30738822]],
                [[3.23043556, -0.67645892], [0.0, 9.77762209]],
                [[3.50382304, 0.1715472], [0.0, 8.91465712]],
                [[2.78916541, -0.79892404], [0.0, 10.72593511]],
                [[1.68195094, 0.32108312], [0.0, 4.29674542]],
            ]
        ),
        "covariances_": np.array(
            [
                [[0.74077445, -0.04511223], [-0.04511223, 0.04790096]],
                [[0.2060851, 0.03367738], [0.03367738, 0.04203976]],
                [[0.09129082, 0.00463204], [0.00463204, 0.01108338]],
                [[0.26107014, 0.01025351], [0.01025351, 0.02573004]],
                [[0.12699696, 0.00676355], [0.00676355, 0.01908753]],
                [[0.09582478, 0.00662958], [0.00662958, 0.01091871]],
                [[0.08145461, -0.00156745], [-0.00156745, 0.01261335]],
                [[0.1285439, 0.00957463], [0.00957463, 0.00940537]],
                [[0.35348692, -0.02641504], [-0.02641504, 0.05613917]],
            ]
        ),
        "precisions_": np.array(
            [
                [[1.43207266, 1.34869939], [1.34869939, 22.14658861]],
                [[5.58326468, -4.47266505], [-4.47266505, 27.36998847]],
                [[11.19131905, -4.67714854], [-4.67714854, 92.17986355]],
                [[3.89129155, -1.55069255], [-1.55069255, 39.48302833]],
                [[8.02566065, -2.84384526], [-2.84384526, 53.39792253]],
                [[10.89331058, -6.61415967], [-6.61415967, 95.60189365]],
                [[12.30620434, 1.52928448], [1.52928448, 79.47111156]],
                [[8.41772331, -8.56920737], [-8.56920737, 115.04568395]],
                [[2.93205332, 1.3796124], [1.3796124, 18.46202117]],
            ]
        ),
        "n_iter_": 1,
        "lower_bound_": -2.1472411750865272,
        "classes": ["A", "B", "C", "D", "M", "P", "Q", "S", "V"],
    },
    31: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 0,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.57642888, 0.42357112]),
        "means_": np.array([[-0.16423236, -0.14662143], [-0.21598056, -0.36027759]]),
        "covariances_": np.array(
            [
                [[0.00425721, -0.002635], [-0.002635, 0.00444454]],
                [[0.00263749, 0.00097987], [0.00097987, 0.00238389]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[15.32630223, 11.66871312], [0.0, 18.85245182]],
                [[19.47172206, -8.26638746], [0.0, 22.25050572]],
            ]
        ),
        "precisions_": np.array(
            [
                [[371.05440569, 219.9838518], [219.9838518, 355.41493961]],
                [[447.48112156, -183.93130139], [-183.93130139, 495.08500469]],
            ]
        ),
        "n_iter_": 3,
        "lower_bound_": 2.366416091552324,
        "classes": ["K", "L"],
    },
    37: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 4,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.2951992, 0.7048008]),
        "means_": np.array([[0.07721267, -0.35738188], [-0.18364554, -0.1314112]]),
        "covariances_": np.array(
            [
                [[0.01253078, -0.00392617], [-0.00392617, 0.00287503]],
                [[0.00700681, -0.00536976], [-0.00536976, 0.00993792]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[8.93328069, 7.72548859], [0.0, 24.65667559]],
                [[11.9464766, 10.04318011], [0.0, 13.10498501]],
            ]
        ),
        "precisions_": np.array(
            [
                [[139.48667777, 190.4848659], [190.4848659, 607.95165097]],
                [[243.58376991, 131.61572473], [131.61572473, 171.74063203]],
            ]
        ),
        "n_iter_": 6,
        "lower_bound_": 1.8342061908155998,
        "classes": ["L", "M"],
    },
    41: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.57142857, 0.42857143]),
        "means_": np.array([[-2.27406628, -0.0696328], [-2.14709323, 0.43575892]]),
        "covariances_": np.array(
            [
                [[0.00447319, 0.00347859], [0.00347859, 0.0054108]],
                [[0.01712456, 0.00304449], [0.00304449, 0.0005493]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[14.95173376, -14.95027401], [0.0, 19.22486281]],
                [[7.64170427, -62.72954274], [0.0, 352.83942862]],
            ]
        ),
        "precisions_": np.array(
            [
                [[447.06503544, -287.41696674], [-287.41696674, 369.59534988]],
                [[3993.39117629, -22133.45601707], [-22133.45601707, 124495.66238811]],
            ]
        ),
        "n_iter_": 2,
        "lower_bound_": 3.1274140654867755,
        "classes": ["B", "V"],
    },
    43: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 2,
        "converged_": True,
        "weights_": np.array([0.34931318, 0.65068682]),
        "means_": np.array([[-0.12423195, -0.67186996], [-0.07423989, -0.2012018]]),
        "covariances_": np.array(
            [
                [[0.00935, -0.00976373], [-0.00976373, 0.01342925]],
                [[0.00326038, -0.00461372], [-0.00461372, 0.03041635]],
            ]
        ),
        "precisions_cholesky_": np.array(
            [
                [[10.3417552, 18.36411671], [0.0, 17.58594217]],
                [[17.51322871, 9.15584743], [0.0, 6.47015225]],
            ]
        ),
        "precisions_": np.array(
            [
                [[444.19268316, 322.95029448], [322.95029448, 309.26536198]],
                [[390.54272193, 59.23972689], [59.23972689, 41.86287018]],
            ]
        ),
        "n_iter_": 9,
        "lower_bound_": 1.4375830291789904,
        "classes": ["D", "S"],
    },
    44: {
        "n_components": 2,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 1,
        "converged_": True,
        "weights_": np.array([0.84215271, 0.15784729]),
        "means_": np.array([[-0.6611763], [-0.22654249]]),
        "covariances_": np.array([[[0.01102564]], [[0.00028669]]]),
        "precisions_cholesky_": np.array([[[9.5235341]], [[59.05990684]]]),
        "precisions_": np.array([[[90.69770171]], [[3488.07259579]]]),
        "n_iter_": 5,
        "lower_bound_": 0.6875220210357678,
        "classes": ["S", "E"],
    },
    "emp": {
        "n_components": 3,
        "tol": 0.001,
        "reg_covar": 1e-06,
        "max_iter": 100,
        "n_init": 1,
        "init_params": "kmeans",
        "random_state": 17,
        "warm_start": False,
        "verbose": 0,
        "verbose_interval": 10,
        "covariance_type": "full",
        "weights_init": None,
        "means_init": None,
        "precisions_init": None,
        "n_features_in_": 1,
        "converged_": True,
        "weights_": np.array([0.35790386, 0.13528, 0.50681614]),
        "means_": np.array([[-1.30343358], [-0.22908327], [-0.83778206]]),
        "covariances_": np.array([[[0.02991983]], [[0.01038391]], [[0.01727975]]]),
        "precisions_cholesky_": np.array(
            [[[5.78123217]], [[9.81340145]], [[7.60731253]]]
        ),
        "precisions_": np.array([[[33.42264544]], [[96.3028481]], [[57.87120399]]]),
        "n_iter_": 5,
        "lower_bound_": -0.3012371887128191,
        "classes": ["P", "E", "M"],
    },
}
