import logging

import classy
import numpy as np
import pandas as pd
from scipy import interpolate, signal


class Spectrum:
    def __init__(self, wave, refl, smooth_degree=None, smooth_window=None):
        """Create a Spectrum.

        Parameters
        ----------
        wave : np.npdarray
            The wavelength bins.
        refl : np.npdarray
            The reflectance values.
        """

        # Sanitize and verify input
        self.mask = np.array([np.isfinite(r) for r in refl])

        if any(~self.mask):
            logging.debug("Found NaN values in reflectance. Removing them")
            wave = wave[self.mask]
            refl = refl[self.mask]

        assert (
            wave.shape == refl.shape
        ), f"The passed wavelength and reflectance arrays are of different shapes."

        if smooth_window is not None:

            assert (
                smooth_window % 2 == 1
            ), f"Smoothing window has to be odd number, received {smooth_window}."

            if smooth_window >= len(refl):
                logging.debug(
                    f"smooth_window ({smooth_window}) is larger than or equal to the number of observed wavelength bins ({len(refl)}). Reducing it to {len(refl) - 1}."
                )
                smooth_window = len(refl) - 1 if len(refl) % 2 == 0 else len(refl) - 2

        # Basic properties
        if isinstance(wave, pd.Series):
            wave = wave.array.astype(float)
        if isinstance(refl, pd.Series):
            refl = refl.array.astype(float)

        self.wave = wave
        self.refl = refl

        # Smoothing properties
        self.refl_smoothed = None
        self.smooth_degree = smooth_degree
        self.smooth_window = smooth_window

    def smooth(self, interactive=False):
        """Smooth spectrum using a Savitzky-Golay filter."""

        if (
            not interactive
            and self.smooth_degree is None
            and self.smooth_window is None
        ):
            logging.debug(
                "Smoothing is set to non-interactive but no smoothing parameters are set. Running smoothing interactively."
            )
            interactive = True

        if interactive:

            # Run with default parameters to initialize self.refl_smoothed
            self.smooth_window = (
                self.smooth_window if self.smooth_window is not None else 99
            )
            self.smooth_degree = (
                self.smooth_degre if self.smooth_degree is not None else 3
            )
            self.refl_smoothed = signal.savgol_filter(
                self.refl, self.smooth_window, self.smooth_degree
            )
            self._smooth_interactive()

        self.refl_smoothed = signal.savgol_filter(
            self.refl, self.smooth_window, self.smooth_degree
        )

    def _smooth_interactive(self):
        """Helper to smooth spectrum interactively. Call the 'smooth' function instead."""
        classy.plotting._smooth_interactive(self)

    def normalize(self):
        """Normalize the reflectance using the mixnorm algorithm."""
        alpha = classy.mixnorm.normalize(self)
        self.refl = np.log(self.refl) - alpha
        self.alpha = alpha

    def resample(self):
        """Resample the spectrum to the classy wavelength grid."""

        # Little hack: If the first point is exactly 0.45 or the last point
        # is exactly 2.45, the spline regards it as extrapolation.
        # Move it slightly outside to get a value there
        if self.wave[0] == classy.defs.LIMIT_VIS:
            self.wave[0] = classy.defs.LIMIT_VIS - 0.0001
        if self.wave[-1] == classy.defs.LIMIT_NIR:
            self.wave[-1] = classy.defs.LIMIT_NIR + 0.0001

        if self.refl_smoothed is None:
            logging.warning(
                "Interpolating the original spectrum, consider smoothing it first."
            )

        refl_interp = interpolate.interp1d(
            self.wave,
            self.refl_smoothed if self.refl_smoothed is not None else self.refl,
            bounds_error=False,
        )

        # Update basic properties
        self.wave = classy.defs.WAVE_GRID
        self.refl = refl_interp(classy.defs.WAVE_GRID)
        self.mask = np.array([np.isfinite(r) for r in self.refl])

    def detect_features(self, feature="all", skip_validation=False):
        """Run automatic recognition of e-, h-, and/or k-feature.

        Parameters
        ----------
        feature : str
            The feature to detect. Choose from ['all', 'e', 'h', 'k']. Default is 'all'.
        skip_validation : bool
            Whether to skip the interactive validation of the band fit. Default is False.

        Notes
        -----
        The fitted features are added as attributes to the Spectrum instance.

        >>> spectrum.detect_features(feature='e')
        >>> type(spectrum.e)
        classy.spectra.Feature
        """

        if feature not in ["all", "e", "h", "k"]:
            raise ValueError(
                f"Passed feature is {feature}, expected one of: ['all', 'e', 'h', 'k']"
            )

        if feature == "all":
            features = ["e", "h", "k"]
        else:
            features = list(feature)

        for feature in features:

            feature_instance = Feature(name=feature)
            feature_instance.fit(self.wave, self.refl, skip_validation=skip_validation)

            setattr(self, feature, feature_instance)

    def plot(self, show=True):
        """Plot the spectrum.

        Parameters
        ----------
        show : bool
            Open the plot. Default is True.

        Returns
        -------
        matplolib.figures.Figure
        matplotlib.axes.Axis
        """
        return classy.plotting._plot_spectrum(self, show)


