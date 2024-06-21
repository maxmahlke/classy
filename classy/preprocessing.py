import numpy as np
import pandas as pd
from scipy import interpolate, signal
from scipy.spatial import ConvexHull
import sklearn

from classy import config

from classy.utils.logging import logger
from classy import utils


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

    kwargs = {k: v for k, v in kwargs.items() if k in ["polyorder", "window_length"]}

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

    kwargs = {k: v for k, v in kwargs.items() if k in ["w", "k"]}

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

    refl_interp = interpolate.interp1d(wave, refl, **kwargs)
    return refl_interp(grid)


def compute_convex_hull(spec):
    # from StackOverflow
    x = spec.wave[~np.isnan(spec.refl)]
    y = spec.refl[~np.isnan(spec.refl)]

    points = np.c_[x, y]
    augmented = np.concatenate(
        [points, [(x[0], np.min(y) - 1), (x[-1], np.min(y) - 1)]], axis=0
    )

    hull = ConvexHull(augmented, qhull_options="")
    continuum_points = points[np.sort([v for v in hull.vertices if v < len(points)])]
    continuum_function = interpolate.interp1d(
        *continuum_points.T, fill_value="extrapolate"
    )
    return continuum_function


def load_smoothing():
    """Load the feature index."""
    if not (config.PATH_DATA / "smoothing.csv").is_file():
        return pd.DataFrame()
    return pd.read_csv(
        config.PATH_DATA / "smoothing.csv",
        index_col="filename",
        dtype={
            "deg_savgol": int,
            "deg_spline": int,
            "window_savgol": int,
        },
    )


def store_smoothing(smoothing):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        smoothing["number"] = smoothing["number"].astype("Int64")
    smoothing.to_csv(
        config.PATH_DATA / "smoothing.csv", index=True, index_label="filename"
    )


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
        logger.debug(
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
    tuple of float
        The parameters of the fitted 1d polynomial (slope, intercept).
    """

    slope_params = np.polyfit(wave, refl, 1)

    if translate_to is not None:
        slope_params[1] -= slope_params[0] * translate_to + slope_params[1] - 1

    # Turn into callable polynomial function
    slope = np.poly1d(slope_params)

    # Remove splope
    refl /= slope(wave)
    return refl, tuple(slope_params)


def _normalize_at(wave, refl, at):
    """Normalize at given wavelength."""

    # Find the closest wavelength to the provided one
    idx = utils.find_nearest(wave, at)
    wave_norm = wave[idx]

    if wave_norm != at:
        logger.warning(f"Normalizing at {wave_norm} rather than at {at}.")

    return refl / refl[idx]


def _normalize_l2(refl):
    """Normalize the reflectance using the L2 norm."""
    return sklearn.preprocessing.normalize(refl.reshape(1, -1))[0]


def smooth_interactive(spec):
    """"""
    from classy import gui

    gui.smooth(spec)
