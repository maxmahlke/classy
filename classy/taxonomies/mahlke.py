import numpy as np
import pandas as pd

from classy import data
from classy import defs
from classy import decision_tree
from classy.log import logger


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
    if any(WAVE.min() <= w <= WAVE.max() for w in spec.wave) or not np.isnan(spec.pV):
        return True

    logger.warning(
        f"[{spec.source + '/' if hasattr(spec, 'source') else ''}{spec.name}]: Insufficient wavelength range for Mahlke taxonomy ({spec.wave.min()} - {spec.wave.max()}) and no visual albedo."
    )
    return False


def preprocess(spec):
    spec.detect_features()
    spec.resample(WAVE, fill_value=np.nan, bounds_error=False)
    spec.normalize(method="mixnorm")

    spec.pV = np.log10(spec.pV)


def classify(spec):
    # Instantiate MCFA model instance if not done yet
    model = data.load("mcfa")

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
    spec.data_classified = spec.add_feature_flags(spec.data_classified)
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

    for class_ in defs.CLASSES:
        results[f"class_{class_}"] = spec.data_classified[f"class_{class_}"].values[0]

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
