import lmfit
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import ConvexHull
from scipy import interpolate, signal

from classy import defs
from classy.log import logger


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

        # Wavelength limits for fit set heuristically from training data
        self.upper = defs.FEATURE[name]["upper"]
        self.lower = defs.FEATURE[name]["lower"]

        self.is_observed = self._is_observed()

        # Set interpolation range for continuum, fit, and parameter estimation
        self.range_interp = np.arange(self.lower, self.upper, 0.001)

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

    def _is_observed(self):
        """Check whether the spectral waverange covers the feature."""

        # Ensure spectral range is covered
        if self.lower < self.spec.wave.min() or self.upper > self.spec.wave.max():
            return False

        if len(self.wave) < 4:  # we need at least 4 data points
            logger.debug(
                f"Passed spectrum does not cover the {self.name}-feature wavelength region."
            )

            return False

        return True

    def compute_fit(self, method="polynomial", **kwargs):
        """Fit the feature-region using a Gaussian model.

        Parameters
        ----------
        method : str
            The fit method to parametrize the band. Choose from ['polynomial', 'gaussian'].
        """
        self.fit_method = method

        # Compute continuum and convert band to energy space
        if not hasattr(self, "continuum"):
            self.compute_continuum()

        if self.refl_err is not None:
            self.refl_err_energy = np.abs(
                (-1)
                * self.refl_err
                / (self.refl / self.continuum(self.wave) * np.log(10))
            )
        else:
            self.refl_err_energy = None

        if self.fit_method == "polynomial":
            self._fit_polynomial(**kwargs)
        elif self.fit_method == "gaussian":
            self._fit_gaussian(**kwargs)
        else:
            raise ValueError(
                f"Unknown fit method '{self.fit_method}'. Choose from ['polynomial', 'gaussian']."
            )

        self.is_present = self._is_present()

    def _fit_polynomial(self, degree=3):
        """Fit a polynomial to parametrize the feature."""

        poly = np.polyfit(self.wave, self.refl / self.continuum(self.wave), deg=degree)

        # Turn into callable polynomial function
        self.fit = np.poly1d(poly)

        # Record band center and depth
        self.center = self._compute_center()
        self.depth = (1 - self.fit(self.center)) * 100

    def _compute_center(self):
        wave_interp = np.arange(self.lower, self.upper, 0.001)
        peak = signal.find_peaks(-self.fit(wave_interp))  # '-' to find the minimum
        try:
            peak_x = wave_interp[peak[0]][0]
        except IndexError:
            peak_x = np.nan

        return peak_x

    def _fit_gaussian(self):
        """Fit a Gaussian Model function."""
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
        self.sigma = abs(
            10000 / (self.center_energy - 1 / 2 * self.sigma_energy)
            + 10000 / (self.center_energy + 1 / 2 * self.sigma_energy)
        )

        self.amplitude = self.fit.result.params["amplitude"].value
        self.amplitude /= self.sigma_energy * np.sqrt(2 * np.pi)
        self.depth = 1 - self.amplitude

        self.noise = (
            np.mean(self.refl_err_energy)  # from the measurement
            if self.refl_err_energy is not None
            else np.mean(abs(self.fit.residual))  # fit residuals
        )
        self.snr = self.amplitude / self.noise

    def _is_present(self):
        """Check whether the feature is present based on predefined limits."""
        mean, sigma = defs.FEATURE[self.name]["center"]

        if mean - 3 * sigma >= self.center or self.center >= mean + 3 * sigma:
            return False

        elif self.depth < 0.5:
            return False

        else:
            return True

    def plot_gaussian(self, save=None):
        """Plot the feature. If it was fit, the model fit is added."""

        # Has the model been fit?
        is_fit = hasattr(self, "center")

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
            self.spec.wave,
            self.spec.refl,
            yerr=self.spec.refl_err,
            ls="-",
            c="dimgray",
            label="Spectrum",
        )

        if is_fit:
            ax_spec.plot(
                xrange, self.continuum(xrange), ls="-", c="black", label="Continuum"
            )
        ax_spec.axvline(self.lower, ls="-", c="steelblue")
        ax_spec.axvline(self.upper, ls="-", c="steelblue", label="Feature Limits")

        # ------
        # Plot feature range + fit in wavelength space
        if is_fit:
            ax_feat.errorbar(
                self.wave,
                self.refl / self.continuum(self.wave),
                yerr=self.refl_err / self.continuum(self.wave)
                if self.refl_err is not None
                else None,
                ls="--",
                c="dimgray",
                label="Feature / Continuum",
            )

            ax_feat.plot(
                xrange,
                np.power(10, -self.fit.eval(x=xrange_energy)),
                c="black",
                label="Fit",
            )
            ax_feat.axvline(
                self.center, ls=":", label=rf"Center: {self.center:.2f} $\mu$m"
            )
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
        ax_spec.set(xlabel=r"Wavelength / $\mu$m", ylabel="Reflectance")
        ax_feat.set(xlabel=r"Wavelength / $\mu$m", ylabel="Reflectance")

        if is_fit:
            ax_fit.legend()
            ax_fit.set(xlabel=r"Wavenumber / cm$^{-1}$", ylabel="Absorbance")

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
        if save is not None:
            plt.savefig(save)
            plt.close()
        else:
            plt.show()

    def plot(self, **kwargs):
        """Plot the feature. If it was fit, the model fit is added."""

        if hasattr(self, "fit_method") and self.fit_method == "gaussian":
            self.plot_gaussian(**kwargs)
        else:
            self.plot_polynomial(**kwargs)

    def plot_polynomial(self, save=None):
        # Has the model been fit?
        is_fit = hasattr(self, "center")

        fig, ax = plt.subplots()

        # ------
        # Plot complete spectrum and continuum
        norm = max(self.spec.refl) / (1 - self.depth)
        ax.errorbar(
            self.spec.wave,
            self.spec.refl / norm,
            yerr=self.spec.refl_err,
            ls="-",
            c="gray",
            label="Spectrum",
        )

        if is_fit:
            ax.plot(
                self.range_interp,
                self.continuum(self.range_interp) / norm,
                ls="-",
                lw=0.7,
                c="black",
                label="Continuum",
            )
        ax.axvline(self.lower, ls="-", c="gray", lw=0.4)
        ax.axvline(self.upper, ls="-", c="gray", lw=0.4, label="Feature Limits")

        # ------
        # Plot continuum and feature
        if is_fit:
            ax.errorbar(
                self.wave,
                self.refl / self.continuum(self.wave),
                yerr=self.refl_err / self.continuum(self.wave)
                if self.refl_err is not None
                else None,
                ls=":",
                c="dimgray",
                label="Feature / Continuum",
            )

            ax.plot(
                self.range_interp,
                self.fit(self.range_interp),
                c="black",
                label="Fit",
            )
            ax.plot(
                [self.center, self.center],
                [1 - self.depth, 1],
                ls="-",
                c="black",
                label=rf"Center: {self.center:.2f} $\mu$m",
            )
            ax.axvline(
                self.center, ls=":", lw=0.7, label=rf"Center: {self.center:.2f} $\mu$m"
            )
            ax.text(self.center + 0.005, 0.99, rf"Center: {self.center:.3f} $\mu$m")
            ax.text(self.center + 0.005, 0.98, rf"Depth: {self.depth:.2f}\%")
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
        # if is_fit:
        #     ax_fit.errorbar(
        #         self.wave_energy,
        #         self.refl_energy,
        #         yerr=self.refl_err_energy if self.refl_err_energy is not None else None,
        #         ls="" if self.refl_err_energy is not None else "-",
        #         c="gray",
        #         label="Feature",
        #     )
        #     ax_fit.plot(
        #         xrange_energy,
        #         self.fit.eval(x=xrange_energy),
        #         ls="-",
        #         c="black",
        #         label="Fit",
        #     )
        #
        # ax_org.set_title(
        #     f"{self.spec.source}|{self.name}: {center:.2f}+-{sigma:.2f}, SNR={snr:.2f}"
        # )
        # ax_org.errorbar(
        #     center,
        # 1.03,
        # xerr=sigma,
        # )

        ax.legend()
        # ax_feat.legend()
        ax.set(xlabel=r"Wavelength / $\mu$m", ylabel="Reflectance")
        ax.set_ylim(ax.get_ylim()[0], 1)
        # ax.set_xlim(self.lower - 0.04, self.upper + 0.04)
        # ax_feat.set(xlabel=r"Wavelength / $\mu$m", ylabel="Reflectance")

        # if is_fit:
        #     ax_fit.legend()
        #     ax_fit.set(xlabel=r"Wavenumber / cm$^{-1}$", ylabel="Absorbance")
        #
        #     ax_fit.text(
        #         0.1,
        #         0.5,
        #         "Present" if self.is_present else "Not Present",
        #         color="green" if self.is_present else "firebrick",
        #         transform=ax_fit.transAxes,
        #     )
        #     ax_fit.text(0.1, 0.4, f"SNR: {self.snr:.2f}", transform=ax_fit.transAxes)
        #     ax_fit.text(
        #         0.1, 0.3, f"Amp: {self.amplitude:.2f}", transform=ax_fit.transAxes
        #     )
        #     ax_fit.text(
        #         0.1, 0.2, f"Noise: {self.noise:.2f}", transform=ax_fit.transAxes
        # )
        # for comp in eval_comps.values():
        #     ax_fit.plot(feat.wave, comp)
        # plt.plot(wave, band(wave), ls="-", c="red")
        # plt.gca().text(0.1, 0.1, f"SNR: {self.snr}", transform=plt.gca().transAxes)
        # plt.show()
        if save is not None:
            plt.savefig(save)
            plt.close()
        else:
            plt.show()

    def compute_continuum(self, method="linear"):
        if method == "linear":
            cont_func = self.compute_linear_continuum()
        elif method == "hull":
            cont_func = self.compute_hull_continuum()
        else:
            raise ValueError(
                f"Unknown continuum method '{method}', expected one of ['linear', 'hull']."
            )

        self.continuum = cont_func

    def compute_linear_continuum(self):
        """Compute spectral conintuum between lower and upper limit.
        Uses two extreme points of spectrum and fits a linear function.
        """

        # Continuum is fit to actualy datapoints rather than interpolated range
        continuum = np.polyfit(
            [self.wave[0], self.wave[-1]], [self.refl[0], self.refl[-1]], deg=1
        )

        # return callable function
        return np.poly1d(continuum)

    def compute_hull_continuum(self, _):
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

    def fit_interactive(self):
        """Run GUI to fit feature interactively."""
        from . import gui

        gui.main(self)

    def _compute_noise(self):
        # Compute mean std of fit against spectrum
        diff = abs(self.refl / self.continuum(self.wave) - self.fit(self.wave))
        self.noise = np.mean(diff)