class Feature:
    def __init__(self, name):
        """Instantiate a Feature.

        Parameters
        ----------
        name : str
            Name of the feature, choose from ['e', 'h', 'k'].
        """

        if name not in ["e", "h", "k"]:
            raise ValueError(
                f"Passed feature name is {name}, expected one of: ['e', 'h', 'k']"
            )

        self.name = name

        # Wavelength limits for fit set heuristically from training data
        self.upper = classy.defs.FEATURE[name]["upper"]
        self.lower = classy.defs.FEATURE[name]["lower"]

    def fit(self, wave, refl, skip_validation):
        """Fit the feature-region using a polynomial."""

        # X-range of the polynomial fit
        xrange = np.arange(0.45, 2.45, 0.0001)
        xrange_fit = (self.lower < xrange) & (self.upper > xrange)

        if (
            xrange[xrange_fit].min() < wave.min()
            or xrange[xrange_fit].max() > wave.max()
        ):
            logging.debug(
                f"Passed spectrum does not cover the {self.name}-feature wavelength region."
            )
            self.is_present = False
            self.is_observed = False
            return
        else:
            self.is_observed = True

        # Cut data down to region of interest
        self.refl = refl[(wave > self.lower - 0.3) & (wave < self.upper + 0.3)]
        self.wave = wave[(wave > self.lower - 0.3) & (wave < self.upper + 0.3)]

        slope = self._fit_continuum()
        refl_no_continuum = self._remove_continuum(slope)
        band = self._fit_band(refl_no_continuum)

        self.compute_band_center_and_depth(band)
        self._compute_snr(band, refl_no_continuum)
        self.is_present = self._band_present()

        if not skip_validation:
            pass

    def _fit_continuum(self):
        # Define fit interval
        range_fit = (self.lower < self.wave) & (self.upper > self.wave)

        # Fit first-order polynomial
        slope = np.polyfit(self.wave[range_fit], self.refl[range_fit], 1)

        # Turn into callable polynomial function
        return np.poly1d(slope)

    def _remove_continuum(self, slope):
        return self.refl / slope(self.wave)

    def _fit_band(self, refl_no_continuum):

        # Define fit parameters
        FIT_DEGREE = 4

        range_fit = (self.lower < self.wave) & (self.upper > self.wave)

        # Fit polynomial order 2-4 to band center
        band = np.polyfit(
            self.wave[range_fit], refl_no_continuum[range_fit], FIT_DEGREE
        )

        # Turn into callable polynomial function
        return np.poly1d(band)

    def compute_band_center_and_depth(self, band):
        xrange = np.arange(0.45, 2.45, 0.0001)
        xrange_fit = (self.lower < xrange) & (self.upper > xrange)

        # band center = minimum of continuum-removed band
        self.center = xrange[xrange_fit][np.argmin(band(xrange[xrange_fit]))]
        self.depth = max(band(xrange[xrange_fit])) - band(self.center)  # in %

    def _compute_snr(self, band, refl_no_continuum):
        range_fit = (self.lower < self.wave) & (self.upper > self.wave)

        # Approximate noise of band
        diff = [
            band(w) - refl_no_continuum[range_fit][i]
            for i, w in enumerate(self.wave[range_fit])
        ]

        noise = np.std(diff)
        self.snr = self.depth / noise

    def _band_present(self):
        mean, sigma = classy.defs.FEATURE[self.name]["center"]
        if mean - 3 * sigma >= self.center or self.center >= mean + 3 * sigma:
            return False
        elif self.snr < 1.0:
            return False
        else:
            return True
