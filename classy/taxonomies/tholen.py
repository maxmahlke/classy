"""Classification of asteroids following Tholen 1984."""
from functools import lru_cache

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import core
from classy.utils.logging import logger
from classy import preprocessing
from classy import utils
from classy import taxonomies

CLASSES = ["A", "B", "C", "D", "E", "F", "G", "M", "P", "Q", "S", "R", "T", "V", "X"]


def is_classifiable(spec):
    """Check if spectrum can be classified based on the wavelength range.

    Parameters
    ----------
    taxonomy : str
        The taxonomic scheme to check.

    Returns
    -------
    bool
        True if the spectrum can be classified, else False.
    """

    if spec.wave.min() > min(WAVE) or spec.wave.max() < max(WAVE):
        # Check if the extrapolation would be sufficient
        if preprocessing._within_extrapolation_limit(
            spec.wave.min(), spec.wave.max(), min(WAVE), max(WAVE)
        ):
            logger.warning(
                f"{spec.name} will be extrapolated for Tholen classification."
            )
            spec._extrapolated_for_tholen = True
            return True

        logger.warning(
            f"[{spec.name}]: Insufficient wavelength range for Tholen taxonomy."
        )
        return False
    return True


# ------
# Functions for preprocessing
def preprocess(spec):
    """Preprocess a spectrum for classification following Tholen 1984.

    Parameters
    ----------
    spec : classy.Spectrum
        The spectrum to classify.
    """
    spec.resample(WAVE, fill_value="extrapolate")
    spec.normalize(at=0.55)


# ------
# Functions for classification
@lru_cache(maxsize=None)
def load_classification():
    """Load the Tholen 1984 classification results like PC scores and classes from file.

    Returns
    -------
    pd.DataFrame
        The classification results of the 405 high-quality ECAS observations.
    """

    # Launch same ECAS method if data not present
    PATH_DATA = config.PATH_DATA / "tholen1984/scores.csv"

    if not PATH_DATA.is_file():
        utils.download.from_github(host="tholen1984", which="scores", path=PATH_DATA)

    return pd.read_csv(PATH_DATA, dtype={"number": "Int64"})


def load_templates():
    """Load the spectral templates of the Tholen classes.

    Returns
    -------
    dict
        Dictionary with classes (str) as key and templates as values (classy.Spectrum).
    """

    templates_ = {}

    for class_, props in TEMPLATES.items():
        wave = [0.337, 0.359, 0.437, 0.550, 0.701, 0.853, 0.948, 1.041]
        refl = []
        refl_err = []

        for r, r_err in zip(props["refl_mean"][:3], props["refl_std"][:3]):
            refl.append(np.power(10, -0.4 * (r)))
            re = np.abs(r) * np.abs(0.4 * np.log(10) * r_err)
            refl_err.append(re)

        refl.append(1)  # v-filter
        refl_err.append(0)  # v-filter

        for r, r_err in zip(props["refl_mean"][3:], props["refl_std"][3:]):
            refl.append(np.power(10, -0.4 * (-r)))
            re = np.abs(r) * np.abs(0.4 * np.log(10) * r_err)
            refl_err.append(re)

        refl = np.array(refl)
        refl_err = np.array(refl_err)

        template = core.Spectrum(
            wave=WAVE,
            refl=refl,
            refl_err=refl_err,
            class_=class_,
            pV=props["alb_mean"],
            pV_err=props["alb_std"],
            source="Tholen 1984",
        )
        templates_[class_] = template
    return templates_


def classify(spec):
    """Classify a spectrum following Tholen 1984.

    Parameters
    ----------
    spec : classy.Spectrum
        The spectrum to classify.

    Notes
    -----
    The resulting class is added as ``class_tholen`` attribute.
    """

    # Is it classifiable?
    if spec.wave.min() > 0.437 or spec.wave.max() < 0.948:
        spec.class_tholen = ""
        spec.scores_tholen = [np.nan] * 7
        spec.colors_ecas = [np.nan] * 7
        logger.error(
            f"{spec.name}:  Cannot classify following Tholen 1984 - insufficient wavelength coverage."
        )
        return

    # Compute ECAS colours
    refl_v = 1
    colors_ecas = np.array(
        # s, u, b
        [-2.5 * np.log10(r / refl_v) for r in spec.refl[:3]]
        # v
        # + [1]
        # w, x, p, z
        + [-2.5 * np.log10(refl_v / r) for r in spec.refl[4:]]
    )

    # Normalize to ECAS dataset
    colors_ecas = (colors_ecas - DATA_MEAN) / DATA_STD

    # Compute Tholen scores
    spec.scores_tholen = np.dot(colors_ecas, taxonomies.tholen.EIGENVECTORS.T)

    # Apply decision tree
    class_ = taxonomies.tholen.decision_tree(spec)
    add_classification_results(spec, results={"class_tholen": class_})


def add_classification_results(spec, results=None):
    if results is None:
        spec.class_tholen = ""
        spec.scores_tholen = [np.nan] * 7
        return

    for key, val in results.items():
        setattr(spec, key, val)


