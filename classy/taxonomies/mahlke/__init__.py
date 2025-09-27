from functools import lru_cache

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import core
from classy import features
from classy import index
from . import defs
from classy.taxonomies.mahlke import decision_tree
from classy.utils.logging import logger
from classy import utils

CLASSES = defs.CLASSES

EIGENVECTORS = np.array(
    [
        [-2.94253796e-01, -1.72717974e-01, 4.60812896e-02, 1.45581633e-01],
        [-2.82101989e-01, -1.29026979e-01, 4.09112349e-02, 1.37979016e-01],
        [-2.72639006e-01, -8.54768008e-02, 3.39814760e-02, 1.39281422e-01],
        [-2.60965407e-01, -4.57917489e-02, 2.50705574e-02, 1.44300267e-01],
        [-2.51061350e-01, -1.32736592e-02, 1.19714951e-02, 1.45396531e-01],
        [-2.40364537e-01, 1.71811823e-02, -6.25372515e-04, 1.45703733e-01],
        [-2.30155736e-01, 4.29478325e-02, -1.10464441e-02, 1.40440941e-01],
        [-2.19574139e-01, 6.76355660e-02, -1.90589875e-02, 1.31919995e-01],
        [-2.09090978e-01, 9.08522308e-02, -2.94739325e-02, 1.26056179e-01],
        [-1.99898556e-01, 1.12637036e-01, -3.43165994e-02, 1.18166119e-01],
        [-1.92081779e-01, 1.28859594e-01, -3.94626968e-02, 1.07967339e-01],
        [-1.83689088e-01, 1.36536226e-01, -3.42059396e-02, 8.75503048e-02],
        [-1.75542712e-01, 1.28273293e-01, -3.87299284e-02, 5.50124273e-02],
        [-1.68482736e-01, 1.07447840e-01, -5.25226854e-02, 1.90249141e-02],
        [-1.60315111e-01, 6.44042864e-02, -8.06179419e-02, -3.21523547e-02],
        [-1.52558491e-01, 1.23140309e-02, -1.16694041e-01, -8.05189088e-02],
        [-1.44919872e-01, -3.96381915e-02, -1.55871466e-01, -1.25847280e-01],
        [-1.37983888e-01, -8.37181956e-02, -1.86825767e-01, -1.65532336e-01],
        [-1.32109076e-01, -1.13077678e-01, -1.99988678e-01, -1.98835239e-01],
        [-1.27270237e-01, -1.24867178e-01, -1.89398751e-01, -2.30052069e-01],
        [-1.23919047e-01, -1.18773460e-01, -1.52922139e-01, -2.54983395e-01],
        [-1.21639803e-01, -9.83037874e-02, -9.51961651e-02, -2.74740010e-01],
        [-1.20087504e-01, -6.79608211e-02, -2.44472791e-02, -2.86643535e-01],
        [-1.18327908e-01, -3.50460596e-02, 4.37661223e-02, -2.92348742e-01],
        [-1.16128907e-01, -1.56413112e-03, 1.04200236e-01, -2.89462954e-01],
        [-1.08812198e-01, 5.62353022e-02, 1.83337241e-01, -2.65137494e-01],
        [-9.90483239e-02, 9.70798433e-02, 2.15040773e-01, -2.30051324e-01],
        [-8.87202024e-02, 1.24038801e-01, 2.24825770e-01, -1.96909934e-01],
        [-7.88056925e-02, 1.43693805e-01, 2.28857353e-01, -1.66066557e-01],
        [-6.89812824e-02, 1.58936992e-01, 2.26510644e-01, -1.32978529e-01],
        [-5.87986074e-02, 1.70213014e-01, 2.14477882e-01, -9.69715193e-02],
        [-4.92023043e-02, 1.75418079e-01, 1.95097953e-01, -6.40751570e-02],
        [-3.84852253e-02, 1.74161658e-01, 1.65015697e-01, -3.03241443e-02],
        [-2.80703902e-02, 1.63687497e-01, 1.27703547e-01, -1.62461202e-03],
        [-1.86525676e-02, 1.43012524e-01, 8.52469057e-02, 1.87526140e-02],
        [-1.07859354e-02, 1.14306189e-01, 4.23326567e-02, 3.00338268e-02],
        [-4.02978342e-03, 8.09341222e-02, 3.04706628e-03, 3.31809595e-02],
        [1.85558351e-03, 4.55375053e-02, -2.95297820e-02, 3.10062394e-02],
        [6.75633410e-03, 1.14726815e-02, -5.76014593e-02, 2.56941132e-02],
        [1.08430404e-02, -1.95228811e-02, -8.05793256e-02, 2.02317499e-02],
        [1.40968887e-02, -4.43287604e-02, -9.78179425e-02, 1.48822274e-02],
        [1.66285876e-02, -6.10358976e-02, -1.03222638e-01, 9.84232500e-03],
        [1.88276786e-02, -7.12607950e-02, -9.58307311e-02, 6.07825816e-03],
        [2.07591485e-02, -7.40536228e-02, -8.09064955e-02, 4.76589706e-03],
        [2.22408324e-02, -6.93102404e-02, -5.87802343e-02, 7.58864405e-03],
        [2.35186908e-02, -5.76220043e-02, -2.80758534e-02, 1.40111903e-02],
        [2.45466717e-02, -4.15597856e-02, 9.26349312e-03, 2.30773259e-02],
        [2.52232160e-02, -2.51844414e-02, 4.74623889e-02, 3.31721604e-02],
        [2.57115494e-02, -8.74866173e-03, 8.56915861e-02, 4.28767055e-02],
        [2.58838199e-02, 6.15314674e-03, 1.22105278e-01, 5.20341508e-02],
        [2.64060386e-02, 1.84116811e-02, 1.53669596e-01, 6.26357272e-02],
        [2.69928761e-02, 2.85878982e-02, 1.82645902e-01, 7.43361488e-02],
        [2.74993274e-02, 3.77255678e-02, 2.06815600e-01, 8.36384222e-02],
        [6.94022626e-02, 7.20640838e-01, -4.87631083e-01, -5.49791902e-02],
    ]
)


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

    # We need at least one observed data point
    if any(min(WAVE) <= w <= max(WAVE) for w in spec.wave) or not np.isnan(
        spec.target.albedo.value
    ):
        return True

    logger.warning(
        f"[{spec.name}]: Insufficient wavelength range for Mahlke taxonomy and no visual albedo."
    )
    return False


