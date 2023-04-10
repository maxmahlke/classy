"""Implement the Spectrum class in classy."""

import numpy as np
import pandas as pd
import rocks
from scipy import interpolate, signal

import tensorflow as tf

tf.get_logger().setLevel("ERROR")

from classy import data
from classy import decision_tree
from classy import defs
from classy.log import logger
from classy import mixnorm
from classy import plotting
from classy import preprocessing
from classy import tools
from classy import taxonomies
from classy import sources


class Spectrum:
    def __init__(
        self,
        wave,
        refl,
        refl_err=None,
        flag=None,
        pV=None,
        pV_err=None,
        name=None,
        number=None,
        preprocessed=False,
        **kwargs,
    ):
        """Create a Spectrum.

        Parameters
        ----------
        wave : list of float
            The wavelength bins.
        refl : list of float
            The reflectance values.
        refl_err : list of float
            The reflectance uncertainty values. Default is None.
        flag : list of int
            List with one flag value per data point. 0 - good, 1 - mediocre, 2 - bad.
            Default is None, which assigns flag 0 to all data points.
        pV : float
            The visual albedo of the asteroid. Default is None, in which case the albedo is looked up using rocks.
        pV_err : float
            The albedo uncertainty value. Default is None.
        name : str
            The name of the asteroid the spectrum is referring to.
        number : int
            The number of the asteroid the spectrum is referring to.
        preprocessed : bool
            Whether the reflectance bins and albedo have already been preprocessed
            following Mahlke+ 2022. Default is False.

        Notes
        -----
        Arbitrary keyword arguments are assigned to attributes carrying the same names.
        """

        if flag is None:
            flag = [0] * len(wave)

        # Verify validity of observations
        wave, refl, refl_err, flag = _basic_checks(wave, refl, refl_err, flag)

        # Assign data
        self.wave = wave
        self.refl = refl
        self.refl_err = refl_err
        self.flag = flag
        self.pV = pV
        self.pV_err = pV_err

        # Assign metadata
        self.name = name
        self.number = number

        # Look up name, number, albedo, if not provided
        if name is None and number is not None:
            self.name, self.number = rocks.id(number)
        elif name is not None and number is None:
            self.name, self.number = rocks.id(name)

        self._refl_original = self.refl.copy()
        self._wave_original = self.wave.copy()

        # Look up pV if it is not provided and we know the asteroid
        if self.pV is None and self.name is not None:
            rock = rocks.Rock(self.name)
            self.pV = rock.albedo.value
            self.pV_err = rock.albedo.error_
        elif self.pV is None:
            self.pV = np.nan
            self.pV_err = np.nan

        # Assign arbitrary arguments
        self.__dict__.update(**kwargs)

        # Attribute to differentiate user-provided and online spectra
        self._source = "User"

    def __len__(self):
        return len(self.wave)

    def smooth(self, method="savgol", **kwargs):
        """Smooth spectrum using a Savitzky-Golay filter or univariate spline.

        Parameters
        ----------
        method : str
            The smoothing method. Choose from ['savgol', 'spline']. Default is 'savgol'.
        """

        if method == "savgol":
            self.refl = preprocessing.savitzky_golay(self.refl, **kwargs)
        elif method == "spline":
            self.refl = preprocessing.univariate_spline(self.wave, self.refl, **kwargs)
        else:
            raise ValueError(
                f"Unknown smoothing method '{method}'. Choose from ['savgol', 'spline']."
            )

    @property
    def albedo(self):
        return self.pV

    @albedo.setter
    def albedo(self, value):
        self.pV = value

    @property
    def albedo_err(self):
        return self.pV_err

    @albedo_err.setter
    def albedo_err(self, value):
        self.pV_err = value

    def truncate(self, wave_min, wave_max):
        """Truncate wavelength range to minimum and maximum value.

        Parameters
        ----------
        wave_min : float
            The lower wavelength to truncate at.
        wave_max : float
            The upper wavelength to truncate at.
        """
        self.refl = self.refl[(self.wave >= wave_min) & (self.wave <= wave_max)]
        self.wave = self.wave[(self.wave >= wave_min) & (self.wave <= wave_max)]

        if self.wave.size == 0:
            logger.error("No wavelength bins left in spectrum after truncating.")

    def normalize(self, method="wave", at=None):
        """Normalize the spectrum.

        Parameters
        ----------
        method : str
            The method to use for the normalization. Choose from ["wave", "l2", "mixnorm"].
            Default is "wave".
        at : float
            The wavelength at which to normalize. Only relevant when method == "wave".
        """
        if at is not None:
            self.refl = preprocessing._normalize_at(self.wave, self.refl, at)

            if hasattr(self, "_refl_original"):
                self._refl_original = preprocessing._normalize_at(
                    self._wave_original, self._refl_original, at
                )
            return

        if method == "l2":
            self.refl = preprocessing._normalize_l2(self.refl)

            if hasattr(self, "_refl_original"):
                self._refl_original = preprocessing._normalize_l2(self._refl_original)

        elif method == "mixnorm":
            alpha = mixnorm.normalize(self)
            self.refl = np.log(self.refl) - alpha
            self.alpha = alpha

            if hasattr(self, "_refl_original"):
                self._refl_original = np.log(self._refl_original) - alpha

    #
    # def preprocess(
    #     self,
    #     smooth_method="savgol",
    #     smooth_params=None,
    #     resample_params=None,
    #     taxonomy="mahlke",
    # ):
    #     """Preprocess a spectrum for classification in a given taxonomic system.
    #
    #     Parameters
    #     ----------
    #     smooth_method : str or None
    #         Optional. The smoothing method to apply to the spectrum. Choose
    #         from ['savgol', 'spline']. Default is 'savgol'. If set to None, no
    #         smoothing is applied.
    #     smooth_params : dict
    #         Optional. The smoothing parameters passed to the respective
    #         smoothing functions. Must be valid arguments of the
    #         ``scipy.signal.savgol_filter`` or ``scipy.interpolate.UnivariateSpline``
    #         functions depending on the chosen smoothing method.
    #     resample_params : dict
    #         Optional. The resampling parameters passed to the ``scipy.interpolate.interp1d`` function.
    #     taxonomy : str
    #         Optional. The taxonomic system to prepare the spectrum for. Choose from
    #         ['mahlke', 'demeo', 'bus', 'tholen']. Default is 'mahlke'.
    #     """
    #
    #     # ------
    #     # Smoothing is universal and the first step
    #     if smooth_method == "savgol":
    #         self.refl = preprocessing.savitzky_golay(self.refl, smooth_params)
    #         self.refl_plot = self.refl
    #     elif smooth_method == "spline":
    #         self.refl = preprocessing.univariate_spline(
    #             self.wave, self.refl, smooth_params
    #         )
    #         self.refl_plot = self.refl
    #     else:
    #         # No smoothing
    #         self.refl_plot = self.refl  # for plotting only
    #         self.refl = self.refl  # for classification only
    #
    #     # Never change the original wave and refl attributes
    #     # Only change the _pre suffixed ones
    #     self.wave_pre = self.wave
    #     self.wave_plot = self.wave
    #
    #     # ------
    #     # Remaining steps depend on the taxonomic scheme
    #     if "mahlke" in taxonomy.lower():
    #         taxonomies.mahlke.preprocess(self, resample_params)
    #
    #     elif "demeo" in taxonomy.lower():
    #         taxonomies.demeo.preprocess(self, resample_params)
    #
    #     elif "bus" in taxonomy.lower():
    #         taxonomies.bus.preprocess(self, resample_params)
    #
    #     elif "tholen" in taxonomy.lower():
    #         taxonomies.tholen.preprocess(self, resample_params)

    def classify(self, taxonomy="mahlke", preprocess_remote=False):
        """Classify a spectrum in a given taxonomic system.

        Parameters
        ----------
        taxonomy : str
            The taxonomic system to use. Choose from ['mahlke', 'demeo', 'bus', 'tholen'].
            Default is 'mahlke'.

        Notes
        -----
        The classification result is added as 'class_{taxonomy}' attribute to the
        spectrum instance. Some taxonomies add more than one result as attribute.
        Refer to the documentation for more information.
        """

        # Argument check
        if taxonomy not in taxonomies.SYSTEMS:
            raise ValueError(
                f"Unknown taxonomy '{taxonomy}'. Choose from {taxonomies.SYSTEMS}."
            )

        # Can the spectrum be classified in the requested taxonomy?
        if not self.is_classifiable(taxonomy):
            getattr(taxonomies, taxonomy).add_classification_results(self, results=None)
            return

        # Should spectra from online repositories be preprocessed?
        # if self.source in sources.SOURCES and preprocess_remote:
        #     # Get the source-specific preprocessing settings for this taxonomy
        #     for func, params in (
        #         getattr(sources, self.source.lower()).PREPROCESSING[taxonomy].items()
        #     ):
        #         getattr(self, func)(**params)

        # Store for resetting after classification
        self._wave_pre_class = self.wave.copy()
        self._refl_pre_class = self.refl.copy()

        # Preprocess and classify as defined by scheme
        getattr(taxonomies, taxonomy).preprocess(self)
        getattr(taxonomies, taxonomy).classify(self)

        # Reset wavelength and reflectance
        self.wave = self._wave_pre_class
        self.refl = self._refl_pre_class

    def is_classifiable(self, taxonomy):
        """Check if spectrum can be classified in taxonomic scheme based
        on the wavelength range.

        Parameters
        ----------
        taxonomy : str
            The taxonomic scheme to check.

        Returns
        -------
        bool
            True if the spectrum can be classified, else False.
        """
        return getattr(taxonomies, taxonomy.lower()).is_classifiable(self)

    def remove_slope(self, translate_to=None):
        """Fit a linear function to the spectrum and divide by the fit.

        Parameters
        ----------
        translate_to : float
            Translate the fitted slope to pass trough unity at given wavelength.
            Useful for DeMeo+ 2009 classification, where the slope should pass
            through (0.55, 1). Default is None.

        Note
        ----
        The fit [slope, intercept] is recorded as ``slope`` attribute.
        """
        self.refl, self.slope = preprocessing.remove_slope(
            self.wave, self.refl, translate_to
        )

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

    def add_feature_flags(self, data_classified):
        """Detect features in spectra and amend the classification."""

        for i, sample in data_classified.reset_index(drop=True).iterrows():
            for feature, props in defs.FEATURE.items():
                if sample.class_ in props["candidates"]:
                    if getattr(self, feature).is_present:
                        if feature == "h":
                            data_classified.loc[i, "class_"] = "Ch"
                            break
                        else:
                            data_classified.loc[i, "class_"] = (
                                data_classified.loc[i, "class_"] + feature
                            )
        return data_classified

    def plot(self, add_classes=False, taxonomy="mahlke"):
        plotting.plot_spectra([self], add_classes, taxonomy)

    def resample(self, grid, **kwargs):
        """Resample the spectrum to another wavelength grid.

        Parameters
        ----------
        grid : list
            The target wavelength values.

        Notes
        -----
        Any additional parameters are passed to the ``scipy.interpoalte.interp1d`` function.
        """

        self.refl = preprocessing.resample(self.wave, self.refl, grid, **kwargs)
        self.wave = grid

    def to_csv(self, path_out=None):
        """Store the classification results to file."""
        result = {}

        for attr in [
            "name",
            "number",
            "class_",
            *[f"class_{letter}" for letter in defs.CLASSES],
        ]:
            if hasattr(self, attr):
                result[attr] = getattr(self, attr)

        result = pd.DataFrame(data=result, index=[0])

        if path_out is not None:
            result.to_csv(path_out, index=False)
        else:
            logger.info("No 'path_out' provided, storing results to ./classy_spec.csv")
            result.to_csv("./classy_spec.csv", index=False)

    # ------
    # Utility functions, not to be called directly


