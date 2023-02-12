import logging
from pathlib import Path
import sys

import numpy as np
import pandas as pd

from classy import core
from classy import defs
from classy.logging import logger
from classy import tools


class Preprocessor:
    """Preprocessor for spectra and albedo observations."""

    def __init__(self, data, verbose=False):
        """Create a preprocessing pipeline directed at a data file.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing the observations to classify and optionally metadata.
        verbose : bool
            Print logging messages. Default is False.
        """
        if not isinstance(data, pd.DataFrame):
            data = pd.read_csv(data)
        self.data = data
        self.verify_data()

        if verbose:
            log = logging.getLogger(__name__)

        # Deserialize the spectral data
        self.spectra = []

        for _, sample in self.data.iterrows():
            smooth_degree = (
                sample["smooth_degree"] if "smooth_degree" in self.columns else None
            )
            smooth_window = (
                sample["smooth_window"] if "smooth_window" in self.columns else None
            )
            spectrum = core.Spectrum(
                np.array(sorted(self.columns_numeric)),
                sample[sorted(self.columns_numeric)].array,
                smooth_degree,
                smooth_window,
            )

            self.spectra.append(spectrum)

    def verify_data(self):
        """Do sanitary check on passed user data."""

        # Ensure sane indexing
        self.data = self.data.reset_index(drop=True)

        # Are there wavelength columns?
        self.columns_numeric = tools.get_numeric_columns(self.data.columns)
        self.data = self.data.rename(
            columns={c: float(c) for c in self.columns_numeric}
        )
        self.columns_numeric = [float(c) for c in self.columns_numeric]

        if not self.columns_numeric:
            logger.error(
                "No wavelength columns were found. Ensure that the input data is in the right format, see https://classy.readthedocs.io/en/latest/tutorial.html#format-of-spectrometric-data"
            )
            sys.exit()

        self.columns = self.data.columns
        logger.debug(f"Identified numeric columns: {self.columns_numeric}")

        # Is there a pV column?
        if not defs.COLUMNS["albedo"] in self.columns:
            logger.debug(
                f"No albedo column ['{classy.defs.COLUMNS['albedo']}'] found in data. Adding an empty column."
            )
            self.data[classy.defs.COLUMNS["albedo"]] = np.nan

        # Any other columns?
        self.columns_meta = [
            column
            for column in self.columns
            if column not in self.columns_numeric
            and column
            not in [classy.defs.COLUMNS["albedo"]] + classy.defs.COLUMNS["smoothing"]
        ]
        logger.debug(f"Ignoring columns: {self.columns_meta}")

    def preprocess(self):
        """Apply entire preprocessing routine to data."""

        # Smooth, resample, normalize spectra
        for spectrum in self.spectra:
            spectrum.detect_features()
            spectrum.smooth()
            spectrum.resample()
            spectrum.normalize()

        # Log-transform albedo
        self.data["pV"] = np.log10(self.data["pV"])

        # Create preprocessed dataframe
        self.merge_results()

    def merge_results(self):
        """Merge the preprocessed spectra and albedo instances into the final dataframe."""

        self.data_preprocessed = pd.DataFrame()

        # Fill the output dataframe with the input samples as rows
        for i, sample in self.data.iterrows():

            spectrum = self.spectra[i]

            # Resampled, smoothed reflectance
            data = {w: r for w, r in zip(spectrum.wave, spectrum.refl)}

            # Albedo and met columns
            data.update(
                {
                    c: sample[c]
                    for c in [classy.defs.COLUMNS["albedo"]] + self.columns_meta
                }
            )

            # Spectral preprocessing parameters
            data.update(
                {
                    "alpha_norm": spectrum.alpha,
                    "smooth_window": spectrum.smooth_window,
                    "smooth_degree": spectrum.smooth_degree,
                }
            )

            for feature in classy.defs.FEATURE:
                if getattr(spectrum, feature).is_present:
                    data.update({feature: 1})
                else:
                    data.update({feature: 0})

            # Append to output
            self.data_preprocessed = pd.concat(
                [self.data_preprocessed, pd.DataFrame(data=data, index=[i])]
            )

    def to_file(self, path):
        """Save the preprocessed data to file.

        Parameters
        ----------
        path : str
            The path at which to save the output.
        """

        if self.data_preprocessed is None:
            raise NotPreprocessedError(
                "You have to call the Preprocessor.preprocess() function first."
            )

        path = Path(path)

        # path_output = Path(
        #     self.path_data.parent
        #     / f"{self.path_data.stem}_preprocessed{self.path_data.suffix}"
        # )
        self.data_preprocessed.to_csv(path, index=False)
        logger.info(f"Stored preprocessed data to {path.resolve()}")


class NotPreprocessedError:
    pass
