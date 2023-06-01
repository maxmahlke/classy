import lmfit
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull
from scipy import interpolate

from classy import defs
from classy.log import logger
from classy import core
from classy import config


class Feature:
    def __init__(self, name, wave, refl, refl_err=None):
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
        self.wave_spec = wave
        self.refl_spec = refl

        if all(np.isnan(r) for r in refl_err):
            refl_err = None

        self.refl_err_spec = refl_err

        # Wavelength limits for fit set heuristically from training data
        self.upper = defs.FEATURE[name]["upper"]
        self.lower = defs.FEATURE[name]["lower"]

        self.is_observed = self._is_observed()

        # Limit observation to feature range
        self.refl = self.refl_spec[
            (self.wave_spec > self.lower) & (self.wave_spec < self.upper)
        ]

        if self.refl_err_spec is not None:
            self.refl_err = self.refl_err_spec[
                (self.wave_spec > self.lower) & (self.wave_spec < self.upper)
            ]
        else:
            self.refl_err = None
        self.wave = self.wave_spec[
            (self.wave_spec > self.lower) & (self.wave_spec < self.upper)
        ]

    def _is_observed(self):
        """Check whether the spectral waverange covers the feature."""

        # Ensure spectral range is covered
        if self.lower < self.wave_spec.min() or self.upper > self.wave_spec.max():
            return False

        if (
            len(
                self.wave_spec[
                    (self.lower < self.wave_spec) & (self.upper > self.wave_spec)
                ]
            )
            < 4
        ):  # we need at least 4 data points
            logger.debug(
                f"Passed spectrum does not cover the {self.name}-feature wavelength region."
            )

            return False

        return True

    def fit(self):
        """Fit the feature-region using a Gaussian model."""

        # Compute continuum and convert band to energy space
        self.continuum = compute_continuum(self.wave, self.refl)

        if self.refl_err is not None:
            self.refl_err_energy = np.abs(
                (-1)
                * self.refl_err
                / (self.refl / self.continuum(self.wave) * np.log(10))
            )
        else:
            self.refl_err_energy = None

        self.refl_energy = (-1) * np.log10(self.refl / self.continuum(self.wave))
        self.wave_energy = 10000 / self.wave

        # Compute band fit
        band = lmfit.models.GaussianModel()
        params = band.guess(self.refl_energy, x=self.wave_energy)
        self.fit = band.fit(
            self.refl_energy,
            params,
            x=self.wave_energy,
            weights=1 / self.refl_err_energy
            if self.refl_err_energy is not None
            else None,
            nan_policy="omit",
        )

        # Record fit parameters
        self.center_energy = self.fit.result.params["center"]
        self.center = 10000 / self.center_energy

        self.sigma_energy = self.fit.result.params["sigma"]
        self.sigma = sigma = abs(
            10000 / (self.center_energy - 1 / 2 * self.sigma_energy)
            + 10000 / (self.center_energy + 1 / 2 * self.sigma_energy)
        )

        self.amplitude = self.fit.result.params["amplitude"].value
        self.amplitude /= self.sigma_energy * np.sqrt(2 * np.pi)

        self.noise = (
            np.mean(self.refl_err_energy)  # from the measurement
            if self.refl_err_energy is not None
            else np.mean(abs(self.fit.residual))  # fit residuals
        )
        self.snr = self.amplitude / self.noise

        self.is_present = self._is_present()

    def _is_present(self):
        """Check whether the feature is present based on predefined limits."""
        mean, sigma = defs.FEATURE[self.name]["center"]

        if mean - 3 * sigma >= self.center or self.center >= mean + 3 * sigma:
            return False

        elif self.snr < 1.0:
            return False

        else:
            return True

    def plot(self, path_out):
        """Plot the feature. If it was fit, the model fit is added."""

        # Has the model been fit?
        is_fit = hasattr(self, "snr")

        # Different axes arrangement depending on fit
        if is_fit:
            fig, axes = plt.subplots(ncols=2, nrows=2)
            ax_feat, ax_fit = axes[1, :]

            gs = axes[0, 0].get_gridspec()

            for ax in axes[0, :]:
                ax.remove()

            ax_spec = fig.add_subplot(gs[0, :])

            # For smooth model plot
            xrange = np.linspace(self.wave.min(), self.wave.max(), 100)
            xrange_energy = 10000 / xrange

        else:
            fig, axes = plt.subplots(nrows=2)
            ax_spec, ax_feat = axes

        # ------
        # Plot complete spectrum and continuum
        ax_spec.errorbar(
            self.wave_spec,
            self.refl_spec,
            yerr=self.refl_err_spec,
            ls="-",
            c="gray",
            label="Spectrum",
        )

        if is_fit:
            ax_spec.plot(
                xrange, self.continuum(xrange), ls=":", c="black", label="Continuum"
            )
        ax_spec.axvline(self.lower, ls=":", c="steelblue")
        ax_spec.axvline(self.upper, ls=":", c="steelblue", label="Feature Limits")

        # ------
        # Plot feature range + fit in wavelength space
        if is_fit:
            ax_feat.errorbar(
                self.wave,
                self.refl / self.continuum(self.wave),
                yerr=self.refl_err / self.continuum(self.wave)
                if self.refl_err is not None
                else None,
                ls="-",
                c="gray",
                label="Feature / Continuum",
            )

            ax_feat.plot(
                xrange,
                np.power(10, -self.fit.eval(x=xrange_energy)),
                c="black",
                label="Fit",
            )
            ax_feat.axvline(self.center, label=f"Center: {self.center:.2f}um")
        else:
            ax_feat.errorbar(
                self.wave,
                self.refl,
                yerr=self.refl_err,
                ls="-",
                c="gray",
                label="Feature",
            )

        # ------
        # Plot fit
        if is_fit:
            ax_fit.errorbar(
                self.wave_energy,
                self.refl_energy,
                yerr=self.refl_err_energy if self.refl_err_energy is not None else None,
                ls="" if self.refl_err_energy is not None else "-",
                c="gray",
                label="Feature",
            )
            ax_fit.plot(
                xrange_energy,
                self.fit.eval(x=xrange_energy),
                ls="-",
                c="black",
                label="Fit",
            )

        # ax_org.set_title(
        #     f"{self.spec.source}|{self.name}: {center:.2f}+-{sigma:.2f}, SNR={snr:.2f}"
        # )
        # ax_org.errorbar(
        #     center,
        # 1.03,
        # xerr=sigma,
        # )

        ax_spec.legend()
        ax_feat.legend()
        ax_spec.set(xlabel="Wavelength / um", ylabel="Reflectance")
        ax_feat.set(xlabel="Wavelength / um", ylabel="Reflectance")

        if is_fit:
            ax_fit.legend()
            ax_fit.set(xlabel="Wavenumber / cm-1", ylabel="Absorbance")

            ax_fit.text(
                0.1,
                0.5,
                "Present" if self.is_present else "Not Present",
                color="green" if self.is_present else "firebrick",
                transform=ax_fit.transAxes,
            )
            ax_fit.text(0.1, 0.4, f"SNR: {self.snr:.2f}", transform=ax_fit.transAxes)
            ax_fit.text(
                0.1, 0.3, f"Amp: {self.amplitude:.2f}", transform=ax_fit.transAxes
            )
            ax_fit.text(
                0.1, 0.2, f"Noise: {self.noise:.2f}", transform=ax_fit.transAxes
            )
        # for comp in eval_comps.values():
        #     ax_fit.plot(feat.wave, comp)
        # plt.plot(wave, band(wave), ls="-", c="red")
        # plt.gca().text(0.1, 0.1, f"SNR: {self.snr}", transform=plt.gca().transAxes)
        # plt.show()
        plt.savefig(path_out)
        plt.close()

    def remove_slope(self):
        # Fit first-order polynomial
        slope = np.polyfit(wave[range_fit], refl[range_fit], 1)

        # Turn into callable polynomial function
        return np.poly1d(slope)


def compute_continuum(wave, refl):
    """Compute the continuum of a spectrum using convex-hull.

    Parameters
    ----------
    wave : np.ndarray
        The wavelengths of the feature.
    refl : np.ndarray
        The reflectances of the feature.

    Returns
    -------
    func
        Function to evaluate the continuum at given values.
    """

    # Ensure that there are no NaNs
    x = wave[~np.isnan(refl)]
    y = refl[~np.isnan(refl)]

    points = np.c_[x, y]
    augmented = np.concatenate(
        [points, [(x[0], np.min(y) - 1), (x[-1], np.min(y) - 1)]], axis=0
    )

    hull = ConvexHull(augmented, qhull_options="")
    continuum_points = points[np.sort([v for v in hull.vertices if v < len(points)])]
    continuum = interpolate.interp1d(*continuum_points.T, fill_value="extrapolate")
    return continuum