def preprocess(spec):
    # spec._wave_pre_norm = spec.wave.copy()  # Doesn't seem like these two are requried anymore
    # spec._refl_pre_norm = spec.refl.copy()
    spec.resample(WAVE, fill_value=np.nan, bounds_error=False)
    spec.normalize(method="mixnorm")

    if hasattr(spec, "pV"):
        spec.pV = np.log10(spec.pV)
    elif hasattr(spec, "target") and isinstance(spec.target, rocks.Rock):
        spec.pV = np.log10(spec.target.albedo.value)
    else:
        spec.pV = np.nan


def classify(spec):
    # Instantiate MCFA model instance if not done yet
    model = index.data.load("mcfa")

    # Get only the classification columns
    data_input = np.concatenate([spec.refl, [spec.pV]])[:, np.newaxis].T

    input_data = pd.DataFrame(
        {col: val for col, val in zip(defs.COLUMNS["all"], data_input[0])},
        index=[0],
    )

    # Compute responsibility matrix based on observed values only
    spec.responsibility = model.predict_proba(data_input)

    # Compute latent scores
    spec.data_imputed = model.impute(data_input)
    spec.data_latent = model.transform(spec.data_imputed)

    # Add latent scores and responsibility to input data
    for factor in range(model.n_factors):
        input_data[f"z{factor}"] = spec.data_latent[:, factor]

    input_data["cluster"] = np.argmax(spec.responsibility, axis=1)

    for i in range(model.n_components):
        input_data[f"cluster_{i}"] = spec.responsibility[:, i]

    # Add asteroid classes based on decision tree
    spec.data_classified = decision_tree.assign_classes(input_data)

    # Detect features
    spec.data_classified = add_feature_flags(spec, spec.data_classified)
    setattr(spec, "class_", spec.data_classified["class_"].values[0])

    for class_ in defs.CLASSES:
        setattr(
            spec, f"class_{class_}", spec.data_classified[f"class_{class_}"].values[0]
        )

    if spec.h.is_present:
        spec.class_Ch = spec.class_C + spec.class_B + spec.class_P
        spec.class_C = 0
        spec.class_B = 0
        spec.class_P = 0

    # Class per asteroid
    probs = [getattr(spec, f"class_{class_}") for class_ in defs.CLASSES]
    class_ = [
        class_
        for class_ in defs.CLASSES
        if getattr(spec, f"class_{class_}") == max(probs)
    ][0]
    results = {"class_mahlke": class_, "class_": class_}
    results["prob"] = max(probs)
    results["scores"] = spec.data_latent[0]
    results["scores_mahlke"] = spec.data_latent[0]

    for class_ in defs.CLASSES:
        results[f"class_{class_}"] = getattr(spec, f"class_{class_}")

    add_classification_results(spec, results=results)

    # Print results
    # Undo this trafo
    spec.pV = np.power(10, spec.pV)


def add_classification_results(spec, results=None):
    if results is None:
        spec.class_ = ""
        spec.class_mahlke = ""
        spec.prob = np.nan

        for class_ in defs.CLASSES:
            setattr(spec, f"class_{class_}", np.nan)
        return

    for key, val in results.items():
        setattr(spec, key, val)


