"""Taxonomic classification of asteroid observations following Mahlke+ 2022."""
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from .log import set_log_level
from .core import Spectrum
from .core import Spectra

# Welcome to classy
__version__ = "0.4.1"
