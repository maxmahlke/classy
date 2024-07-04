"""Taxonomic classification of asteroid reflectance spectra."""

import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from .utils.logging import set_log_level  # noqa
from .core import Spectrum  # noqa
from .core import Spectra  # noqa

# Welcome to classy
__version__ = "0.8.6"
