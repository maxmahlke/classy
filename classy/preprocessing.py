from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import interpolate, signal
import sklearn

from classy import config
from classy import core
from classy import defs
from classy.log import logger
from classy import tools


# ------
# Smoothing
def savitzky_golay(refl, **kwargs):
    """Apply Savitzky-Golay filter to an array of values.

    Parameters
    ----------
    refl : np.ndarray
        Array of reflectance values.

    Returns
    -------
    np.ndarray
        The smoothened reflectance values.

    Notes
    -----
    This function uses the ``scipy.signal.savgol_filter`` function. Any keyword
    arguments are passed to this function and must be valid argument names of
    the ``savgol_filter`` function.

    The two main parameters are the filters ``window_length`` and the
    ``polyorder``. These are set to a fifth of the number of reflectance values
    and to 3 respectively if not present in the ``params`` dictionary.
    """

    if "window_length" not in kwargs:
        logger.debug(
            "No window_length supplied to Savitzky-Golay filter. Using a fifth of the number of values."
        )
        kwargs["window_length"] = int(len(refl) // 5)
    else:
        if not isinstance(kwargs["window_length"], int):
            logger.debug(
                "Savitzky-Golay filter window length must be integer. Converting with int()."
            )
            kwargs["window_length"] = int(kwargs["window_length"])

    if "polyorder" not in kwargs:
        logger.debug("No polyorder supplied to Savitzky-Golay filter. Using 3.")
        kwargs["polyorder"] = 3

    kwargs = {k: v for k, v in kwargs.items() if k in ['polyorder', 'window_length']}

    # There might be NaN values in the reflectance. They should be ignored.
    refl[~np.isnan(refl)] = signal.savgol_filter(refl[~np.isnan(refl)], **kwargs)
    return refl


def univariate_spline(wave, refl, **kwargs):
    """Apply a smoothing spline fit to an array of values.

    Parameters
    ----------
    wave : np.ndarray
        Array of wavelength values.
    refl : np.ndarray
        Array of reflectance values.

    Returns
    -------
    np.ndarray
        The smoothened reflectance values.

    Notes
    -----
    This function uses the ``scipy.interpolate.UniveriateSpline`` class. Any
    keyword arguments are passed to this function and must be valid argument
    names of the ``UnivariateSpline`` class.

    The two main parameters are the weights ``w`` and the degree of the fitted
    spline ``k``. These are set 1 and to 3 respectively if not present in the
    ``params`` dictionary.
    """

    if "k" not in kwargs:
        logger.debug("No polynomial order 'k' supplied to spline fit. Using 3.")
        kwargs["k"] = 3

    if "w" not in kwargs:
        logger.debug("No weights supplied to spline fit. Using 1 for all values.")
        kwargs["w"] = [1] * len(wave)

    kwargs = {k: v for k, v in kwargs.items() if k in ['w', 'k']}

    # Temporarily replace NaN by 0
    refl[np.isnan(refl)] = 0

    # Compute spline and sample wavlength
    spline = interpolate.UnivariateSpline(wave, refl, **kwargs)
    refl = spline(wave)

    # Et voila
    refl[refl == 0] = np.nan
    return refl


def resample(wave, refl, grid, **kwargs):
    """Resample a spectrum to another wavelength grid.

    Parameters
    ----------
    wave : np.ndarray
        List of wavelength values.
    refl : np.ndarray
        List of reflectance values.
    grid : list
        The target wavelength values.

    Returns
    -------
    np.ndarray
        The reflectance values sampled on the target wavelength grid.

    Notes
    -----
    Any additional parameters are passed to the ``scipy.interpoalte.interp1d`` function.
    """

    # Little hack: If the first or the last point are exactly
    # on the edges, the spline regards it as extrapolation.
    # Move it slightly outside to get a value there
    if wave[0] == grid[0]:
        wave[0] -= 0.0001
    if wave[-1] == grid[-1]:
        wave[-1] += 0.0001

    if "fill_value" in kwargs:
        if kwargs["fill_value"] == "bounds":
            kwargs["bounds_error"] = False
            kwargs["fill_value"] = (refl[0], refl[-1])
    else:
        if _within_extrapolation_limit(wave.min(), wave.max(), min(grid), max(grid)):

            kwargs["bounds_error"] = False
            kwargs["fill_value"] = (refl[0], refl[-1])

    refl_interp = interpolate.interp1d(wave, refl, **kwargs)
    return refl_interp(grid)


def _within_extrapolation_limit(wave_min, wave_max, grid_min, grid_max):
    """Compute whether a spectrum is within the user-defined extrapolation limit.

    Parameters
    ----------
    wave_min : float
        The lower wavelength limit of the spectrum.
    wave_max : float
        The upper wavelength limit of the spectrum.
    grid_min : float
        The lower wavelength limit of the new grid.
    grid_max : float
        The upper wavelength limit of the new grid.

    Returns
    -------
    bool
        True if the covered wavelength range is within the extrapolation
        limit. Else False.
    """
    delta_wave_min = max(wave_min - grid_min, 0)
    delta_wave_max = max(grid_max - wave_max, 0)

    missing_percent = delta_wave_min + delta_wave_max / (grid_max - grid_min)

    if missing_percent <= config.EXTRAPOLATION_LIMIT / 100 and missing_percent > 0:
        logger.info(
            f"Missing {missing_percent*100:.1f}% of wavelength range. Extrapolating edges with constant values."
        )
        return True
    return False


def remove_slope(wave, refl, translate_to=None):
    """Fit a linear function to the spectrum and divide by the fit.

    Parameters
    ----------
    wave : np.ndarray
        Array of wavelength values.
    refl : np.ndarray
        Array of reflectance values.
    translate_to : float
        Translate the fitted slope to pass trough unity at given wavelength.
        Useful for DeMeo09 classification, where the slope should pass through (0.55, 1).
        Default is None.

    Returns
    -------
    np.ndarray
        The slope-removed reflectance values.
    list of float
        The parameters of the fitted 1d polynomial [slope, intercept].
    """

    slope_params = np.polyfit(wave, refl, 1)

    if translate_to is not None:
        slope_params[1] -= slope_params[0] * translate_to + slope_params[1] - 1

    # Turn into callable polynomial function
    slope = np.poly1d(slope_params)

    # Remove splope
    refl /= slope(wave)
    return refl, slope_params


def _normalize_at(wave, refl, at):
    """Normalize at given wavelength."""

    # Find the closest wavelength to the provided one
    idx = tools.find_nearest(wave, at)
    wave_norm = wave[idx]

    if wave_norm != at:
        logger.warning(f"Normalizing at {wave_norm} rather than at {at}.")

    return refl / refl[idx]


def _normalize_l2(refl):
    """Normalize the reflectance using the L2 norm."""
    return sklearn.preprocessing.normalize(refl.reshape(1, -1))[0]


#
# class Preprocessor:
#     """Preprocessor for spectra and albedo observations."""
#
#     def __init__(self, data):
#         """Create a preprocessing pipeline directed at a data file.
#
#         Parameters
#         ----------
#         data : pd.DataFrame
#             DataFrame containing the observations to classify and optionally metadata.
#         """
#         if not isinstance(data, pd.DataFrame):
#             data = pd.read_csv(data)
#         self.data = data
#         self.verify_data()
#
#         # Deserialize the spectral data
#         self.spectra = []
#
#         for _, sample in self.data.iterrows():
#             smooth_degree = (
#                 sample["smooth_degree"] if "smooth_degree" in self.columns else None
#             )
#             smooth_window = (
#                 sample["smooth_window"] if "smooth_window" in self.columns else None
#             )
#             spectrum = core.Spectrum(
#                 np.array(sorted(self.columns_numeric)),
#                 sample[sorted(self.columns_numeric)].array,
#                 smooth_degree,
#                 smooth_window,
#             )
#
#             self.spectra.append(spectrum)
#
#     def verify_data(self):
#         """Do sanitary check on passed user data."""
#
#         # Ensure sane indexing
#         self.data = self.data.reset_index(drop=True)
#
#         # Are there wavelength columns?
#         self.columns_numeric = tools.get_numeric_columns(self.data.columns)
#         self.data = self.data.rename(
#             columns={c: float(c) for c in self.columns_numeric}
#         )
#         self.columns_numeric = [float(c) for c in self.columns_numeric]
#
#         if not self.columns_numeric:
#             logger.error(
#                 "No wavelength columns were found. Ensure that the input data is in the right format, see https://classy.readthedocs.io/en/latest/tutorial.html#format-of-spectrometric-data"
#             )
#             sys.exit()
#
#         self.columns = self.data.columns
#         logger.debug(f"Identified numeric columns: {self.columns_numeric}")
#
#         # Is there a pV column?
#         if not defs.COLUMNS["albedo"] in self.columns:
#             logger.debug(
#                 f"No albedo column ['{classy.defs.COLUMNS['albedo']}'] found in data. Adding an empty column."
#             )
#             self.data[classy.defs.COLUMNS["albedo"]] = np.nan
#
#         # Any other columns?
#         self.columns_meta = [
#             column
#             for column in self.columns
#             if column not in self.columns_numeric
#             and column
#             not in [classy.defs.COLUMNS["albedo"]] + classy.defs.COLUMNS["smoothing"]
#         ]
#         logger.debug(f"Ignoring columns: {self.columns_meta}")
#
#     def preprocess(self):
#         """Apply entire preprocessing routine to data."""
#
#         # Smooth, resample, normalize spectra
#         for spectrum in self.spectra:
#             spectrum.detect_features()
#             spectrum.smooth()
#             spectrum.resample()
#             spectrum.normalize()
#
#         # Log-transform albedo
#         self.data["pV"] = np.log10(self.data["pV"])
#
#         # Create preprocessed dataframe
#         self.merge_results()
#
#     def merge_results(self):
#         """Merge the preprocessed spectra and albedo instances into the final dataframe."""
#
#         self.data_preprocessed = pd.DataFrame()
#
#         # Fill the output dataframe with the input samples as rows
#         for i, sample in self.data.iterrows():
#             spectrum = self.spectra[i]
#
#             # Resampled, smoothed reflectance
#             data = {w: r for w, r in zip(spectrum.wave, spectrum.refl)}
#
#             # Albedo and met columns
#             data.update(
#                 {
#                     c: sample[c]
#                     for c in [classy.defs.COLUMNS["albedo"]] + self.columns_meta
#                 }
#             )
#
#             # Spectral preprocessing parameters
#             data.update(
#                 {
#                     "alpha_norm": spectrum.alpha,
#                     "smooth_window": spectrum.smooth_window,
#                     "smooth_degree": spectrum.smooth_degree,
#                 }
#             )
#
#             for feature in classy.defs.FEATURE:
#                 if getattr(spectrum, feature).is_present:
#                     data.update({feature: 1})
#                 else:
#                     data.update({feature: 0})
#
#             # Append to output
#             self.data_preprocessed = pd.concat(
#                 [self.data_preprocessed, pd.DataFrame(data=data, index=[i])]
#             )
#
#     def to_file(self, path):
#         """Save the preprocessed data to file.
#
#         Parameters
#         ----------
#         path : str
#             The path at which to save the output.
#         """
#
#         if self.data_preprocessed is None:
#             raise NotPreprocessedError(
#                 "You have to call the Preprocessor.preprocess() function first."
#             )
#
#         path = Path(path)
#
#         # path_output = Path(
#         #     self.path_data.parent
#         #     / f"{self.path_data.stem}_preprocessed{self.path_data.suffix}"
#         # )
#         self.data_preprocessed.to_csv(path, index=False)
#         logger.info(f"Stored preprocessed data to {path.resolve()}")
#
#
# class NotPreprocessedError:
#     pass
