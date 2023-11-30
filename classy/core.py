"""Implement the Spectrum class in classy."""

import numpy as np
import pandas as pd
import rocks

from classy import cache
from classy import defs
from classy.feature import Feature
from classy.log import logger
from classy import index
from classy.taxonomies.mahlke import mixnorm
from classy import plotting
from classy import progress as prog
from classy import preprocessing
from classy import taxonomies


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
        wave = np.array([float(w) for w in wave])
        refl = np.array([float(r) for r in refl])

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
            logger.debug("Found negative values in reflectance. Ignoring them.")

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
            self.truncate(params["wave_min"], params["wave_max"])
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
            self.refl_original = preprocessing._normalize_l2(self.refl_original)

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

        ephem = cache.miriade_ephems(self.target.name, self.date_obs.split(","))

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
            features = ["e", "h", "k"]

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

    def add_feature_flags(self, data_classified):
        """Detect features in spectra and amend the classification."""

        for i, sample in data_classified.reset_index(drop=True).iterrows():
            for feature, props in defs.FEATURE.items():
                if sample.class_ in props["candidates"]:
                    if (
                        getattr(self, feature).is_covered
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

    def resample(self, wave_new, **kwargs):
        """Resample the spectrum to another wavelength grid.

        Parameters
        ----------
        wave_new : list
            The target wavelength values.

        Notes
        -----
        Any additional parameters are passed to the ``scipy.interpoalte.interp1d`` function.
        """

        self.refl = preprocessing.resample(self.wave, self.refl, wave_new, **kwargs)
        self.wave = np.array(wave_new)

        if self.refl_err is not None:
            self.refl_err = None

    def to_csv(self, path_out=None):
        """Store the classification results to file."""
        result = {}

        for attr in [
            "name",
            "number",
            "class_",
            *[f"class_{letter}" for letter in defs.CLASSES],
            "class_tholen",
            "class_demeo",
        ]:
            if hasattr(self, attr):
                result[attr] = getattr(self, attr)

        result = pd.DataFrame(data=result, index=[0])

        if path_out is not None:
            result.to_csv(path_out, index=False)
        else:
            logger.info("No 'path_out' provided, storing results to ./classy_spec.csv")
            result.to_csv("./classy_spec.csv", index=False)


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

        spectra = index.query(id, **kwargs)
        spectra = cache.load_spectra(spectra, skip_target)

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
        plotting.plot_spectra(list(self), **kwargs)

    def classify(self, taxonomy="mahlke"):
        for spec in self:
            spec.classify(taxonomy=taxonomy)

    # def echo(self):
    #     """Print list of Spectra using a nice table format."""
    #     import rich
    #     from rich.table import Table
    #
    #     if not len(self):
    #         rich.print(f"No {parameter} on record for {rock.name}.")
    #         return

    # # Sort catalogue by year of reference
    # if "year" in catalogue.columns:
    #     catalogue = catalogue.sort_values("year").reset_index()
    #
    # # ------
    # # Create table to echo
    # if parameter in ["diameters", "albedos"]:
    #     if parameter == "diameters":
    #         catalogue = catalogue.dropna(subset=["diameter"])
    #         preferred = catalogue.preferred_diameter
    #     elif parameter == "albedos":
    #         catalogue = catalogue.dropna(subset=["albedo"])
    #         preferred = catalogue.preferred_albedo
    # elif hasattr(catalogue, "preferred"):
    #     preferred = catalogue.preferred
    # else:
    #     preferred = [False for _ in range(len(catalogue))]
    #
    # # Only show the caption if there is a preferred entry
    # if any(preferred):
    #     caption = "Green: preferred entry"
    # else:
    #     caption = None
    #
    # table = Table(
    #     header_style="bold blue",
    #     box=rich.box.SQUARE,
    #     footer_style="dim",
    #     title=f"({rock.number}) {rock.name}",
    #     caption=caption,
    # )
    #
    # # The columns depend on the catalogue
    # columns = [""] + config.DATACLOUD[parameter]["print_columns"]
    #
    # for c in columns:
    #     table.add_column(c)
    #
    # # Some catalogues do not have a "preferred" attribute
    # # if not hasattr(catalogue, "preferred"):
    # #     preferred = [False for _ in range(len(catalogue))]
    # # else:
    #
    # # Add rows to table, styling by preferred-state of entry
    # for i, pref in enumerate(preferred):
    #     if parameter in ["diamalbedos"]:
    #         if pref:
    #             if (
    #                 catalogue.preferred_albedo[i]
    #                 and not catalogue.preferred_diameter[i]
    #             ):
    #                 style = "bold yellow"
    #             elif (
    #                 not catalogue.preferred_albedo[i]
    #                 and catalogue.preferred_diameter[i]
    #             ):
    #                 style = "bold blue"
    #             else:
    #                 style = "bold green"
    #         else:
    #             style = "white"
    #
    #     else:
    #         style = "bold green" if pref else "white"
    #
    #     table.add_row(
    #         *[str(catalogue[c].values[i]) if c else str(i + 1) for c in columns],
    #         style=style,
    #     )
    #
    # rich.print(table)
    #     for spec in self:
    #         print(spec)

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
            with prog.mofn as mofn:
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
            with prog.mofn as mofn:
                task = mofn.add_task("Smoothing..", total=len(self))
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

    def to_csv(self, path_out=None):
        results = {}

        for attr in [
            "name",
            "number",
            "class_",
            *[f"class_{letter}" for letter in defs.CLASSES],
            "class_tholen",
            "class_demeo",
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