def decision_tree(spec):
    """Decision tree to identify taxonomic class in Tholen 1984 system.

    Parameters
    ----------
    spec : classy.Spectrum
        The spectrum to classify.

    Returns
    -------
    str
        The Tholen classification of this spectrum.

    Notes
    -----
    The spectrum must have the Tholen PC scores as ``scores_tholen`` attribute.
    """
    if hasattr(spec, "pV"):
        spec.pV = np.log10(spec.pV)
    elif hasattr(spec, "target") and isinstance(spec.target, rocks.Rock):
        spec.pV = np.log10(spec.target.albedo.value)
    else:
        spec.pV = np.nan

    # Load the PCs of all ECAS asteroids
    tholen = load_classification()
    tholen_scores = tholen[["PC1", "PC2", "PC3", "PC4", "PC5", "PC6", "PC7"]].values

    # Find the classification of the closest asteroid in PC space
    distances = [
        np.linalg.norm(spec.scores_tholen - ecas_scores)
        for ecas_scores in tholen_scores
    ]
    class_ = tholen.loc[np.argmin(distances), "class_"]

    if not isinstance(class_, str) and np.isnan(class_):
        raise ValueError(
            "The ECAS scores file is missing classifications. Clean the PDS cache using 'classy status' and try again."
        )

    # Resolve ambiguity the simple way
    if len(class_) == 2:
        class_ = class_[0]

    # Pass through albedo decision tree
    if class_ in ["E", "M", "P", "X"]:
        if np.isnan(spec.pV):
            return "X"
        elif -2.5 * np.log10(spec.pV) > 3:
            return "P"
        elif -2.5 * np.log10(spec.pV) > 1.4:
            return "M"
        return "E"

    if class_ in ["C", "F", "B", "G"]:
        if -2.5 * np.log10(spec.pV) <= 1.4:
            return "E"

    if class_ in ["C", "B"]:
        if -2.5 * np.log10(spec.pV) > 3:
            return "C"
        return "B"

    return class_


# ------
# Functions for plotting
def plot_pc_space(ax, spectra):
    """Plot the distribution of classified spectra and the ECAS spectra in the Tholen PC space.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The matplotlib axis instance to plot to.
    spectra : classy.Spectra or list of classy.Spectrum
        One or more spectra which were previously classified in the Tholen system.

    Returns
    -------
    matplotlib.axes.Axes
        The matplotlib axis with the plotted classification results.
    """

    opts_text = dict(va="center", ha="center", clip_on=True)

    # ------
    # Add the distribution of the ECAS asteroids
    tholen = load_classification()

    for _, ast in tholen.iterrows():
        # Dummy to ensure proper plot limits
        ax.scatter(ast.PC1, ast.PC2, alpha=0)

        # Add asteroid position in PC space represented by its number
        ax.text(ast.PC1, ast.PC2, str(ast.number), color="lightgray", **opts_text)

    # ------
    # Add the mean positions of the main classes
    for class_, pcs in tholen.groupby("class_"):
        # Only add the core classe
        if len(class_) > 1:
            continue

        pc0 = np.mean(pcs.PC1)
        pc1 = np.mean(pcs.PC2)

        # Small offsets for readability
        if class_ == "E":
            pc0 += 0.05
        elif class_ == "P":
            pc0 += 0.09

        # Add class indicator
        ax.text(pc0, pc1, class_, size=14, color="black", **opts_text)

    # ------
    # Add classified spectra
    for spec in spectra:
        if not spec.class_tholen:
            logger.debug(f"[{spec.name}]: Not classified in Tholen 1984 system.")
            continue

        ax.scatter(
            spec.scores_tholen[0],
            spec.scores_tholen[1],
            marker="d",
            c=spec._color,
            s=40,
            label=f"{spec.source + ': ' if hasattr(spec, 'source') else ''}{spec.class_tholen}",
            zorder=100,
        )

    # ------
    # Final additions et voila
    ax.axvline(0, ls=":", c="gray")
    ax.axhline(0, ls=":", c="gray")
    ax.legend()
    ax.set(xlabel="Principal Score 1", ylabel="Principal Score 2")

    return ax


# ------
# Defintions

# Central wavelengths of the ECAS colours
WAVE = np.array([0.337, 0.359, 0.437, 0.550, 0.701, 0.853, 0.948, 1.041])
WAVE = list(WAVE)

# Mean and standard deviation of ECAS colours, Tholen 1984 Table II
DATA_MEAN = np.array([0.325, 0.234, 0.089, 0.091, 0.105, 0.103, 0.111])
DATA_STD = np.array([0.221, 0.173, 0.092, 0.081, 0.091, 0.104, 0.120])


