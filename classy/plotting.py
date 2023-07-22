import warnings

warnings.filterwarnings(
    "ignore", message="Warning: converting a masked element to nan."
)

import classy
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from classy import taxonomies


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
    # CLASSES.remove("Ch")

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


def plot_spectra(spectra, taxonomy=None, save=None, templates=None):
    """Plot spectra. Called by 'classy spectra [id]'.

    Parameters
    ----------
    spectra : list of classy.spectra.Spectrum
        The spectra to plot.
    taxonomy : str
        The taxonomic system to plot. Choose from ['mahlke', 'demeo', 'tholen'].
        Default is None, in which case no classification results are added.
    save : str
        Path to save the figure under. Default is None, which opens the
        plot instead of saving it.
    """

    # Give user some degree of freedom in taxonomy specification
    if taxonomy is not None:
        if taxonomy.lower() not in classy.taxonomies.SYSTEMS:
            raise ValueError(
                f"Unknown taxonomy '{taxonomy}'. Choose from {classy.taxonomies.SYSTEMS}."
            )

    # Ensure uniform plot appearance
    mpl.rcParams.update(mpl.rcParamsDefault)

    # Add color information to spectrum
    colors = get_colors(len(spectra), cmap="jet")
    lines, labels = [], []  # for the global legend

    # Build figure instance
    if taxonomy is not None:
        fig, axes = plt.subplots(
            ncols=3, figsize=(16, 7), gridspec_kw={"width_ratios": [4, 1, 4]}
        )
        ax_spec, ax_pv, ax_classes = axes
    else:
        fig, ax_spec = plt.subplots(figsize=(10, 7))

    # 1. Plot spectra, grouped by _source
    _sources = sorted(set(spec._source for spec in spectra))

    for source in _sources:
        lines_source, labels_source = [], []
        for spec in spectra:
            if taxonomy == "mahlke" and spec.source != "Gaia":
                # spec.wave_plot = spec._wave_pre_norm
                # spec.refl_plot = spec._refl_pre_norm
                spec._wave_preprocessed = spec._wave_pre_norm
                spec._refl_preprocessed = spec._refl_pre_norm
            if not hasattr(spec, "wave_plot"):
                spec.wave_plot = spec.wave
                spec.refl_plot = spec.refl

            spec._color = colors.pop() if source != "Gaia" else "black"

            if source == "Gaia":
                user_line, user_label = plot_gaia_spectrum(ax_spec, spec)
            else:
                user_line, user_label = plot_user_spectrum(ax_spec, spec)

            for line, label in zip(user_line, user_label):
                lines_source.append(line)
                labels_source.append(label)

        (dummy,) = ax_spec.plot([], [], alpha=0)
        lines += [dummy, dummy] + lines_source
        labels += ["", source] + labels_source

    # (dummy,) = ax_spec.plot([], [], alpha=0)
    # (l1,) = ax_spec.plot([], [], ls="-", c="black", lw=1)
    # (l2,) = ax_spec.plot([], [], ls="-", c="black", alpha=0.3, lw=3)
    # lines += [dummy, l1, l2]
    # labels += ["", "Reflectance", "Uncertainty"]

    if taxonomy is not None:
        (l3,) = ax_spec.plot([], [], ls=":", c="gray")
        lines += [dummy, l3]
        labels += ["", "Taxonomy Limits"]

    if templates is not None:
        plot_class_templates(ax_spec, taxonomy, templates)
        if taxonomy is None or taxonomy == "mahlke":
            scheme = "Mahlke+ 2022"
        elif taxonomy == "bus":
            scheme = "Bus and Binzel 2002"
        elif taxonomy == "tholen":
            scheme = "Tholen 1984"
        elif taxonomy == "demeo":
            scheme = "DeMeo+ 2009"
        (l3,) = ax_spec.plot([], [], ls=(1, (1, 7)), alpha=0.3, c="gray")
        lines += [dummy, dummy, l3]
        labels += ["", f"Class Templates", f"Complex {templates} - {scheme}"]

    leg = ax_spec.legend(
        lines,
        labels,
        edgecolor="none",
        # ncols=4,
        # loc="upper center",
        # loc="lower left",
        loc="center right",
        # bbox_to_anchor=(0.5, 1.3),
        fontsize=8,
    )
    ax_spec.add_artist(leg)

    if taxonomy is not None:
        wave = getattr(taxonomies, taxonomy).WAVE
        lower, upper = min(wave), max(wave)
        ax_spec.axvline(lower, ls=":", zorder=-10, c="gray")
        ax_spec.axvline(upper, ls=":", zorder=-10, c="gray")

    # ensure that there is space for the legend by adding empty space
    xmin, xmax = ax_spec.get_xlim()
    xmax += 1 / 2.8 * (xmax - xmin)

    ymin, ymax = ax_spec.get_ylim()
    if ymax - ymin < 0.1:
        ymin -= 0.05
        ymax += 0.05

    ax_spec.set(
        xlabel=r"Wavelength / µm",
        ylabel="Reflectance",
        xlim=(xmin, xmax),
        ylim=(ymin, ymax),
    )

    # 2. Add pV axis
    if taxonomy is not None:
        for i, spec in enumerate(spectra):
            ax_pv.errorbar(
                i, spec.pV, yerr=spec.pV_err, capsize=3, marker=".", c=spec._color
            )

        ticklabels = [
            spec.shortbib if hasattr(spec, "shortbib") else spec._source
            for spec in spectra
        ]
        ax_pv.set_xticks(range(len(spectra)), ticklabels, rotation=90)

        ymin, ymax = ax_pv.get_ylim()
        ymin = 0 if ymin < 0.1 else ymin
        ymax += 0.051

        ax_pv.set(xlabel="pV", ylim=(ymin, ymax), xlim=(-0.5, len(spectra) - 0.5))

    # 3. Add classes
    if taxonomy is not None:
        if taxonomy == "mahlke":
            width = 0.8 / len(spectra)

            for i, spec in enumerate(spectra):
                if not hasattr(spec, "class_A"):
                    continue  # spec was not classified following Mahlke+ 2022
                for x, class_ in enumerate(classy.defs.CLASSES):
                    ax_classes.bar(
                        x - 0.3 + i * width if len(spectra) > 1 else x,
                        getattr(spec, f"class_{class_}"),
                        fill=True,
                        color=spec._color,
                        width=width,
                        alpha=0.7,
                        label=f"{spec.shortbib if hasattr(spec, 'shortbib') else spec._source}: {spec.class_}"
                        if x == 0
                        else None,
                    )
            ax_classes.set(ylim=(0, 1))
            ax_classes.set_xticks(
                [i for i, _ in enumerate(classy.defs.CLASSES)], classy.defs.CLASSES
            )
            ax_classes.legend(title="Most Likely Class", frameon=True, edgecolor="none")
            ax_classes.grid(c="gray", alpha=0.4, zorder=-100)
        elif "tholen" in taxonomy:
            ax_classes = taxonomies.tholen.plot_pc_space(ax_classes, spectra)
        elif "demeo" in taxonomy:
            ax_classes = taxonomies.demeo.plot_pc_space(ax_classes, spectra)

    if spec.name is not None:
        ax_spec.set_title(f"({spec.number}) {spec.name}", loc="left", size=10)
    if taxonomy is not None:
        if taxonomy == "tholen":
            taxonomy = "Tholen 1984"
        if taxonomy == "mahlke":
            taxonomy = "Mahlke+ 2022"
        if taxonomy == "demeo":
            taxonomy = "DeMeo+ 2009"
        ax_classes.set_title(
            f"Classification following {taxonomy}", loc="left", size=10
        )

    fig.tight_layout()

    if save is None:
        plt.show()
    else:
        fig.savefig(save)


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
            c=spec._color,
            alpha=0.4,
            capsize=3,
            ls="",
        )
        ax.plot(spec.wave_interp, spec.refl_interp, c=spec._color)

    else:
        # Line
        (l1,) = ax.plot(
            spec.wave,
            spec.refl,
            c=spec._color,
            ls="-",
            alpha=0.5,
        )

        ax.fill_between(
            spec.wave,
            spec.refl + spec.refl_err / 2,
            spec.refl - spec.refl_err / 2,
            color=spec._color,
            alpha=0.3,
            ec="none",
        )

    line = [l1]
    label = [spec.shortbib]
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
    ax.plot(spec.wave_plot, spec.refl_plot, ls=":", lw=1, c=spec._color, zorder=100)

    # Errorbars colour-coded by photometric flag
    props = dict(lw=1, capsize=3, ls="", zorder=100)
    l0 = ax.errorbar(
        spec.wave,
        spec.refl,
        yerr=spec.refl_err,
        c=spec._color,
        **props,
    )

    lines = [l0]  # to construct Gaia-specific legend

    f1 = spec.flag == 1
    f2 = spec.flag == 2

    if any(f1):
        l1 = ax.errorbar(
            spec.wave[f1],
            spec.refl[f1],
            yerr=spec.refl_err[f1],
            c="orange",
            **props,
        )
        lines.append(l1)

    if any(f2):
        l2 = ax.errorbar(
            spec.wave[f2],
            spec.refl[f2],
            yerr=spec.refl_err[f2],
            c="red",
            **props,
        )
        lines.append(l2)

    labels = [f"Flag {i}" for i, _ in enumerate(lines)]

    if hasattr(spec, "refl_interp"):
        (l3,) = ax.plot(
            # classy.defs.WAVE_GRID,
            spec.wave_interp,
            spec.refl_interp,
            ls="-",
            lw=1,
            c=spec._color,
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


def plot_akari_spectrum(ax, spec):
    """Plot an AKARI spectrum.

    Parameters
    ----------
    ax : matplotlib.axes.Axis
        The axis to plot to.
    spec : classy.spectra.Spectrum
        The Gaia spectrum to plot.
    """

    # Line to guide the eye
    ax.plot(spec.wave, spec.refl, ls=":", lw=1, c=spec._color, zorder=100)

    # Errorbars colour-coded by photometric flag
    props = dict(lw=1, capsize=3, ls="", zorder=100)
    l0 = ax.errorbar(
        spec.wave[spec.flag != 1],
        spec.refl[spec.flag != 1],
        yerr=spec.refl_err[spec.flag != 1],
        c=spec._color,
        **props,
    )

    lines = [l0]  # to construct AKARI-specific legend

    f1 = spec.flag == 1

    if any(f1):
        l1 = ax.errorbar(
            spec.wave[f1],
            spec.refl[f1],
            yerr=spec.refl_err[f1],
            c=spec._color,
            **props,
            alpha=0.3,
        )
        lines.append(l1)

    labels = [f"Flag {i}" for i, _ in enumerate(lines)]

    if hasattr(spec, "refl_interp"):
        (l3,) = ax.plot(
            spec.wave_interp,
            spec.refl_interp,
            ls="-",
            lw=1,
            c=spec._color,
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


def plot_ecas_spectrum(ax, spec):
    """Plot an ECAS spectrum.

    Parameters
    ----------
    ax : matplotlib.axes.Axis
        The axis to plot to.
    spec : classy.spectra.Spectrum
        The Gaia spectrum to plot.
    """

    # Line to guide the eye
    ax.plot(spec.wave, spec.refl, ls="--", lw=1, c=spec._color, zorder=100)

    # Errorbars colour-coded by photometric flag
    props = dict(lw=1, capsize=3, ls="", zorder=100)

    l0 = ax.errorbar(
        spec.wave[spec.flag != 1],
        spec.refl[spec.flag != 1],
        yerr=spec.refl_err[spec.flag != 1],
        c=spec._color,
        **props,
    )

    lines = [l0]  # to construct AKARI-specific legend

    f1 = spec.flag == 1

    if any(f1):
        l1 = ax.errorbar(
            spec.wave[f1],
            spec.refl[f1],
            yerr=spec.refl_err[f1],
            c=spec._color,
            **props,
            alpha=0.3,
        )
        lines.append(l1)

    labels = [f"Flag {i}" for i, _ in enumerate(lines)]

    if hasattr(spec, "refl_interp"):
        (l3,) = ax.plot(
            # classy.defs.WAVE_GRID,
            spec.wave_interp,
            spec.refl_interp,
            ls="-",
            lw=1,
            c=spec._color,
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


def plot_user_spectrum(ax, spec):
    """Plot a user provided spectrum.

    Parameters
    ----------
    ax : matplotlib.axes.Axis
        The axis to plot to.
    spec : classy.spectra.Spectrum
        The SMASS spectrum to plot.
    """

    # Plot original
    if not hasattr(spec, "_refl_preprocessed"):
        wave = spec.wave
        refl = spec.refl
        err = spec.refl_err
    else:
        wave = spec._wave_preprocessed
        refl = spec._refl_preprocessed
        err = np.nan

    (l1,) = ax.plot(
        wave,
        refl,
        c=spec._color,
        ls="-",
        alpha=0.5,
    )

    if err is not None:
        ax.fill_between(
            wave,
            refl + err / 2,
            refl - err / 2,
            color=spec._color,
            alpha=0.3,
            ec="none",
        )

    line = [l1]

    if hasattr(spec, "shortbib"):
        label = spec.shortbib
    elif hasattr(spec, "source"):
        label = spec.source
    else:
        label = "User"
    label = [label]
    return line, label


def plot_class_templates(ax, scheme, complex):
    """Add class templates of taxonomic scheme to figure."""
    if scheme is None:
        scheme = "mahlke"

    if scheme not in ["bus", "demeo", "mahlke", "tholen"]:
        raise ValueError(f"Unknown taxonomy '{scheme}' for class templates.")

    templates = getattr(taxonomies, scheme).load_templates()

    for class_, spec in templates.items():
        if class_ not in taxonomies.COMPLEXES[complex]:
            continue

        ax.plot(spec.wave, spec.refl, ls=(1, (1, 7)), alpha=0.3, c="gray", zorder=-100)
        for w, r in zip(spec.wave[::2], spec.refl[::2]):
            ax.text(
                w,
                r,
                class_,
                size=6,
                c="gray",
                ha="center",
                va="center",
                clip_on=True,
                alpha=0.5,
            )
