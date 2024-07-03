"""Implement the Spectrum class in classy."""

import shutil

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import sources
from classy.features import Feature
from classy import index
from classy.taxonomies.mahlke import mixnorm
from classy import plotting
from classy import preprocessing
from classy import taxonomies
from classy import utils
from classy.utils.logging import logger


class Spectrum:
    def __init__(self, wave, refl, refl_err=None, target=None, **kwargs):
        """Create a Spectrum.

        Parameters
        ----------
        wave : list of float
            The wavelength bins.
        refl : list of float
            The reflectance values.
        refl_err : list of float
            The reflectance uncertainty values. Default is None.
        target : int or str
            Identifier to resolve target of observation. Passed to rocks.identify.

        Notes
        -----
        Arbitrary keyword arguments are assigned to attributes carrying the same names.
        """

        # Verify validity of observations
        self.wave, self.refl, self.refl_err = self._basic_checks(wave, refl, refl_err)

        if target is not None:
            self.set_target(target)

        # Store original attributes for restoration reasons
        self._wave_original = self.wave.copy()
        self._refl_original = self.refl.copy()
        self._refl_err_original = (
            None if self.refl_err is None else self.refl_err.copy()
        )

        # TODO: Is this useful?
        self.is_smoothed = False

        # TODO: Is this required?
        self.phase = np.nan

        self.source = "User"

        # Assign arbitrary arguments
        self.__dict__.update(**kwargs)

    def __getattr__(self, attr):
        """Custom getattr to support dynamic instantiation of feature attributes."""
        if attr in ["e", "h", "k"]:
            setattr(self, attr, Feature(attr, self))
            return getattr(self, attr)
        raise AttributeError(f"{type(self)} has no attribute '{attr}'")

    def _basic_checks(self, wave, refl, refl_err):
        """Check the validity of passed values for spectra."""

        # Ensure floats and np.ndarrays
        wave = np.array(wave, dtype=float)
        refl = np.array(refl, dtype=float)

        if refl_err is not None:
            refl_err = np.array([float(r) for r in refl_err])

        # Equal lengths?
        assert (
            wave.shape == refl.shape
        ), f"'wave' {wave.shape} and 'refl' {refl.shape} have different shapes"

        if refl_err is not None:
            assert (
                refl.shape == refl_err.shape
            ), f"'refl' {refl.shape} and 'refl_err' {refl_err.shape} have different shapes"

        # Any negative or NaN values in wavelength?
        wave_invalid = (wave < 0) | (np.isnan(wave))
        # Any NaN values in reflectance?
        refl_invalid = np.isnan(refl)

        self.mask_valid = ~(wave_invalid | refl_invalid)

        if any(wave_invalid):
            logger.debug("Found negative or NaN values in 'wave'. Removing them.")
        if any(refl_invalid):
            logger.debug("Found NaN values in reflectance. Removing them.")
        if any(refl < 0):
            logger.debug("Found negative values in reflectance.")

        wave = wave[self.mask_valid]
        refl = refl[self.mask_valid]

        if refl_err is not None:
            refl_err = refl_err[self.mask_valid]

        # Wavelength order ascending?
        if list(wave) != list(sorted(wave)):
            logger.debug("'wave' values are not in ascending order. Ordering them.")

            refl = np.array([r for _, r in sorted(zip(wave, refl))])
            if refl_err is not None:
                refl_err = np.array([u for _, u in sorted(zip(wave, refl_err))])

            wave = np.array([w for _, w in sorted(zip(wave, wave))])

        return wave, refl, refl_err

    def reset_data(self):
        self.wave = self._wave_original.copy()
        self.refl = self._refl_original.copy()
        self.refl_err = (
            None if self._refl_err_original is None else self._refl_err_original.copy()
        )

    def unsmooth(self):
        self.reset_data()
        self.is_smoothed = False

    def copy(self):
        from copy import deepcopy

        return deepcopy(self)

    @property
    def has_smoothing_parameters(self):
        # We need at least a filename to store the parameters
        if not hasattr(self, "filename"):
            return False

        smoothing = index.load_smoothing()

        if self.filename in smoothing.index.values:
            return True
        return False

    def load_smoothing_parameters(self):
        smoothing = index.load_smoothing()
        return smoothing.loc[self.filename].to_dict()

    def smooth_interactive(self):
        preprocessing.smooth_interactive(self)
        self.is_smoothed = True

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

    def smooth(self, method="interactive", force=False, **kwargs):
        """Smooth spectrum using a Savitzky-Golay filter or univariate spline.

        Parameters
        ----------
        method : str
            The smoothing method. Choose from ['savgol', 'spline']. Default is 'savgol'.
        force : bool
            Include spectra that already have smoothing parameters in interactive
            smoothing. Default is False. Smoothing parameters are applied in both cases.
        """

        if method in ["savgol", "spline"]:
            if not kwargs:
                raise ValueError(
                    "smooth needs to be called with the smoothing parameters specified if method != 'interactive'."
                )

        if method == "savgol":
            self.refl = preprocessing.savitzky_golay(self.refl, **kwargs)
            self.is_smoothed = True
            return

        if method == "spline":
            self.refl = preprocessing.univariate_spline(self.wave, self.refl, **kwargs)
            self.is_smoothed = True
            return

        if self.has_smoothing_parameters and not force:
            params = self.load_smoothing_parameters()

            params["polyorder"] = params["deg_savgol"]
            params["window_length"] = params["window_savgol"]
            params["k"] = params["deg_spline"]

            self.truncate(params["wave_min"], params["wave_max"])

            # Should it even be smoothed?
            if params["smooth"]:
                self.smooth(**params)
            self.is_smoothed = True
            return

        self.smooth_interactive()
        self.is_smoothed = True

    def set_target(self, target):
        rock = rocks.Rock(target)
        self.target = rock

    def truncate(self, wave_min=None, wave_max=None):
        """Truncate wavelength range to minimum and maximum value.

        Parameters
        ----------
        wave_min : float
            The lower wavelength to truncate at.
        wave_max : float
            The upper wavelength to truncate at.
        """
        # TODO: Move to preprocessing module
        if wave_min is None:
            wave_min = min(self.wave)
        if wave_max is None:
            wave_max = max(self.wave)

        self.refl = self.refl[(self.wave >= wave_min) & (self.wave <= wave_max)]
        if self.refl_err is not None:
            self.refl_err = self.refl_err[
                (self.wave >= wave_min) & (self.wave <= wave_max)
            ]
        self.wave = self.wave[(self.wave >= wave_min) & (self.wave <= wave_max)]

        if self.wave.size == 0:
            logger.error("No wavelength bins left in spectrum after truncating.")

    def normalize(self, method="wave", at=None):
        """Normalize the spectrum.

        Parameters
        ----------
        method : str
            The method to use for the normalization. Choose from ["wave", "l2"].
            Default is "wave".
        at : float
            The wavelength at which to normalize. Only relevant if method == "wave".
        """
        if at is not None:
            self.refl = preprocessing._normalize_at(self.wave, self.refl, at)
            self._refl_original = preprocessing._normalize_at(
                self._wave_original, self._refl_original, at
            )

        if method == "l2":
            self.refl = preprocessing._normalize_l2(self.refl)
            self._refl_original = preprocessing._normalize_l2(self._refl_original)

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
        if not hasattr(self, "target") or not isinstance(self.target, rocks.Rock):
            raise AttributeError(
                "The spectrum requires a defined target. Use the 'set_target()' method to define it."
            )

        if not isinstance(self.date_obs, str) or not self.date_obs:
            logger.debug("'date_obs' is empty, cannot compute phase angle")
            self.phase = np.nan
            return

        ephem = index.phase.query_miriade_syncronously(
            self.target.name, self.date_obs.split(",")
        )

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
        The fit (slope, intercept) is recorded as ``slope`` attribute.
        """
        self.refl, self.slope = preprocessing.remove_slope(
            self.wave, self.refl, translate_to
        )

    def inspect_features(self, feature="all", force=False):
        """Run interactive inspection of e-, h-, and/or k-feature.

        Parameters
        ----------
        feature: str of list of str
            Features to inspect. Choose from ['all', 'e', 'h', 'k']. Default is 'all'.
        force : bool
            Include spectra that already have fit parameters in interactive fitting. Default is False.

        Notes
        -----
        The fitted features are added as attributes to the Spectrum instance.

        >>> spectrum.inspect_features(feature='e')
        >>> type(spectrum.e)
        classy.Feature
        """
        if feature == "all":
            feature = ["e", "h", "k"]

        features = list(feature) if not isinstance(feature, list) else feature

        if not all(f in ["e", "h", "k"] for f in feature):
            raise ValueError(
                f"Passed feature is {feature}, expected one of: ['all', 'e', 'h', 'k']"
            )

        for f in features:
            feature = Feature(f, self)
            setattr(self, f, feature)

            if not feature.is_covered:
                continue

            if feature.is_candidate or force:
                feature.inspect()

    @property
    def name(self):
        """A dynamic short description of the spectrum."""
        if hasattr(self, "target") and isinstance(self.target, rocks.Rock):
            name = self.target.name
        else:
            name = "Unknown"
        return f"{self.source}/{name}"

    def plot(self, **kwargs):
        return plotting.plot_spectra([self], **kwargs)

    def resample(self, wave_new, **kwargs):
        """Resample the spectrum to another wavelength grid.

        Parameters
        ----------
        wave_new : list
            The target wavelength values.

        Notes
        -----
        Any additional parameters are passed to the ``scipy.interpolate.interp1d`` function.
        """
        wave_new = sorted(wave_new)

        self.refl = preprocessing.resample(self.wave, self.refl, wave_new, **kwargs)
        self.wave = np.array(wave_new)

        if self.refl_err is not None:
            self.refl_err = None

    def compute_continuum(self):
        """Compute the convex-hull continuum of the spectrum.

        Notes
        -----
        The continuum is stored as a callable in the 'continuum' attribute.
        """
        self.continuum = preprocessing.compute_convex_hull(self)

    def export(self, path, columns=None, raw=False):
        """Export spectrum attributes to a csv file.

        Parameters
        ----------
        path : str or pathlib.Path
            The output path and filename of the exported file.
        columns : list of str
            List of attributes to export. Attributes must have the same
            shape. Default is ['wave', 'refl', 'refl_err'].
        raw : bool
            Export the raw data of the spectrum. Default is False. If raw is
            True, 'columns' is ignored.
        """
        if raw:
            if not hasattr(self, "filename"):
                raise AttributeError(
                    "The spectrum does not have a 'filename' attribute that points to the original data file."
                )

            if self.source == "Gaia" and hasattr(self, "host") and self.host == "Gaia":
                # Create virtual file and write to disk
                data = sources.gaia._load_virtual_file(
                    pd.Series(
                        {"name": self.target.name, "number": self.target.number},
                        name=self.filename,
                    )
                )
                data.to_csv(path, index=False)
                return

            shutil.copy(config.PATH_DATA / self.filename, path)
            return

        if columns is None:
            columns = ["wave", "refl", "refl_err"]

        data = pd.DataFrame(
            data={col: getattr(self, col) for col in columns}, index=range(len(self))
        )
        data.to_csv(path, index=False)


class Spectra(list):
    """List of several spectra of individual asteroid."""

    def __init__(self, id=None, skip_target=False, **kwargs):
        """Select spectra from classy index using matching criteria.

        Parameters
        ----------
        id : int, str, or list
            One or many asteroid identifiers. Optional, default is None,
            in which case no selection based on target identity is done.
        """

        # Check if argument is list of Spectrum instances
        if isinstance(id, list) and all(isinstance(entry, Spectrum) for entry in id):
            for spec in id:
                self.append(spec)
            return

        # Is it a subset of the classy index?
        if isinstance(id, pd.DataFrame):
            spectra = id
        else:
            spectra = index.query(id, **kwargs)

        spectra = index.data.load_spectra(spectra, skip_target)

        for spec in spectra:
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
        return plotting.plot_spectra(list(self), **kwargs)

    def classify(self, taxonomy="mahlke"):
        for spec in self:
            spec.classify(taxonomy=taxonomy)

    def smooth(self, method="interactive", force=False, progress=True, **kwargs):
        """Smooth spectrum using a Savitzky-Golay filter or univariate spline.

        Parameters
        ----------
        method : str
            The smoothing method. Choose from ['savgol', 'spline']. Default is 'savgol'.
        force : bool
            Include spectra that already have smoothing parameters in interactive
            smoothing. Default is False. Smoothing parameters are applied in both cases.
        progress : bool
            Show progress bar. Default is True.
        """

        if progress:
            with utils.progress.mofn as mofn:
                task = mofn.add_task("Smoothing..", total=len(self))
                for spec in self:
                    spec.smooth(method, force, **kwargs)
                    mofn.update(task, advance=1)
        else:
            for spec in self:
                spec.smooth(method, force, **kwargs)

    def inspect_features(self, feature="all", force=False, progress=True):
        """Smooth spectrum using a Savitzky-Golay filter or univariate spline.

        Parameters
        ----------
        method : str
            The smoothing method. Choose from ['savgol', 'spline']. Default is 'savgol'.
        feature: str of list of str
            Features to inspect. Choose from ['all', 'e', 'h', 'k']. Default is 'all'.
        force : bool
            Include spectra that already have fit parameters in interactive fitting. Default is False.
        progress : bool
            Show progress bar. Default is True.
        """

        if progress:
            with utils.progress.mofn as mofn:
                task = mofn.add_task("Inspecting Features..", total=len(self))
                for spec in self:
                    if spec.has_smoothing_parameters:
                        spec.smooth()
                    spec.inspect_features(feature, force)
                    mofn.update(task, advance=1)
        else:
            for spec in self:
                if spec.has_smoothing_parameters:
                    spec.smooth()
                spec.inspect_features(feature, force)

    def export(self, path=None, columns=None):
        # TODO: Update doc: path no longer required
        def rgetattr(obj, attr, *args):
            from functools import reduce

            def _getattr(obj, attr):
                return getattr(obj, attr, *args)

            return reduce(_getattr, [obj] + attr.split("."))

        if columns is None:
            columns = [
                "name",
                "target.name",
                "class_mahlke",
                "class_demeo",
                "class_tholen",
                "filename",
            ]

        result = []

        for spec in self:
            row = {}
            for col in columns:
                if hasattr(spec, col.split(".")[0]):
                    row[col] = rgetattr(spec, col)
            result.append(row)

        result = pd.DataFrame(data=result, index=list(range(len(self))))
        if path is not None:
            result.to_csv(path, index=False)
        return result
