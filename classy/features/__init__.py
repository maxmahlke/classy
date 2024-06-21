import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy import interpolate, signal

from classy import config
from classy import index
from classy.utils.logging import logger


# Parameters for feature-fits
FEATURE = {
    # feature: center [mean, std], lower and upper fitting window limits
    "e": {
        "candidates": ["P", "M", "E", "X"],
        "center": [0.49725, 0.0055],
        "lower": 0.45,
        "upper": 0.54,
    },
    "h": {
        "candidates": ["B", "C", "P", "X"],
        "center": [0.69335, 0.011],
        "lower": 0.61,
        "upper": 0.80,
        # "upper": 0.934,
    },
    "k": {
        "candidates": ["P", "M", "E", "X"],
        "center": [0.90596, 0.017],
        "lower": 0.76,
        "upper": 1.06,
    },
}


def store(features):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        features["number"] = features["number"].astype("Int64")
    features.to_csv(config.PATH_DATA / "features.csv", index=True)


def load():
    """Load the feature index."""
    if not (config.PATH_DATA / "features.csv").is_file():
        # Creating indices
        ind = pd.MultiIndex(
            levels=[[], []],
            codes=[[], []],
            names=["filename", "feature"],
        )
        return pd.DataFrame(index=ind, columns=["is_present"])
    return pd.read_csv(
        config.PATH_DATA / "features.csv",
        index_col=["filename", "feature"],
        dtype={"is_present": bool},
    )


class Feature:
    def __init__(self, name, spec):
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
        self.spec = spec

        # Initialize default feature and fit parameters
        self.upper = FEATURE[name]["upper"]
        self.lower = FEATURE[name]["lower"]

        self.deg_poly = 4
        self.type_continuum = "linear"

        self.is_candidate = True
        self.is_present = False

        # Update parameters if present in feature index
        if self.has_parameters:
            self.load_parameters()
        else:
            self.center = np.nan
            self.depth = np.nan

        # Set interpolation range for continuum, fit, and parameter estimation
        self.range_interp = np.arange(self.lower, self.upper, 0.001)

    def __repr__(self):
        return f"<Feature {self.name}>"

    @property
    def wave(self):
        return self.spec.wave[
            (self.spec.wave > self.lower) & (self.spec.wave < self.upper)
        ]

    @property
    def refl(self):
        return self.spec.refl[
            (self.spec.wave > self.lower) & (self.spec.wave < self.upper)
        ]

    @property
    def refl_err(self):
        if self.spec.refl_err is None:
            return None
        return self.spec.refl_err[
            (self.spec.wave > self.lower) & (self.spec.wave < self.upper)
        ]

    @property
    def is_covered(self):
        """Check whether the spectral waverange covers the feature."""

        # Ensure spectral range is covered
        if self.lower < self.spec.wave.min() or self.upper > self.spec.wave.max():
            return False

        if len(self.wave) < 4:  # we need at least 4 data points
            return False

        return True

    @property
    def has_parameters(self):
        """Check whether the given feature of this spectrum has been parameterized already."""

        # We need at least a filename to store the parameters
        if not hasattr(self.spec, "filename"):
            return False

        features = load()
        ind = (self.spec.filename, self.name)
        return ind in features.index

    def load_parameters(self):
        """Load and set previously stored fit parameters from index."""
        features = load()

        ind = (self.spec.filename, self.name)

        if ind not in features.index:
            raise IndexError(f"Feature {self.name} has not been fit yet.")

        for param, value in features.loc[ind].to_dict().items():
            if param in ["name", "number", "source", "shortbib", "bibcode"]:
                continue
            setattr(self, param, value)

        # This feature has been inspected by user
        self.is_candidate = False

    def compute_continuum(self, method="linear"):
        """Compute the spectral continuum over the feature range.

        Parameters
        ----------
        method : str
            The method to compute the continuum with. Choose from ['linear', 'convex_hull']

        Notes
        -----
        The continuum callable is assigned to the 'continuum' attribute.
        """
        if method == "linear":
            self.continuum = self._compute_linear_continuum()
        elif method == "convex_hull":
            self.continuum = self._compute_hull_continuum()
        else:
            raise ValueError(
                f"Unknown continuum method '{method}', expected one of ['linear', 'convex_hull']."
            )

    def _compute_linear_continuum(self):
        """Compute linear continuum over feature range."""

        # Continuum is fit to actualy datapoints rather than interpolated range
        continuum = np.polyfit(
            [self.wave[0], self.wave[-1]], [self.refl[0], self.refl[-1]], deg=1
        )
        return np.poly1d(continuum)

    # TODO: This should be a method of the parent Spectrum class
    def _compute_hull_continuum(self):
        """Compute the continuum of a spectrum using convex-hull."""

        # Ensure that there are no NaNs
        x = self.wave[~np.isnan(self.refl)]
        y = self.refl[~np.isnan(self.refl)]

        points = np.c_[x, y]
        augmented = np.concatenate(
            [points, [(x[0], np.min(y) - 1), (x[-1], np.min(y) - 1)]], axis=0
        )

        hull = ConvexHull(augmented, qhull_options="")
        continuum_points = points[
            np.sort([v for v in hull.vertices if v < len(points)])
        ]
        continuum = interpolate.interp1d(*continuum_points.T, fill_value="extrapolate")
        return continuum

    def compute_fit(self, degree):
        """Fit the feature-region using a polynomial model.

        Parameters
        ----------
        degree : int
            The degree of the fitted polynomial.

        Notes
        -----
        The fit callable is assigned to the 'fit' attribute.
        """

        # Compute continuum and convert band to energy space
        if not hasattr(self, "continuum"):
            self.compute_continuum()

        self._fit_polynomial(degree)

    def _fit_polynomial(self, degree=3):
        """Fit a polynomial to parametrize the feature."""

        poly = np.polyfit(self.wave, self.refl / self.continuum(self.wave), deg=degree)

        # Turn into callable polynomial function
        self.fit = np.poly1d(poly)

        # Record band center and depth
        self.center = self._compute_center()
        self.depth = (1 - self.fit(self.center)) * 100

    def _compute_center(self):
        """Compute center wavelength of fit function."""
        wave_interp = np.arange(self.lower, self.upper, 0.001)
        peak = signal.find_peaks(-self.fit(wave_interp))  # '-' to find the minimum
        try:
            peak_x = wave_interp[peak[0]][0]
        except IndexError:
            peak_x = np.nan

        return peak_x

    def inspect(self):
        """Run GUI to fit feature interactively."""

        if not self.is_covered:
            logger.warning("The feature is not covered by the observed wavelength.")

        from . import gui

        gui.main(self)
        self.is_candidate = False

    def _compute_noise(self):
        """Compute mean standard deviation of fit against original data."""
        diff = abs(self.refl / self.continuum(self.wave) - self.fit(self.wave))
        self.noise = np.mean(diff)
