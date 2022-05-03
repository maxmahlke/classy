import logging
from pathlib import Path

import numpy as np
import pandas as pd

import classy


class Preprocessor:
    """Preprocessor for spectra and albedo observations."""

    def __init__(self, path_data):
        """Create a preprocessing pipeline directed at a data file.

        Parameters
        ----------
        path_data : str
            Path to data in a CSV file.
        """
        self.path_data = Path(path_data)
        self.read_and_verify_data()

        # Deserialize the spectral data
        self.spectra = []

        for _, sample in self.data.iterrows():
            smooth_degree = (
                sample["smooth_degree"] if "smooth_degree" in self.columns else None
            )
            smooth_window = (
                sample["smooth_window"] if "smooth_window" in self.columns else None
            )
            spectrum = classy.spectra.Spectrum(
                np.array(sorted(self.columns_numeric)),
                sample[sorted(self.columns_numeric)],
                smooth_degree,
                smooth_window,
            )

            self.spectra.append(spectrum)

    def read_and_verify_data(self):
        """Read in user data and do sanitary check."""

        # Read into dataframe
        self.data = pd.read_csv(self.path_data)
        self.data = self.data.reset_index(drop=True)

        # Are there wavelength columns?
        self.columns_numeric = classy.tools.get_numeric_columns(self.data.columns)
        self.data = self.data.rename(columns={str(n): n for n in self.columns_numeric})
        self.columns = self.data.columns
        logging.debug(f"Identified numeric columns: {self.columns_numeric}")

        # Is there a pV column?
        if not classy.defs.COLUMNS["albedo"] in self.columns:
            logging.debug(
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
        logging.debug(f"Ignoring columns: {self.columns_meta}")

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

    def to_file(self):
        """Save the preprocessed data to file."""

        if self.data_preprocessed is None:
            raise NotPreprocessedError(
                "You have to call the Preprocessor.preprocess() function first."
            )

        path_output = Path(
            self.path_data.parent
            / f"{self.path_data.stem}_preprocessed{self.path_data.suffix}"
        )
        self.data_preprocessed.to_csv(path_output, index=False)
        logging.info(f"Stored preprocessed data to {path_output.resolve()}")


class NotPreprocessedError:
    pass
