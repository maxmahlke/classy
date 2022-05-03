import warnings

import classy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
import numpy as np

# Ensure uniform plot appearance
mpl.rcParams.update(mpl.rcParamsDefault)


def get_colors(N):
    """
    Get a list of unique colors.

    Parameters
    ----------
    N : int
        The number of unique colors to return.

    Returns
    -------
    list of str
        A list of color-hexcodes.

    """
    COLORS = plt.cm.get_cmap("gnuplot", N)
    return [mpl.colors.rgb2hex(COLORS(i)[:3]) for i in range(N)]


def plot(data):
    """
    Plot the classified data in latent and data space inlcuding the class- and cluster probabilities.

    Parameters
    ----------
    data : pd.DataFrame
        The classified input data.
    """
    COLORS = get_colors(len(data))

    fig, axes = plt.subplots(figsize=(15, 12), nrows=3, ncols=3)

    # Load classy latent scores for background distribution
    classy_data = classy.data.load()

    # Plot the distribution in latent space
    for i in range(classy.defs.MODEL_PARAMETERS["d"] - 1):
        for j in range(classy.defs.MODEL_PARAMETERS["d"] - 1):

            dx = j  # latent dimension on x-axis
            dy = i + 1  # latent dimension on y-axis

            if dx >= dy:
                continue

            # Background
            axes[i, j].scatter(
                classy_data.loc[:, f"z{dx}"],
                classy_data.loc[:, f"z{dy}"],
                c="gray",
                alpha=0.3,
                marker=".",
            )

            # Highlight mean score
            axes[i, j].axhline(0, ls=":", c="dimgray")
            axes[i, j].axvline(0, ls=":", c="dimgray")

            # Add scores of classified data
            # Iterate as plt.scatter does not accept list of markers
            for ind, obs in data.iterrows():
                axes[i, j].scatter(obs[f"z{dx}"], obs[f"z{dy}"], alpha=0)
                axes[i, j].text(
                    obs[f"z{dx}"], obs[f"z{dy}"], str(ind), color=COLORS[ind], size=13
                )

    # Plot the input data
    for ind, obs in data.iterrows():
        axes[0, 1].plot(
            classy.defs.WAVE_GRID,
            np.exp(obs.loc[classy.defs.WAVE_GRID].astype(float)),
            label=str(ind),
            color=COLORS[ind],
        )
        axes[0, 1].scatter(
            2.5, np.power(10, float(obs.loc["pV"])) + 1, color=COLORS[ind]
        )

    axes[0, 1].legend(frameon=False, ncol=len(data) if len(data) <= 5 else 4)
    axes[0, 1].set(ylim=(0.6, 2.2))

    # Add the cluster probabilities
    for ind, obs in data.iterrows():
        axes[0, 2].bar(
            range(classy.defs.MODEL_PARAMETERS["k"]),
            height=obs.loc[
                [f"cluster_{i}" for i in range(classy.defs.MODEL_PARAMETERS["k"])]
            ],
            facecolor="none",
            edgecolor=COLORS[ind],
        )
    axes[0, 2].set(ylim=(0, 1))

    # And now the class probablities
    for ind, obs in data.iterrows():
        print({c: obs[f"class_{c}"] for c in classy.defs.CLASSES})
        axes[1, 2].bar(
            classy.defs.CLASSES,
            height=[obs[f"class_{c}"] for c in classy.defs.CLASSES],
            facecolor="none",
            edgecolor=COLORS[ind],
        )
    axes[1, 2].set(ylim=(0, 1))

    # All done
    fig.tight_layout()
    plt.show()


def _smooth_interactive(spectrum):
    """Helper to smooth spectrum interactively. Call the 'smooth' function instead."""

    # Suppress unrelated deprecation warning on TextBox.submit
    warnings.simplefilter("ignore", mpl.MatplotlibDeprecationWarning)

    _, ax = spectrum.plot(show=False)

    # Include widgets
    def update_smooth(_):
        """Read the GUI values and re-smooth the spectrum."""
        spectrum.smooth_degree = int(degree_box.text)
        spectrum.smooth_window = int(window_box.text)

        spectrum.smooth(interactive=False)
        ax.get_lines()[1].set_ydata(spectrum.refl_smoothed)
        plt.draw()

    def update_and_exit(_):
        """Update the smoothing and quit the plot."""
        update_smooth(None)
        plt.close()

    ax_win = plt.axes([0.25, 0.90, 0.05, 0.03])
    window_box = TextBox(ax_win, "Smoothing Window", initial=spectrum.smooth_window)

    ax_deg = plt.axes([0.45, 0.90, 0.05, 0.03])
    degree_box = TextBox(ax_deg, "Smoothing Degree", initial=spectrum.smooth_degree)

    ax_update = plt.axes([0.55, 0.90, 0.12, 0.03])
    update = Button(ax_update, "Update Smoothing")

    ax_exit = plt.axes([0.75, 0.90, 0.12, 0.03])
    exit_ = Button(ax_exit, "Save and Exit")

    window_box.on_submit(lambda x: update_smooth(x))
    degree_box.on_submit(lambda x: update_smooth(x))
    update.on_clicked(lambda x: update_smooth(x))
    exit_.on_clicked(lambda x: update_and_exit(x))

    plt.show()


