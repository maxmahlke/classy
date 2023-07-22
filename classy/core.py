"""Implement the Spectrum class in classy."""

from functools import singledispatchmethod

import numpy as np
import pandas as pd
import rocks

from classy import cache
from classy import defs
from classy.feature import Feature
from classy.log import logger
from classy import index
from classy import mixnorm
from classy import plotting
from classy import preprocessing
from classy import taxonomies


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

        Notes
        -----
        Arbitrary keyword arguments are assigned to attributes carrying the same names.
        """

        if flag is None:
            flag = [0] * len(wave)

        # Verify validity of observations
        self.wave, self.refl, self.refl_err, self.flag = _basic_checks(
            wave, refl, refl_err, flag
        )

        # Assign data
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
        # self._source = "User"

        # Add features
        self.e = Feature("e", self)
        self.h = Feature("h", self)
        self.k = Feature("k", self)

        self.wave_original = self.wave.copy()
        self.refl_original = self.refl.copy()
        self.refl_err_original = None if self.refl_err is None else self.refl_err.copy()

    def reset_data(self):
        self.wave = self.wave_original.copy()
        self.refl = self.refl_original.copy()
        self.refl_err = (
            None if self.refl_err_original is None else self.refl_err_original.copy()
        )

    def unsmooth(self):
        self.reset_data()

    def __len__(self):
        return len(self.wave)

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
        return Spectra([self, *rhs])

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

        if method == "l2":
            self.refl = preprocessing._normalize_l2(self.refl)

        elif method == "mixnorm":
            alpha = mixnorm.normalize(self)
            self.refl = np.log(self.refl) - alpha
            self._alpha = alpha

    def compute_phase_angle(self):
        """Compute the asteroid's phase angle at the time of observation."""

        if not hasattr(self, "date_obs"):
            raise AttributeError(
                "The spectrum requires a 'date_obs' attribute to compute the phase angle."
            )
        if not hasattr(self, "name"):
            raise AttributeError(
                "The spectrum requires a 'name' attribute to compute the phase angle."
            )
        if not self.date_obs:
            logger.debug("'date_obs' is empty, cannot compute phase angle")

        ephem = cache.miriade_ephems(self.name, self.date_obs.split(","))

        if isinstance(ephem, bool):
            self.phase = np.nan
            return

        if len(ephem) == 1:
            self.phase = ephem.phase.to_list()[0]
        else:
            self.phase = ephem.phase.to_list()

    def classify(self, taxonomy="mahlke"):
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

        # Store for resetting after classification
        self._wave_pre_class = self.wave.copy()
        self._refl_pre_class = self.refl.copy()

        # Preprocess and classify as defined by scheme
        getattr(taxonomies, taxonomy).preprocess(self)
        getattr(taxonomies, taxonomy).classify(self)

        # Reset wavelength and reflectance
        self._wave_preprocessed = self.wave.copy()
        self._refl_preprocessed = self.refl.copy()
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

    def dropnan(self, include=[]):
        """Drop NaN values in reflectance, wave, and error.

        Parameters
        ----------
        include : list of str
            List of attributes which should also be masked
            using the NaN reflectance values. Attributes must be
            numpy.ndarrays.
        """

        for param in ["wave", "refl_err"] + include:
            setattr(self, param, getattr(self, param)[~np.isnan(self.refl)])

        self.refl = self.refl[~np.isnan(self.refl)]

    def detect_features(self, feature="all"):
        """Run automatic recognition of e-, h-, and/or k-feature.

        Parameters
        ----------
        feature : str
            The feature to detect. Choose from ['all', 'e', 'h', 'k']. Default is 'all'.

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

        for name in features:
            feature = Feature(name, self)

            if feature.is_observed:
                feature.compute_fit()

            setattr(self, name, feature)

    def add_feature_flags(self, data_classified):
        """Detect features in spectra and amend the classification."""

        for i, sample in data_classified.reset_index(drop=True).iterrows():
            for feature, props in defs.FEATURE.items():
                if sample.class_ in props["candidates"]:
                    if (
                        getattr(self, feature).is_observed
                        and getattr(self, feature).is_present
                    ):
                        if feature == "h":
                            data_classified.loc[i, "class_"] = "Ch"
                            break
                        else:
                            data_classified.loc[i, "class_"] = (
                                data_classified.loc[i, "class_"] + feature
                            )
        return data_classified

    def plot(self, **kwargs):
        plotting.plot_spectra([self], **kwargs)

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

    def preprocess(self):
        """Launch GUI to preprocess spectrum."""
        # TODO: The GUI should be a method of the spectrum, not of the feature
        self.h.fit_interactive()


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
    ), "The passed wavelength and reflectance arrays are of different shapes."

    if unc is not None:
        assert (
            refl.shape == unc.shape
        ), "The passed reflectance and uncertainty arrays are of different shapes."

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

    # Any negative values in wavelength?
    if any([w < 0 for w in wave]):
        logger.debug("Found negative values in wavelength. Removing them.")
        refl = refl[[w > 0 for w in wave]]
        flag = flag[[w > 0 for w in wave]]

        if unc is not None:
            unc = unc[[w > 0 for w in wave]]

        wave = wave[[w > 0 for w in wave]]

    # Any NaN values in reflectance?
    if any([np.isnan(w) for w in wave]):
        logger.debug("Found NaN values in wavelength. Removing them.")
        refl = refl[[np.isfinite(w) for w in wave]]
        flag = flag[[np.isfinite(w) for w in wave]]

        if unc is not None:
            unc = unc[[np.isfinite(w) for w in wave]]

        wave = wave[[np.isfinite(w) for w in wave]]

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


class Spectra(list):
    """List of several spectra of individual asteroid."""

    @singledispatchmethod
    def __init__(self, arg, **kwargs):
        raise TypeError(
            f"Unsupported argument type '{type(arg)}'. Expected int, float, str, list, pd.Series, or pd.DataFrame."
        )

    @__init__.register(int)
    @__init__.register(str)
    @__init__.register(float)
    def _id(self, id_, **kwargs):
        """Instantiate Spectra from asteroid identifier. Select subsample of spectra using index keys."""
        name, number = rocks.id(id_)

        if name is None:
            raise ValueError(
                f"Could not resolve '{id_}'. A recognisable name, number, or designation is required."
            )

        # Look up asteroid in index
        idx = index.load()

        if idx.empty:
            return None

        spectra = idx[idx["name"] == name]

        # Further subselection based on user arguments
        for criterion, value in kwargs.items():
            if criterion not in spectra:
                raise AttributeError("Unknown selection parameter")

            if value is None:
                continue

            if not isinstance(value, (list, tuple)):
                value = [value]

            spectra = spectra[spectra[criterion].isin(value)]

        if spectra.empty:
            name, number = rocks.id(name)
            if "source" in kwargs:
                if not isinstance(kwargs["source"], list):
                    kwargs["source"] = [kwargs["source"]]
                logger.warning(
                    f"Did not find a spectrum of ({number}) {name} in {', '.join(kwargs['source'])} "
                )
            return None

        spectra = cache.load_spectra(spectra)

        for spec in spectra:
            self.append(spec)

    @__init__.register
    def _list(self, spectra: list):
        """Instantiate Spectra by passing a list of Spectrum instances."""
        # Need this check for __add__
        if not isinstance(spectra, list):
            spectra = [spectra]

        for spec in spectra:
            if isinstance(spec, Spectrum):
                self.append(spec)
            else:
                raise TypeError(f"Expected classy.Spectrum, got '{type(spec)}'.")

    @__init__.register(pd.DataFrame)
    @__init__.register(pd.Series)
    def _df(self, idx):
        """Instantiate Spectra using entries from the classy spectra index."""
        if isinstance(idx, pd.Series):
            idx = pd.DataFrame(idx).transpose()

        for _, entry in idx.iterrows():
            spec = Spectra(
                entry["name"],
                source=entry["source"],
                shortbib=entry["shortbib"],
                filename=entry["filename"],
            )[0]
            self.append(spec)

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

    def plot(self, **kwargs):
        plotting.plot_spectra(list(self), **kwargs)

    def classify(self, taxonomy="mahlke"):
        for spec in self:
            spec.classify(taxonomy=taxonomy)

    def detect_features(self):
        for spec in self:
            spec.detect_features()

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
