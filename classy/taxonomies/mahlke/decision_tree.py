import numpy as np
import pandas as pd

from sklearn.mixture import GaussianMixture

from . import defs
from classy import index
from classy.taxonomies.mahlke import gmm


def assign_classes(data):
    """Convert the cluster probabilites into class probabilites based on the decision tree.

    Parameters
    ----------
    data : pd.DataFrame
        Input observations which contain latent scores and cluster probabilites.

    Returns
    -------
    pd.DataFrame
        The input dataframe with additional columns containing asteroid class probabilites.
    """

    # Instantiate the class probability columns
    for class_ in defs.CLASSES:
        data[f"class_{class_}"] = 0

    # Load trained mixture models
    GMMS, CLASSES = gmm.load_mixture_models()

    # ------
    # Compute class probabilites

    # 1. Core cluster probability is translated one-to-one to class probability
    for cluster, class_ in defs.CORE_CLUSTER.items():
        data[f"class_{class_}"] += data[f"cluster_{cluster}"]

    # 2. Continuum cluster follow decision tree
    for cluster in defs.X_COMPLEX:
        if cluster == 37 and (
            pd.isna(data["pV"].values[0]) or data["pV"].values[0] > -1
        ):
            # Split L from M in cluster 37
            MASK_37 = GMMS[37].predict(data[["z1", "z3"]])

            # Let's just say explicit is better than implicit
            LMASK = (
                [True if m == 0 else False for m in MASK_37]
                if CLASSES[37][0] == "L"
                else [False if m == 0 else True for m in MASK_37]
            )
            MMASK = (
                [True if m == 0 else False for m in MASK_37]
                if CLASSES[37][0] == "M"
                else [False if m == 0 else True for m in MASK_37]
            )

            # Classify M-types
            data.loc[MMASK] = data.loc[MMASK].apply(
                lambda sample: resolve_emp_classes(
                    sample, cluster, GMMS["emp"], CLASSES["emp"]
                ),
                axis=1,
            )
            # Rest goes to L-Types
            data.loc[LMASK, "class_L"] += data.loc[LMASK, "cluster_37"]
            continue

        data = data.apply(
            lambda sample: resolve_emp_classes(
                sample, cluster, GMMS["emp"], CLASSES["emp"]
            ),
            axis=1,
        )

    for cluster in defs.CONTINUUM_CLUSTER:
        if cluster == 29:  # taken care of below
            continue
        elif cluster == 30:
            data = data.apply(resolve_cluster_30, axis=1)
        else:
            data = data.apply(
                lambda sample: RESOLVE_CLUSTER_FUNCTIONS[cluster](
                    sample, GMMS[cluster], CLASSES[cluster]
                ),
                axis=1,
            )

    # Get E types from K and L clusters
    data = data.apply(
        lambda sample: resolve_E(sample, GMMS["emp"], CLASSES["emp"]), axis=1
    )

    data["class_"] = data.apply(
        lambda sample: defs.CLASSES[
            np.argmax([sample[f"class_{class_}"] for class_ in defs.CLASSES])
        ],
        axis=1,
    )

    # Build class GMM for cluster 29 resolution
    GMM_29, CLASSES_29 = index.data.load("gmm", 29)

    data = data.apply(
        lambda sample: resolve_cluster_29(sample, GMM_29, CLASSES_29), axis=1
    )

    # Redo this after 29 was assigned, should not change much
    data["class_"] = data.apply(
        lambda sample: defs.CLASSES[
            np.argmax([sample[f"class_{class_}"] for class_ in defs.CLASSES])
        ],
        axis=1,
    )

    data["DIFFUSE"] = data["cluster"].apply(
        lambda cluster: True if cluster in defs.DIFFUSE_CLUSTER else False
    )

    return data


def resolve_E(sample, GMM_EMP, CLASSES_EMP):
    """Resolve spectral similarity between K, L, M and E using albedo"""

    if pd.isna(sample.pV):
        return sample

    # If albedo wise it's an E-type, sort the K and L probability to E
    label = GMM_EMP.predict(np.array([sample.pV]).reshape(-1, 1))

    if CLASSES_EMP[label[0]] == "E":
        for class_ in ["K", "L", "M"]:
            sample["class_E"] += 2 * sample[f"class_{class_}"] / 3
            sample[f"class_{class_}"] /= 3

    return sample


