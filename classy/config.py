"""User-specific configuration in classy."""

import os
from pathlib import Path

from classy.log import logger
from platformdirs import user_cache_dir


if "CLASSY_DATA_DIR" in os.environ:
    PATH_CACHE = Path(os.environ["CLASSY_DATA_DIR"]).expanduser().absolute()

    if not PATH_CACHE.is_dir():
        raise ValueError(f"Path {PATH_CACHE} does not exist.")
else:
    PATH_CACHE = Path(user_cache_dir()) / "classy"

logger.debug(f"classy data directory: {PATH_CACHE}")

# Maximum missing wavelength range to extrapolate for classification
EXTRAPOLATION_LIMIT = 10  # in percent
