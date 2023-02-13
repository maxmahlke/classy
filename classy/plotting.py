import warnings

warnings.filterwarnings(
    "ignore", message="Warning: converting a masked element to nan."
)

import classy
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox
import numpy as np

from classy import cache


def get_colors(N, cmap="turbo"):
    """
    Get a list of unique colors.

    Parameters
    ----------
    N : int
        The number of unique colors to return.
    cmap : str
        The matplotlib colormap to sample. Default is 'turbo'

    Returns
    -------
    list of str
        A list of color-hexcodes.

    """
    COLORS = plt.cm.get_cmap(cmap, N)
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
    classy_data = classy.data.load("classy")

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
            axes[i, j].axhline(0, ls=":", c="gray")
            axes[i, j].axvline(0, ls=":", c="gray")

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
    axes[0, 1].set(xlim=(0.45, 2.5))

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
    CLASSES = classy.defs.CLASSES
    CLASSES.remove("Ch")

    for ind, obs in data.iterrows():
        axes[1, 2].bar(
            CLASSES,
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


def plot_spectra(spectra, add_classes=False, system="Mahlke+ 2022"):
    """Plot spectra. Called by 'classy spectra [id] -p'.

    Parameters
    ----------
    spectra : list of classy.spectra.Spectrum
        The spectra to plot.
    add_classes : bool
        Add axes showing classification preprocessing and results.
    """
    # Ensure uniform plot appearance
    mpl.rcParams.update(mpl.rcParamsDefault)

    # Add color information to spectrum for simplicity
    # n_smass = sum([1 for spec in spectra if spec.source == "SMASS"])
    # colors_smass = get_colors(n_smass, "turbo")
    colors = get_colors(len(spectra), cmap="jet")

    # Build figure instance
    if add_classes:
        fig, axes = plt.subplots(
            ncols=3, figsize=(14, 5), gridspec_kw={"width_ratios": [4, 1, 4]}
        )
        ax_spec, ax_pv, ax_classes = axes
    else:
        fig, ax_spec = plt.subplots()

    # 1. Plot spectra
    smass_lines, smass_labels = [], []
    gaia_lines, gaia_labels = [], []
    for spec in spectra:

        if spec.source in ["SMASS", "Gaia"]:

            spec.color = colors.pop()
            if spec.source == "SMASS":
                smass_line, smass_label = plot_smass_spectrum(ax_spec, spec)
                smass_lines.append(*smass_line)
                smass_labels.append(*smass_label)

            else:
                spec.color = "black"
                gaia_lines, gaia_labels = plot_gaia_spectrum(ax_spec, spec)

        elif spec.source == "user":
            raise Error  # to be implemented

    # Axis setup
    # Construct legend
    lines, labels = [], []

    if gaia_lines:
        (dummy,) = ax_spec.plot([], [], alpha=0)
        lines += [dummy, dummy] + gaia_lines
        labels += ["", "Gaia"] + gaia_labels
    if smass_lines:
        (dummy,) = ax_spec.plot([], [], alpha=0)
        lines += [dummy, dummy] + smass_lines
        labels += ["", "SMASS"] + smass_labels

    if add_classes:

        (dummy,) = ax_spec.plot([], [], alpha=0)
        l1 = ax_spec.errorbar(
            [], [], yerr=[], capsize=3, ls="", c="black", lw=1, alpha=0.3
        )
        (l2,) = ax_spec.plot([], [], ls="-", c="black")
        lines += [dummy, l1, l2]
        labels += ["", "Observed", "Preprocessed"]
    leg = ax_spec.legend(
        lines,
        labels,
        edgecolor="none",
        loc="center right"
        # frameon=False,
        # loc="lower center",
        # bbox_to_anchor=(1.2, 1.08),
        # ncol=2,
    )
    ax_spec.add_artist(leg)
    # if any(spec.source == "SMASS" for spec in spectra):
    #
    #     ax_spec.legend(  # SMASS legend, Gaia one is added in function
    #         facecolor="white",
    #         edgecolor="none",
    #         title="SMASS",
    #         loc="lower right",
    #     )

    if add_classes:
        ax_spec.axvline(0.45, ls=":", zorder=-10, c="dimgray")
        ax_spec.axvline(2.45, ls=":", zorder=-10, c="dimgray")

    # ensure that there is space for the legend by adding empty space
    xmin, xmax = ax_spec.get_xlim()
    xmax += 1 / 2.8 * (xmax - xmin)

    ax_spec.set(xlabel=r"Wavelength / $\mu$m", ylabel="Reflectance", xlim=(xmin, xmax))

    # 2. Add pV axis
    if add_classes:

        # Are all albedos the same?
        if len(set(spec.pV for spec in spectra)) == 1:
            ax_pv.errorbar(
                0,
                spectra[0].pV,
                yerr=spectra[0].pV_err,
                capsize=3,
                marker=".",
                c="dimgray",
            )
            ax_pv.set_xticks([], [])

        else:
            for i, spec in enumerate(spectra):
                ax_pv.errorbar(
                    i, spec.pV, yerr=spec.pV_err, capsize=3, marker=".", c=spec.color
                )

            ax_pv.set_xticks(
                range(len(spectra)), [f"{spec.name}" for spec in spectra], rotation=90
            )

        ymin, ymax = ax_pv.get_ylim()
        ymin = 0 if ymin < 0.1 else ymin
        ymax += 0.051

        ax_pv.set(xlabel="pV", ylim=(ymin, ymax))

    # 3. Add classes
    if add_classes:

        width = 0.8 / len(spectra)

        for i, spec in enumerate(spectra):
            for x, class_ in enumerate(classy.defs.CLASSES):
                ax_classes.bar(
                    x - 0.3 + i * width,
                    getattr(spec, f"class_{class_}"),
                    fill=True,
                    color=spec.color,
                    width=width,
                    alpha=0.7,
                    label=f"{spec.name}: {spec.class_}" if x == 0 else None,
                )
        ax_classes.set(ylim=(0, 1))
        ax_classes.set_xticks(
            [i for i, _ in enumerate(classy.defs.CLASSES)], classy.defs.CLASSES
        )
        ax_classes.legend(title="Most Likely Class", frameon=True, edgecolor="none")
        ax_classes.grid(c="gray", alpha=0.4, zorder=-100)

    if spec.asteroid_name is not None:
        ax_spec.set_title(
            f"({spec.asteroid_number}) {spec.asteroid_name}", loc="left", size=10
        )
    if add_classes:
        ax_classes.set_title(f"Classification following {system}", loc="left", size=10)

    fig.tight_layout()
    plt.show()


def plot_smass_spectrum(ax, spec):
    """Plot a SMASS spectrum.

    Parameters
    ----------
    ax : matplotlib.axes.Axis
        The axis to plot to.
    spec : classy.spectra.Spectrum
        The SMASS spectrum to plot.
    """

    # Error-interval

    if hasattr(spec, "refl_interp"):
        l1 = ax.errorbar(
            spec.wave,
            spec.refl,
            yerr=spec.refl_err,
            c=spec.color,
            label=f"{spec.run}",
            alpha=0.4,
            capsize=3,
            ls="",
        )
        ax.plot(classy.defs.WAVE_GRID, spec.refl_interp, c=spec.color)

    else:
        # Line
        (l1,) = ax.plot(
            spec.wave, spec.refl, c=spec.color, label=f"{spec.run}", ls="-", alpha=0.5
        )

        ax.fill_between(
            spec.wave,
            spec.refl + spec.refl_err / 2,
            spec.refl - spec.refl_err / 2,
            color=spec.color,
            alpha=0.3,
            ec="none",
        )

    line = [l1]
    label = [spec.name]
    return line, label


def plot_gaia_spectrum(ax, spec):
    """Plot a Gaia spectrum.

    Parameters
    ----------
    ax : matplotlib.axes.Axis
        The axis to plot to.
    spec : classy.spectra.Spectrum
        The Gaia spectrum to plot.
    """

    # Line to guide the eye
    ax.plot(spec.wave, spec.refl, ls=":", lw=1, c=spec.color, zorder=100)

    # Errorbars colour-coded by photometric flag
    props = dict(lw=1, capsize=3, ls="", zorder=100)
    l0 = ax.errorbar(spec.wave, spec.refl, yerr=spec.refl_err, c=spec.color, **props)

    lines = [l0]  # to construct Gaia-specific legend

    f1 = spec.flag == 1
    f2 = spec.flag == 2

    if any(f1):
        l1 = ax.errorbar(
            spec.wave[f1], spec.refl[f1], yerr=spec.refl_err[f1], c="orange", **props
        )
        lines.append(l1)

    if any(f2):
        l2 = ax.errorbar(
            spec.wave[f2], spec.refl[f2], yerr=spec.refl_err[f2], c="red", **props
        )
        lines.append(l2)

    labels = [f"Flag {i}" for i, _ in enumerate(lines)]

    if hasattr(spec, "refl_interp"):
        (l3,) = ax.plot(
            classy.defs.WAVE_GRID,
            spec.refl_interp,
            ls="-",
            lw=1,
            c=spec.color,
            zorder=100,
        )
    # lines.append(l3)

    # Add Gaia-specific legend
    # labels += ["Preprocessed"]
    # leg = ax.legend(
    #     lines,
    #     labels,
    #     facecolor="white",
    #     edgecolor="none",
    #     loc="lower center",
    #     title="Gaia",
    # )
    # ax.add_artist(leg)
    return lines, labels