# Eigenvalues and eigenvectors of PCA, Tholen 1984 Table IV
EIGENVALUES = np.array([4.737, 1.879, 0.180, 0.118, 0.045, 0.032, 0.010])
EIGENVECTORS = np.array(
    [
        [0.346, 0.373, 0.415, 0.433, 0.399, 0.336, 0.330],
        [-0.463, -0.416, -0.289, 0.000, 0.320, 0.475, 0.448],
        [0.231, 0.207, 0.028, -0.622, -0.290, -0.002, 0.657],
        [-0.207, -0.103, 0.028, 0.586, -0.399, -0.460, 0.481],
        [0.442, 0.044, -0.707, 0.094, 0.398, -0.347, 0.124],
        [-0.303, -0.039, 0.398, -0.271, 0.580, -0.574, 0.100],
        [0.531, -0.795, 0.292, -0.016, -0.010, -0.022, 0.031],
    ]
)

# Table VIII in Tholen 1984
TEMPLATES = {
    "A": {
        "refl_mean": [1.015, 0.779, 0.381, 0.305, 0.240, 0.141, 0.034],
        "refl_std": [0.083, 0.058, 0.042, 0.068, 0.051, 0.073, 0.096],
        "alb_mean": 0.210,
        "alb_std": 0.099,
    },
    "B": {
        "refl_mean": [0.192, 0.098, -0.015, -0.011, -0.038, -0.062, -0.100],
        "refl_std": [0.025, 0.027, 0.017, 0.027, 0.028, 0.034, 0.055],
        "alb_mean": 0.088,
        "alb_std": 0.021,
    },
    "C": {
        "refl_mean": [0.245, 0.155, 0.024, 0.003, 0.019, 0.019, 0.028],
        "refl_std": [0.064, 0.044, 0.025, 0.025, 0.029, 0.033, 0.045],
        "alb_mean": 0.039,
        "alb_std": 0.009,
    },
    "D": {
        "refl_mean": [0.128, 0.103, 0.067, 0.153, 0.273, 0.340, 0.367],
        "refl_std": [0.052, 0.038, 0.027, 0.024, 0.031, 0.055, 0.066],
        "alb_mean": 0.030,
        "alb_std": 0.005,
    },
    "E": {
        "refl_mean": [0.117, 0.080, 0.028, 0.068, 0.105, 0.123, 0.132],
        "refl_std": [0.082, 0.051, 0.025, 0.022, 0.039, 0.042, 0.050],
        "alb_mean": 0.427,
        "alb_std": 0.065,
    },
    "F": {
        "refl_mean": [0.020, -0.014, -0.049, 0.008, -0.013, -0.032, -0.066],
        "refl_std": [0.045, 0.036, 0.016, 0.014, 0.025, 0.029, 0.050],
        "alb_mean": 0.040,
        "alb_std": 0.008,
    },
    "G": {
        "refl_mean": [0.420, 0.290, 0.069, -0.020, -0.005, -0.002, -0.003],
        "refl_std": [0.026, 0.025, 0.021, 0.030, 0.005, 0.022, 0.025],
        "alb_mean": 0.055,
        "alb_std": 0.006,
    },
    "M": {
        "refl_mean": [0.117, 0.080, 0.028, 0.068, 0.105, 0.123, 0.132],
        "refl_std": [0.082, 0.051, 0.025, 0.022, 0.039, 0.042, 0.050],
        "alb_mean": 0.117,
        "alb_std": 0.036,
    },
    "P": {
        "refl_mean": [0.117, 0.080, 0.028, 0.068, 0.105, 0.123, 0.132],
        "refl_std": [0.082, 0.051, 0.025, 0.022, 0.039, 0.042, 0.050],
        "alb_mean": 0.030,
        "alb_std": 0.006,
    },
    "Q": {
        "refl_mean": [0.746, 0.434, 0.153, 0.091, -0.042, -0.163, -0.168],
        "refl_std": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        "alb_mean": 0.210,
        "alb_std": np.nan,
    },
    "R": {
        "refl_mean": [0.765, 0.567, 0.254, 0.190, -0.042, -0.124, -0.008],
        "refl_std": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        "alb_mean": 0.249,
        "alb_std": np.nan,
    },
    "S": {
        "refl_mean": [0.552, 0.419, 0.188, 0.169, 0.159, 0.138, 0.160],
        "refl_std": [0.105, 0.075, 0.041, 0.034, 0.050, 0.057, 0.075],
        "alb_mean": 0.154,
        "alb_std": 0.035,
    },
    "T": {
        "refl_mean": [0.316, 0.239, 0.105, 0.116, 0.215, 0.226, 0.223],
        "refl_std": [0.027, 0.022, 0.014, 0.023, 0.029, 0.043, 0.091],
        "alb_mean": 0.042,
        "alb_std": np.nan,
    },
    "V": {
        "refl_mean": [0.652, 0.428, 0.142, 0.085, -0.168, -0.268, 0.004],
        "refl_std": [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
        "alb_mean": 0.249,
        "alb_std": np.nan,
    },
    "X": {
        "refl_mean": [0.117, 0.080, 0.028, 0.068, 0.105, 0.123, 0.132],
        "refl_std": [0.082, 0.051, 0.025, 0.022, 0.039, 0.042, 0.050],
        "alb_mean": np.nan,
        "alb_std": np.nan,
    },
}