def _basic_checks(wave, refl, unc, flag):
    """Basic quality checks for spectra."""

    # Ensure floats
    wave = np.array([float(w) for w in wave])
    refl = np.array([float(r) for r in refl])
    flag = np.array([float(f) for f in flag])

    if unc is not None:
        unc = np.array([float(u) for u in unc])

    # Equal lengths?
    assert (
        wave.shape == refl.shape
    ), f"The passed wavelength and reflectance arrays are of different shapes."

    if unc is not None:
        assert (
            refl.shape == unc.shape
        ), f"The passed reflectance and uncertainty arrays are of different shapes."

    # Any NaN values in reflectance?
    if any([np.isnan(r) for r in refl]):
        logger.debug("Found NaN values in reflectance. Removing them.")
        wave = wave[[np.isfinite(r) for r in refl]]
        flag = flag[[np.isfinite(r) for r in refl]]

        if unc is not None:
            unc = unc[[np.isfinite(r) for r in refl]]

        refl = refl[[np.isfinite(r) for r in refl]]

    # Any negative values in reflectance?
    if any([r < 0 for r in refl]):
        logger.debug("Found negative values in reflectance. Removing them.")
        wave = wave[[r > 0 for r in refl]]
        flag = flag[[r > 0 for r in refl]]

        if unc is not None:
            unc = unc[[r > 0 for r in refl]]

        refl = refl[[r > 0 for r in refl]]

    # Wavelength ordered ascending?
    if list(wave) != list(sorted(wave)):
        # logger.warning("Wavelength values are not in ascending order. Ordering them.")

        refl = np.array([r for _, r in sorted(zip(wave, refl))])
        flag = np.array([f for _, f in sorted(zip(wave, flag))])

        if unc is not None:
            unc = np.array([u for _, u in sorted(zip(wave, unc))])

        # sort wave last
        wave = np.array([w for _, w in sorted(zip(wave, wave))])
    return wave, refl, unc, flag


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
        self.upper = defs.FEATURE[name]["upper"]
        self.lower = defs.FEATURE[name]["lower"]

    def fit(self, wave, refl, skip_validation):
        """Fit the feature-region using a polynomial."""

        # X-range of the polynomial fit
        xrange = np.arange(0.45, 2.45, 0.0001)
        xrange_fit = (self.lower < xrange) & (self.upper > xrange)

        # Cut data down to region of interest
        self.refl = refl[(wave > self.lower - 0.3) & (wave < self.upper + 0.3)]
        self.wave = wave[(wave > self.lower - 0.3) & (wave < self.upper + 0.3)]

        range_fit = (self.lower < self.wave) & (self.upper > self.wave)

        # if (
        #     xrange[xrange_fit].min() < wave.min()
        #     or xrange[xrange_fit].max() > wave.max()
        #     or len(xrange[xrange_fit]) < 5
        # ):
        if len(self.wave[range_fit]) < 4:  # we need at least 4 data points
            logger.debug(
                f"Passed spectrum does not cover the {self.name}-feature wavelength region."
            )
            self.is_present = False
            self.is_observed = False
            return
        else:
            self.is_observed = True

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
        band, *_ = np.polyfit(
            self.wave[range_fit], refl_no_continuum[range_fit], FIT_DEGREE, full=True
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
        mean, sigma = defs.FEATURE[self.name]["center"]
        if mean - 3 * sigma >= self.center or self.center >= mean + 3 * sigma:
            return False
        elif self.snr < 1.0:
            return False
        else:
            return True

    def remove_slope(self):
        # Fit first-order polynomial
        slope = np.polyfit(wave[range_fit], refl[range_fit], 1)

        # Turn into callable polynomial function
        return np.poly1d(slope)


class Spectra(list):
    """List of several spectra of individual asteroid."""

    def __init__(self, id_, source=None):
        """Create a list of spectra of an asteroid from online repositories.

        Parameters
        ----------
        id_ : str, int
            The name, number, or designation of the asteroid.
        source : str, list of string
            Only return spectrum from specified sources. Choose one or more
            from classy.sources.SOURCES. Default is None, which returns all spectra.
        """

        if source is not None:
            if isinstance(source, str):
                source = [source]

            for s in source:
                if s not in sources.SOURCES:
                    raise ValueError(
                        f"Unknown source '{s}'. Choose from {sources.SOURCES}."
                    )
        else:
            source = sources.SOURCES

        # Need this check for __add__
        if not isinstance(id_, list):
            id_ = [id_]

        spectra = []

        for i in id_:
            if isinstance(i, Spectrum):
                spectra.append(i)
                continue

            name, number = rocks.id(id_)

            if name is None:
                raise ValueError(
                    f"Could not resolve '{id_}'. A recognisable name, number, or designation is required."
                )
            spectra += data.load_spectra(name, source=source)
        return super().__init__(spectra)

    # def __setitem__(self, index, item):
    #     super().__setitem__(index, str(item))
    #
    # def insert(self, index, item):
    #     super().insert(index, str(item))
    #
    # def append(self, item):
    #     super().append(str(item))
    #
    # def extend(self, other):
    #     if isinstance(other, type(self)):
    #         super().extend(other)
    #     else:
    #         super().extend(str(item) for item in other)
    #
    def __add__(self, rhs):
        if isinstance(rhs, Spectrum):
            rhs = [rhs]
        if not isinstance(rhs, list):
            raise TypeError(
                "Expected a list of classy.Spectrum or a single classy.Spectrum."
            )
        if not all(isinstance(entry, Spectrum) for entry in rhs):
            raise ValueError(
                "Can only add a list of classy.Spectrum instances or a classy.Spectra instance to another classy.Spectra instance."
            )
        return Spectra([*self, *rhs])

    def plot(self, add_classes=False, taxonomy="mahlke"):
        plotting.plot_spectra(list(self), add_classes, taxonomy)

    def classify(self, taxonomy="mahlke"):
        for spec in self:
            spec.classify(taxonomy=taxonomy)

    def to_csv(self, path_out=None):
        results = {}

        for attr in [
            "name",
            "number",
            "class_",
            *[f"class_{letter}" for letter in defs.CLASSES],
        ]:
            column = []

            for spec in self:
                if hasattr(spec, attr):
                    column.append(getattr(spec, attr))

            results[attr] = column

        df = pd.DataFrame(data=results, index=[i for i, _ in enumerate(self)])

        if path_out is not None:
            df.to_csv(path_out, index=False)
        else:
            logger.info(
                "No 'path_out' provided, storing results to ./classy_spectra.csv"
            )
            df.to_csv("./classy_spectra.csv", index=False)
