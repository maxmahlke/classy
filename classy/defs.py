import numpy as np

# ------
# Input Data

# Spectra

# Wavelength Grid
LIMIT_VIS = 0.45  # in mu
LIMIT_NIR = 2.45  # in mu
STEP_NIR = 0.05  # in mu
STEP_VIS = 0.025  # in mu

VIS_NIR_TRANSITION = 1.05  # in mu

WAVE_GRID_VIS = np.arange(LIMIT_VIS, VIS_NIR_TRANSITION + STEP_VIS, STEP_VIS)
WAVE_GRID_NIR = np.arange(VIS_NIR_TRANSITION + STEP_NIR, LIMIT_NIR + STEP_NIR, STEP_NIR)
WAVE_GRID = np.round(np.concatenate((WAVE_GRID_VIS, WAVE_GRID_NIR)), 3)
WAVE_GRID_STR = [str(w) for w in WAVE_GRID]

# Wavelength regions with atmospheric absorption
TELLURIC_TROUBLE = [
    (0.93, 0.97),
    (1.11, 1.16),
    (1.30, 1.49),
    (1.74, 1.98),
    (2.45, 2.60),
]

# Parameters for feature-fits
FEATURE = {
    # feature: center [mean, std], lower and upper fitting window limits
    "e": {
        "candidates": ["P", "M", "E", "X"],
        "center": [0.49725, 0.0055],
        "lower": 0.45,
        "upper": 0.539,
    },
    "h": {
        "candidates": ["B", "C", "P", "X"],
        "center": [0.69335, 0.011],
        "lower": 0.549,
        "upper": 0.834,
    },
    "k": {
        "candidates": ["P", "M", "E", "X"],
        "center": [0.90596, 0.017],
        "lower": 0.758,
        "upper": 1.06,
    },
}

# All data
COLUMNS = {
    "albedo": "pV",
    "smoothing": ["smooth_degree", "smooth_window"],
    "spectra": list(WAVE_GRID_STR),
}
COLUMNS["all"] = COLUMNS["spectra"] + [COLUMNS["albedo"]]
COLUMNS["all_str"] = [str(c) for c in COLUMNS["spectra"]] + [COLUMNS["albedo"]]

# ------
# Model Parameters
MODEL_PARAMETERS = {
    "k": 50,
    "d": 4,
    "random_state": 7,
    "init_params": "ppca",
    "normalize_spectra": "mixnorm",
    "max_missing_bins": 60,  # amount of maximum missing spectral bins in percent
    "k_norm": 30,
}

# ------
# Cluster
CORE_CLUSTER = {
    0: "S",
    1: "D",
    2: "B",
    3: "S",
    5: "C",
    6: "S",  # formerly Sq
    7: "V",
    9: "A",
    11: "S",
    12: "A",
    14: "S",
    15: "V",
    16: "Q",
    18: "V",
    # 19: "C",
    20: "S",
    21: "S",  # formerly Sq
    25: "C",
    26: "C",
    27: "A",
    28: "V",
    # 29: "U",
    30: "S",
    32: "V",
    33: "S",  # formerly Sa
    34: "D",
    36: "Z",
    38: "S",
    39: "S",
    40: "S",
    42: "S",
    # 44: "S",
    45: "V",
    47: "S",
    48: "Q",
    49: "A",
}
X_COMPLEX = [17, 22, 35, 37, 46]
DIFFUSE_CLUSTER = {13, 29, 41}
CONTINUUM_CLUSTER = {
    4: ["S", "L"],
    8: ["S", "D"],
    10: ["R", "S"],
    13: ["Q", "C", "O"],
    19: ["C", "P"],
    23: ["L", "M"],
    24: ["K", "M"],
    29: ["A", "B", "C", "D", "M", "P", "Q", "S", "V"],
    31: ["K", "L"],
    41: ["B", "V"],
    43: ["D", "S"],
    44: ["S", "E"],
}

# ------
# CLASSES
CLASSES = list(set(CORE_CLUSTER.values())) + ["X", "E", "P", "Ch"]
for classes in CONTINUUM_CLUSTER.values():
    CLASSES = CLASSES + classes
CLASSES = sorted(list(set(CLASSES)))