def resolve_emp_classes(sample, cluster, GMM_EMP, CLASSES):
    if pd.isna(sample.pV):
        sample["class_X"] += sample[f"cluster_{cluster}"]
        return sample

    # Class probabilities for E, M, P
    probs = GMM_EMP.predict_proba(np.array(sample.pV).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample[f"cluster_{cluster}"]

    return sample


def resolve_cluster_4(sample, GMM_23_40, CLASSES):
    """
    Notes
    -----
    The objects are resolved based on their distance to clusters 23 and 40 in z2-z3 (0-indexed).
    """

    # Class probabilities for E, M, P
    probs = GMM_23_40.predict_proba(np.array(sample[["z2", "z3"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_4"]

    return sample


def resolve_cluster_8(sample, GMM_0_34, CLASSES):
    # Class probabilities for E, M, P
    probs = GMM_0_34.predict_proba(np.array(sample[["z1", "z3"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_8"]

    return sample


def resolve_cluster_10(sample, GMM, CLASSES):
    # Class probabilities for E, M, P
    probs = GMM.predict_proba(np.array(sample[["z0", "z1"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_10"]

    return sample


def resolve_cluster_13(sample, GMM_13, CLASSES):
    # Class probabilities for E, M, P
    probs = GMM_13.predict_proba(np.array(sample[["z1", "z3"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_13"]

    return sample


def resolve_cluster_19(sample, GMM_19, CLASSES):
    # No albedo -> assign to default class, C
    # if pd.isna(sample.pV):
    #     sample[f"class_C"] += sample[f"cluster_19"]
    #     return sample

    # Class probabilities for E, M, P
    probs = GMM_19.predict_proba(np.array([sample[["z0", "z3"]]]))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_19"]

    return sample


def resolve_cluster_23(sample, GMM_23, CLASSES):
    # Class probabilities for L, M
    probs = GMM_23.predict_proba(np.array(sample[["z0", "z3"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_23"]

    return sample


def resolve_cluster_24(sample, GMM_24, CLASSES):
    # Class probabilities for L, M
    probs = GMM_24.predict_proba(np.array(sample[["z2", "z3"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_24"]

    return sample


def resolve_cluster_31(sample, GMM_31, CLASSES):
    # Class probabilities for L, M
    probs = GMM_31.predict_proba(np.array(sample[["z2", "z3"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_31"]

    return sample


def resolve_cluster_41(sample, GMM_41, CLASSES):
    # Class probabilities for L, M
    probs = GMM_41.predict_proba(np.array(sample[["z0", "z1"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_41"]

    return sample


def resolve_cluster_43(sample, GMM_43, CLASSES):
    # Class probabilities for L, M
    probs = GMM_43.predict_proba(np.array(sample[["z1", "z3"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_43"]

    return sample


def resolve_cluster_44(sample, GMM_44, CLASSES):
    if pd.isna(sample.pV):
        # Default if no albedo present is S
        probs = [[1, 0]] if CLASSES[0] == "S" else [[0, 1]]
    else:
        # Class probabilities for S, E
        probs = GMM_44.predict_proba(np.array(sample["pV"]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_44"]

    return sample


LM23 = {}


def resolve_cluster_29(sample, GMM, CLASSES):
    """ """

    probs = GMM.predict_proba(np.array(sample[["z0", "z1"]]).reshape(1, -1))

    for j, class_ in enumerate(CLASSES):
        # Add class probabilites scaled by cluster probability
        sample[f"class_{class_}"] += probs[0][j] * sample["cluster_29"]
    return sample


def resolve_cluster_37():
    data, _ = ml.load_data()
    data_cluster = data[data.cluster.isin([23, 46])]
    X37 = data_cluster[["z1", "z3"]]

    gmm_37 = GaussianMixture(
        n_components=2,
        random_state=4,
    ).fit(X37)

    # Find out which component captures which class
    CLASSES = ["L", "M"] if gmm_37.means_[0][0] > gmm_37.means_[1][0] else ["M", "L"]
    return gmm_37, CLASSES


def resolve_complex_emp():
    """Fit the X complex cluster using a Gaussian mixture model with three components.

    Returns
    -------
    sklearn.mixture.GaussianMixture
        The mixture model trained on the X complex albedo distribution.
    dict
        Dictionary containing E, M, P as keys and their mean and std as values
    """

    # Get data
    data, _ = ml.load_data()
    data_x = data.loc[data.cluster.isin(defs.X_COMPLEX)]
    x_pV = data_x.loc[~pd.isna(data_x.pV), "pV"].values

    # Fit E, M, P
    gmm = GaussianMixture(n_components=3, random_state=17).fit(x_pV.reshape(-1, 1))

    # Find out which component captures which class
    CLASSES = ["", "", ""]

    for ind, class_ in zip(np.argsort(gmm.means_.flatten()), ["P", "M", "E"]):
        CLASSES[ind] = class_

    return gmm, CLASSES


def resolve_cluster_30(sample):
    """Heurisitc decision tree branch added after publication. This cluster contains D-types."""

    if not pd.isna(sample.pV):
        if sample.pV > np.log10(0.14):
            sample.class_S += sample.cluster_30
        else:
            sample.class_D += sample.cluster_30
    else:
        if sample.z1 > 0:
            sample.class_S += sample.cluster_30
        else:
            sample.class_D += sample.cluster_30
    return sample


RESOLVE_CLUSTER_FUNCTIONS = {
    4: resolve_cluster_4,
    8: resolve_cluster_8,
    10: resolve_cluster_10,
    13: resolve_cluster_13,
    19: resolve_cluster_19,
    23: resolve_cluster_23,
    24: resolve_cluster_24,
    30: resolve_cluster_30,
    31: resolve_cluster_31,
    37: resolve_cluster_37,
    41: resolve_cluster_41,
    43: resolve_cluster_43,
    44: resolve_cluster_44,
    "emp": resolve_complex_emp,
}
