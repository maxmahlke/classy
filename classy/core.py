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
        asteroid_name=None,
        asteroid_number=None,
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
            A unique identifier for this spectrum.
        asteroid_name : str
            The name of the asteroid the spectrum is referring to.
        asteroid_number : int
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
        self.asteroid_name = asteroid_name
        self.asteroid_number = asteroid_number

        # Look up name, number, albedo, if not provided
        if (asteroid_name is None and asteroid_number is not None) or (
            asteroid_name is not None and asteroid_number is None
        ):
            self.asteroid_name, self.asteroid_number = rocks.id(asteroid_number)

        # ------
        # Classification Results
        self.class_tholen = ""
        self.scores_tholen = []

        self.class_demeo = ""
        self.scores_demeo = []

        self.class_mahlke = ""
        self.scores_mahlke = []

        # Look up pV if it is not provided and we know the asteroid
        if self.pV is None and self.asteroid_name is not None:
            rock = rocks.Rock(self.asteroid_name)
            self.pV = rock.albedo.value
            self.pV_err = rock.albedo.error_
        elif self.pV is None:
            self.pV = np.nan
            self.pV_err = np.nan

        # Assign arbitrary arguments
        self.__dict__.update(**kwargs)

        # Attribute to differentiate user-provided and online spectra
        self._source = "user"

    def __len__(self):
        return len(self.wave)

    def smooth(self, degree=None, window=None, interactive=False):
        """Smooth spectrum using a Savitzky-Golay filter."""
        # from scipy.interpolate import UnivariateSpline
        #
        # transform = {0: 1, 1: 0.5, 2: 0}
        #
        # weights = [transform[f] for f in self.flag]
        #
        # if len(self) > 40:
        #     s = 0.2
        # else:
        #     s = 0.2
        #
        # spline = UnivariateSpline(x=self.wave, y=self.refl, w=weights, k=5, s=s)
        # self.refl_smoothed = spline(self.wave)

        if degree is None:
            degree = 3
        if window is None:
            window = int(len(self) // 5)

            if window % 2 == 0:
                window += 1
            window = window if window > 5 else 5

        if not interactive and degree is None and window is None:
            logger.warning(
                "Smoothing is set to non-interactive but no smoothing parameters are set. Running smoothing interactively."
            )
            interactive = True
        else:
            self.smooth_degree = degree
            self.smooth_window = window

        # user might have set refl values to nan
        self.wave_smoothed = self.wave[~np.isnan(self.refl)]
        self.refl_smoothed = self.refl[~np.isnan(self.refl)]

        if interactive:
            # Run with default parameters to initialize self.refl_smoothed
            self.smooth_window = self.smooth_window if window is not None else 99
            self.smooth_degree = self.smooth_degre if degree is not None else 3
            self.refl_smoothed = signal.savgol_filter(
                self.refl_smoothed, self.smooth_window, self.smooth_degree
            )
            self._smooth_interactive()

        if True:
            self.refl_smoothed = signal.savgol_filter(
                self.refl_smoothed, self.smooth_window, self.smooth_degree
            )
        # else:
        #     weights = [
        #         1 / err**2 if not np.isnan(self.refl[i]) else 0
        #         for i, err in enumerate(self.refl_err)
        #     ]
        #     print(self.source)
        #     print(weights)
        #     self.refl_smoothed[
        #         np.isnan(self.refl_smoothed)
        #     ] = 0  # temporarily replace, they are 0 weighed anyway
        #     spline = interpolate.UnivariateSpline(
        #         self.wave_smoothed, self.refl_smoothed, w=weights
        #     )
        #     self.refl_smoothed = spline(self.wave_smoothed)

    @property
    def albedo(self):
        return self.pV

    @property.setter
    def albedo(self, value):
        self.pV = value

    @property
    def albedo_err(self):
        return self.pV_err

    @property.setter
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

    def normalize(self, method="l2", at=None):
        """Normalize the spectrum.

        Parameters
        ----------
        method : str
            The method to use for the normalization. Choose from ["l2", "mixnorm"].
            Default is "l2" unless "at" is not None.
        at : float
            The wavelength at which to normalize. If not None, the spectrum is
            normalized to unity at the wavelength which is closest to the pass
            value.
        """
        if at is not None:
            self.refl_pre = preprocessing._normalize_at(
                self.wave_pre, self.refl_pre, at
            )
            return

        if method == "l2":
            self.refl_pre = preprocessing._normalize_l2(self.refl_pre)

        elif method == "mixnorm":
            alpha = mixnorm.normalize(self)
            self.refl_pre = np.log(self.refl_pre) - alpha
            self.alpha = alpha

    def preprocess(
        self,
        smooth_method="savgol",
        smooth_params=None,
        resample_params=None,
        taxonomy="mahlke",
    ):
        """Preprocess a spectrum for classification in a given taxonomic system.

        Parameters
        ----------
        smooth_method : str or None
            Optional. The smoothing method to apply to the spectrum. Choose
            from ['savgol', 'spline']. Default is 'savgol'. If set to None, no
            smoothing is applied.
        smooth_params : dict
            Optional. The smoothing parameters passed to the respective
            smoothing functions. Must be valid arguments of the
            ``scipy.signal.savgol_filter`` or ``scipy.interpolate.UnivariateSpline``
            functions depending on the chosen smoothing method.
        resample_params : dict
            Optional. The resampling parameters passed to the ``scipy.interpolate.interp1d`` function.
        taxonomy : str
            Optional. The taxonomic system to prepare the spectrum for. Choose from
            ['mahlke', 'demeo', 'bus', 'tholen']. Default is 'mahlke'.
        """

        # ------
        # Smoothing is universal and the first step
        if smooth_method == "savgol":
            self.refl_pre = preprocessing.savitzky_golay(self.refl, smooth_params)
            self.refl_plot = self.refl_pre
        elif smooth_method == "spline":
            self.refl_pre = preprocessing.univariate_spline(
                self.wave, self.refl, smooth_params
            )
            self.refl_plot = self.refl_pre
        else:
            # No smoothing
            self.refl_plot = self.refl  # for plotting only
            self.refl_pre = self.refl  # for classification only

        # Never change the original wave and refl attributes
        # Only change the _pre suffixed ones
        self.wave_pre = self.wave
        self.wave_plot = self.wave

        # ------
        # Remaining steps depend on the taxonomic scheme
        if "mahlke" in taxonomy.lower():
            taxonomies.mahlke.preprocess(self, resample_params)

        elif "demeo" in taxonomy.lower():
            taxonomies.demeo.preprocess(self, resample_params)

        elif "bus" in taxonomy.lower():
            taxonomies.bus.preprocess(self, resample_params)

        elif "tholen" in taxonomy.lower():
            taxonomies.tholen.preprocess(self, resample_params)

    def classify(self, preprocessing=None, taxonomy="mahlke"):
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

        if preprocessing is None and self.source in sources.SOURCES:
            # Get the source-specific preprocessing settings for this taxonomy
            preprocessing = getattr(sources, self.source.lower()).PREPROCESS_PARAMS[
                taxonomy
            ]

        if preprocessing is not None:
            self.preprocess(**preprocessing, taxonomy=taxonomy)
            getattr(taxonomies, taxonomy).classify(self)

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
            self, wave, refl, translate_to
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

    def resample(self, grid, params=None):
        """Resample the spectrum to another wavelength grid.

        Parameters
        ----------
        grid : list
            The target wavelength values.
        params : dict
            Optional. Parameters passed to the ``scipy.interpoalte.interp`` function.
        """

        if params is None:
            params = {}

        self.refl_pre = preprocessing.resample(
            self.wave_pre, self.refl_pre, grid, params
        )
        self.wave_pre = grid

        self.wave_plot = grid
        self.refl_plot = self.refl_pre

    def to_csv(self, path_out=None):
        """Store the classification results to file."""
        result = {}

        for attr in [
            "asteroid_name",
            "asteroid_number",
            "name",
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
        if not isinstance(rhs, list):
            raise TypeError("Expected a list of classy.Spectrum instances.")
        if not all(isinstance(entry, Spectrum) for entry in rhs):
            raise ValueError(
                "Can only add a list of classy.Spectrum instances or a classy.Spectra instance to another classy.Spectra instance."
            )
        return Spectra([*self, *rhs])

    def plot(self, add_classes=False, taxonomy="mahlke"):
        plotting.plot_spectra(list(self), add_classes, taxonomy)

    # def preprocess(
    #     self,
    #     smooth_method="savgol",
    #     smooth_params=None,
    #     resample_params=None,
    #     taxonomy="mahlke",
    # ):
    #     for spec in self:
    #
    #         if spec.source in sources.SOURCES:
    #             # Get the source-specific preprocessing settings for this taxonomy
    #             preprocess_params = getattr(
    #                 sources, spec.source.lower()
    #             ).PREPROCESS_PARAMS[taxonomy]
    #
    #         spec.preprocess(**preprocess_params, taxonomy=taxonomy)

    def classify(self, taxonomy="mahlke"):
        for spec in self:
            if spec.source in sources.SOURCES:
                # Get the source-specific preprocessing settings for this taxonomy
                preprocess_params = getattr(
                    sources, spec.source.lower()
                ).PREPROCESS_PARAMS[taxonomy]

            spec.classify(preprocessing=preprocess_params, taxonomy=taxonomy)

    def to_csv(self, path_out=None):
        results = {}

        for attr in [
            "asteroid_name",
            "asteroid_number",
            "name",
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
