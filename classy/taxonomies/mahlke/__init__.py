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

# CLASSES = ["B", "C", "Ch", "D", "Z", "P", "Pk", "Pe", "Pek"
# "M", "Mk", "Me", "Mek", "E", "Ek", "Ee", "Eek",
# "X", "Xk", "Xe", "Xek", "K", "L", "O", 'Q', 'S',
# 'R', 'A', 'V']


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
    spec._wave_pre_norm = spec.wave.copy()
    spec._refl_pre_norm = spec.refl.copy()
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
    """Load the spectral templates of the DeMeo+ classes.

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
