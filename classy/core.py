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
from classy.logging import logger
from classy import mixnorm
from classy import plotting


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

        # Look up pV if it is not provided and we know the asteroid
        if self.pV is None and self.asteroid_name is not None:
            rock = rocks.Rock(self.asteroid_name)
            self.pV = rock.albedo.value
            self.pV_err = rock.albedo.error_

        # Has it been preprocessed already?
        self.preprocessed = preprocessed

        if self.preprocessed:
            self.wave_preprocessed = self.wave
            self.refl_preprocessed = self.refl
            self.pV_preprocessed = self.pV

        # Assign arbitrary arguments
        self.__dict__.update(**kwargs)

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

        if interactive:

            # Run with default parameters to initialize self.refl_smoothed
            self.smooth_window = self.smooth_window if window is not None else 99
            self.smooth_degree = self.smooth_degre if degree is not None else 3
            self.refl_smoothed = signal.savgol_filter(
                self.refl, self.smooth_window, self.smooth_degree
            )
            self._smooth_interactive()

        # self.refl_original = self.refl

        self.refl_smoothed = signal.savgol_filter(
            self.refl, self.smooth_window, self.smooth_degree
        )

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

    def normalize(self):
        """Normalize the reflectance using the mixnorm algorithm."""
        alpha = mixnorm.normalize(self)
        self.refl_preprocessed = np.log(self.refl_normalised) - alpha
        self.alpha = alpha

    def preprocess(self):
        """Preprocess spectrum for classification."""
        self.detect_features()
        self.smooth()
        self.resample()
        self.normalize()

        self.pV_preprocessed = np.log10(self.pV)

        self.preprocessed = True

    def resample(self):
        """Resample the spectrum to the classy wavelength grid."""

        # Little hack: If the first point is exactly 0.45 or the last point
        # is exactly 2.45, the spline regards it as extrapolation.
        # Move it slightly outside to get a value there
        if self.wave[0] == defs.LIMIT_VIS:
            self.wave[0] = defs.LIMIT_VIS - 0.0001
        if self.wave[-1] == defs.LIMIT_NIR:
            self.wave[-1] = defs.LIMIT_NIR + 0.0001

        if self.refl_smoothed is None:
            logger.warning(
                "Interpolating the original spectrum, consider smoothing it first."
            )

        refl_interp = interpolate.interp1d(
            self.wave, self.refl_smoothed, bounds_error=False
        )

        # Update basic properties
        self.wave_interp = defs.WAVE_GRID
        self.refl_interp = refl_interp(defs.WAVE_GRID)
        self.mask = np.array([np.isfinite(r) for r in self.refl_interp])

    def classify(self, system="Mahlke+ 2022"):

        # Find out which system
        if "mahlke" in system.lower():
            system = "Mahlke+ 2022"
        elif "demeo" in system.lower():
            system = "DeMeo+ 2009"
        elif "bus" in system.lower():
            system = "Bus and Binzel"
        elif "demeo" in system.lower():
            system = "Tholen 1984"

        if system == "Mahlke+ 2022" and not self.preprocessed:
            self.preprocess()

        # Instantiate MCFA model instance if not done yet
        model = data.load("mcfa")

        # Get only the classification columns
        data_input = np.concatenate([self.refl_preprocessed, [self.pV_preprocessed]])[
            :, np.newaxis
        ].T

        input_data = pd.DataFrame(
            {col: val for col, val in zip(defs.COLUMNS["all"], data_input[0])},
            index=[0],
        )

        # Compute responsibility matrix based on observed values only
        self.responsibility = model.predict_proba(data_input)

        # Compute latent scores
        self.data_imputed = model.impute(data_input)
        self.data_latent = model.transform(self.data_imputed)

        # Add latent scores and responsibility to input data
        for factor in range(model.n_factors):
            input_data[f"z{factor}"] = self.data_latent[:, factor]

        input_data["cluster"] = np.argmax(self.responsibility, axis=1)

        for i in range(model.n_components):
            input_data[f"cluster_{i}"] = self.responsibility[:, i]

        # Add asteroid classes based on decision tree
        self.data_classified = decision_tree.assign_classes(input_data)

        for class_ in defs.CLASSES:
            setattr(
                self,
                f"class_{class_}",
                self.data_classified[f"class_{class_}"].values[0],
            )

        # Detect features
        self.data_classified = self.add_feature_flags(self.data_classified)
        setattr(self, "class_", self.data_classified["class_"].values[0])

        # Class per asteroid
        # self.data_classified = _compute_class_per_asteroid(self.data_classified)

        # Print results
        from collections import Counter

        classes = Counter(self.data_classified.class_)
        results_str = ", ".join(
            [f"{class_}" for class_, count in classes.most_common()]
        )
        logger.info(
            f"[({self.asteroid_number}) {self.asteroid_name}] - [{self.name}]: {results_str}"
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
        return plotting._plot_spectrum(self, show)

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
    def _normalize_l2(self):
        """Normalize the reflectance using the L2 norm."""
        self.refl = preprocessing.normalize(self.refl.reshape(1, -1))[0]

        if hasattr(self, "refl_original"):
            self.refl_original = preprocessing.normalize(
                self.refl_original.reshape(1, -1)
            )[0]

    def _smooth_interactive(self):
        """Helper to smooth spectrum interactively. Call the 'smooth' function instead."""

        _, ax = self.plot()

        # Include widgets
        def update_smooth(_):
            """Read the GUI values and re-smooth the spectrum."""
            self.smooth_degree = int(degree_box.text)
            self.smooth_window = int(window_box.text)

            self.smooth(interactive=False)
            ax.get_lines()[1].set_ydata(self.refl_smoothed)
            plt.draw()

        ax_win = plt.axes([0.25, 0.90, 0.05, 0.03])
        window_box = TextBox(ax_win, "Smoothing Window", initial=self.smooth_window)

        ax_deg = plt.axes([0.45, 0.90, 0.05, 0.03])
        degree_box = TextBox(ax_deg, "Smoothing Degree", initial=self.smooth_degree)

        window_box.on_submit(lambda x: update_smooth(x))
        degree_box.on_submit(lambda x: update_smooth(x))

        plt.show()


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

        if (
            xrange[xrange_fit].min() < wave.min()
            or xrange[xrange_fit].max() > wave.max()
        ):
            logger.debug(
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
            from classy.data.SOURCES. Default is None, which returns all spectra.
        """

        if source is not None:
            if isinstance(source, str):
                source = [source]

            for s in source:
                if s not in data.SOURCES:
                    raise ValueError(
                        f"Unknown source '{s}'. Choose from {data.SOURCES}."
                    )
        else:
            source = data.SOURCES

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

    def plot(self, add_classes=False):
        plotting.plot_spectra(list(self), add_classes)

    def classify(self):
        for spec in self:
            spec.classify()

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
