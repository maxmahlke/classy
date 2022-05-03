__version__ = 0.2

import importlib.util
from . import (
    cli,
    classify,
    data,
    decision_tree,
    defs,
    gmm,
    logging,
    mcfa,
    mixnorm,
    plotting,
    preprocessing,
    spectra,
    tools,
)

from pathlib import Path

PATH_DATA = Path(importlib.util.find_spec("classy").origin).parent.parent / "data"