def _plot_spectrum(spectrum, show=True):
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

    fig, ax = plt.subplots(figsize=(13, 7))

    ax.plot(spectrum.wave, spectrum.refl, alpha=1, ls="-", c="black", label="Original")

    if spectrum.refl_smoothed is not None:
        ax.plot(
            spectrum.wave,
            spectrum.refl_smoothed,
            marker="",
            ls="-",
            c="red",
            label="Smoothed",
        )

    # Shade atmospheric absorption bands
    for lower, upper in classy.defs.TELLURIC_TROUBLE:
        ax.axvspan(lower, upper, alpha=0.3, color="gray", edgecolor=None, linewidth=0)

    for limit in [classy.defs.LIMIT_VIS, classy.defs.LIMIT_NIR]:
        ax.axvline(limit, ls="--", c="black")

    ax.set(xlabel=r"Wavelength / micron", ylabel=r"Reflectance")

    if show:
        plt.show()

    return fig, ax


def fit_feature():
    fig, ax = plt.subplots()

    (spectrum,) = ax.plot(wave, refl_no_continuum, ls="-", c="dimgray")
    (band_fit,) = ax.plot(
        xrange[xrange_fit],
        band(xrange[xrange_fit]),
        ls="--",
        c="firebrick" if not present else "steelblue",
        lw=2,
    )

    lambda_min = ax.axvline(FEATURE["lower"], ls=":", c="dimgray")
    lambda_max = ax.axvline(FEATURE["upper"], ls=":", c="dimgray")
    ax.axvline(FEATURE["center"][0], ls="--", c="black")

    # Make interactive
    ax_lower = plt.axes([0.15, 0.1, 0.25, 0.03])
    lower_slider = Slider(
        ax=ax_lower,
        label="Lower",
        valmin=0.45,
        valmax=1.2,
        valinit=FEATURE["lower"],
    )

    ax_upper = plt.axes([0.55, 0.1, 0.25, 0.03])
    upper_slider = Slider(
        ax=ax_upper,
        label="Upper",
        valmin=0.45,
        valmax=1.2,
        valinit=FEATURE["upper"],
    )

    def update_lower(lower_limit):

        # Update limit value
        FEATURE["lower"] = lower_limit

        # Change v-line
        lambda_min.set_data([FEATURE["lower"], FEATURE["lower"]], [0, 1])

        # Update continuum fit
        slope = fit_continuum()
        refl_no_continuum = remove_continuum(slope)
        spectrum.set_ydata(refl_no_continuum)

        # Update band fit
        band = fit_band(refl_no_continuum)

        xrange_fit = (FEATURE["lower"] < xrange) & (FEATURE["upper"] > xrange)
        band_fit.set_xdata(xrange[xrange_fit])
        band_fit.set_ydata(band(xrange[xrange_fit]))

        center, depth = get_band_center_and_depth(band)
        snr = compute_snr(band, refl_no_continuum)
        present = band_present(center, snr)
        if present:
            band_fit.set_color("steelblue")
        else:
            band_fit.set_color("firebrick")

        print(f"Band center: {center:.3f}")
        print(f"Band depth: {depth:.3f}")
        print(f"SNR: {snr:.2f}")
        print(f"Present: {present}")
        # recompute the ax.dataLim
        ax.relim()
        # update ax.viewLim using the new dataLim
        ax.autoscale_view()
        fig.canvas.draw_idle()

    def update_upper(upper_limit):

        # Update limit value
        FEATURE["upper"] = upper_limit

        # Change v-line
        lambda_max.set_data([FEATURE["upper"], FEATURE["upper"]], [0, 1])

        # Update continuum fit
        slope = fit_continuum()
        refl_no_continuum = remove_continuum(slope)
        spectrum.set_ydata(refl_no_continuum)

        # Update band fit
        band = fit_band(refl_no_continuum)

        xrange_fit = (FEATURE["lower"] < xrange) & (FEATURE["upper"] > xrange)
        band_fit.set_xdata(xrange[xrange_fit])
        band_fit.set_ydata(band(xrange[xrange_fit]))

        center, depth = get_band_center_and_depth(band)
        snr = compute_snr(band, refl_no_continuum)
        present = band_present(center, snr)
        if present:
            band_fit.set_color("steelblue")
        else:
            band_fit.set_color("firebrick")

        print(f"Band center: {center:.3f}")
        print(f"Band depth: {depth:.3f}")
        print(f"SNR: {snr:.2f}")
        print(f"Present: {present}")

        # recompute the ax.dataLim
        ax.relim()
        # update ax.viewLim using the new dataLim
        ax.autoscale_view()
        fig.canvas.draw_idle()

    # register the update function with each slider
    lower_slider.on_changed(update_lower)
    upper_slider.on_changed(update_upper)

    plt.show()