@lru_cache(maxsize=None)
def load_templates():
    """Load the spectral templates of the Mahlke+ classes.

    Returns
    -------
    dict
        Dictionary with classes (str) as key and templates as values (classy.Spectrum).
    """

    PATH_DATA = config.PATH_DATA / "mahlke2022/templates.csv"

    if not PATH_DATA.is_file():
        utils.download.from_github(host="mahlke2022", which="templates", path=PATH_DATA)

    data = pd.read_csv(PATH_DATA)

    templates = {}

    for class_ in CLASSES:
        refl = data[class_].values[:-1]
        pV = data[class_].values[-1]
        refl_err = data[f"{class_}_upper"].values[:-1]  # - refl
        pV_err = data[f"{class_}_upper"].values[-1]  # - pV
        template = core.Spectrum(
            wave=WAVE,
            refl=refl,
            refl_err=refl_err,
            pV=pV,
            pV_err=pV_err,
            class_=class_,
            source="Mahlke+ 2022",
        )
        templates[class_] = template
    return templates


def add_feature_flags(spec, data_classified):
    """Detect features in spectra and amend the classification."""

    for i, sample in data_classified.reset_index(drop=True).iterrows():
        for feature, props in features.FEATURE.items():
            if sample.class_ in props["candidates"]:
                if (
                    getattr(spec, feature).is_covered
                    and getattr(spec, feature).is_present
                ):
                    if feature == "h":
                        data_classified.loc[i, "class_"] = "Ch"
                        break
                    else:
                        data_classified.loc[i, "class_"] = (
                            data_classified.loc[i, "class_"] + feature
                        )
    return data_classified


# Functions for classification
@lru_cache(maxsize=None)
def load_classification():
    """Load the Mahlke+ 2022 classification results like PC scores and classes from file.

    Returns
    -------
    pd.DataFrame
    """
    mahlke = index.data._load_classy()
    mahlke = mahlke.rename(columns={"z0": "PC1", "z1": "PC2", "z2": "PC3", "z3": "PC4"})
    return mahlke


def plot_pc_space(ax, x=1, y=2):
    """Plot the distribution of classified spectra and the SMASS spectra in the Mahlke PC space.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The matplotlib axis instance to plot to.
    x : int, optional
        The x-axis PC score to plot. Default is 1.
    y : int, optional
        The y-axis PC score to plot. Default is 2.

    Returns
    -------
    matplotlib.axes.Axes
        The matplotlib axis with the plotted classification results.
    """

    opts_text = dict(va="center", ha="center", clip_on=True)

    # ------
    # Add the distribution of the ECAS asteroids
    mahlke = load_classification()

    # for _, ast in mahlke.iterrows():
    # Dummy to ensure proper plot limits
    ax.scatter(mahlke[f"PC{x}"], mahlke[f"PC{y}"], c="lightgray", s=1, zorder=0)

    # Add asteroid position in PC space represented by its number
    # ax.text(ast.PC1, ast.PC2, str(ast.number), color="lightgray", **opts_text)

    # ------
    # Add the mean positions of the main classes
    for class_, pcs in mahlke.groupby("class_"):
        # Only add the core classe
        if len(class_) > 1:
            continue

        pc0 = np.mean(pcs[f"PC{x}"])
        pc1 = np.mean(pcs[f"PC{y}"])

        # Add class indicator
        ax.text(pc0, pc1, class_, size=10, color="black", **opts_text)

    # ------
    # Add classified spectra
    # for spec in spectra:
    #     if not spec.class_demeo:
    #         logger.debug(f"[{spec.name}]: Not classified in DeMeo+ 2009 system.")
    #         continue
    #
    #     ax.scatter(
    #         spec.scores_demeo[0],
    #         spec.scores_demeo[1],
    #         marker="d",
    #         c=spec._color,
    #         s=40,
    #         label=f"{spec.source + ': ' if hasattr(spec, 'source') else ''}{spec.class_demeo}",
    #         zorder=100,
    #     )

    # ------
    # Final additions et voila
    # ax.axvline(0, ls=":", c="gray")
    # ax.axhline(0, ls=":", c="gray")
    ax.legend()

    return ax


# ------
# Defintions
LIMIT_VIS = 0.45  # in mu
LIMIT_NIR = 2.45  # in mu
STEP_NIR = 0.05  # in mu
STEP_VIS = 0.025  # in mu

VIS_NIR_TRANSITION = 1.05  # in mu

WAVE_GRID_VIS = np.arange(LIMIT_VIS, VIS_NIR_TRANSITION + STEP_VIS, STEP_VIS)
WAVE_GRID_NIR = np.arange(VIS_NIR_TRANSITION + STEP_NIR, LIMIT_NIR + STEP_NIR, STEP_NIR)
WAVE = np.round(np.concatenate((WAVE_GRID_VIS, WAVE_GRID_NIR)), 3)
WAVE = list(WAVE)
