"""User-specific configuration in classy."""

from pathlib import Path

from platformdirs import user_cache_dir

PATH_CACHE = Path(user_cache_dir()) / "classy"

# Maximum missing wavelength range to extrapolate for classification
EXTRAPOLATION_LIMIT = 10  # in percent
