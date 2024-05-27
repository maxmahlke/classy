# import warnings

# warnings.filterwarnings(
#     "ignore", message="Warning: converting a masked element to nan."
# )

import classy
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from classy import taxonomies
from classy.utils.logging import logger


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
    COLORS = plt.get_cmap(cmap, N)
    return [mpl.colors.rgb2hex(COLORS(i)[:3]) for i in range(N)]


def plot_spectra(spectra, show=True, save=None, taxonomy=None):
    """Plot one or many spectra.

    Parameters
    ----------
    spectra : classy.Spectra or list of classy.Spectrum
        The spectrum / spectra to plot.
    show : bool
        Show plot immediately. Default is True.
    save : str
        Save figure to specified file path. If specified,
        show is set to False.
    taxonomy : str
        Add axis showing the classification result in the given taxonomic
        system. Choose from ['mahlke', 'demeo', 'tholen']. Default is None,
        which excludes this axis.
    """

    if taxonomy is not None and taxonomy not in ["mahlke", "demeo", "tholen"]:
        raise ValueError(
            f"Value of 'taxonomy' is {taxonomy}, expected on of ['mahlke', 'demeo', 'tholen']."
        )

    if save is not None and show:
        logger.debug(
            "If 'save' is specified, 'show' cannot be True. Setting it to False."
        )
        show = False

    # Ensure uniform plot appearance
    mpl.rcParams.update(mpl.rcParamsDefault)
    mpl.rcParams["axes.labelsize"] = 12

    # Add color information to spectrum
    colors = get_colors(len(spectra), cmap="jet")
    for i, spec in enumerate(spectra):
        spec._color = colors[i]

    # ------
    # Populate figure
    if taxonomy is None:
        fig, ax = plt.subplots(figsize=(10, 7))
        ax_spec = ax
    else:
        fig, ax = plt.subplots(figsize=(20, 7), ncols=2)
        ax_spec, ax_class = ax

    for spec in spectra:
        _plot_spectrum(ax_spec, spec)

    if taxonomy is not None:
        if taxonomy == "mahlke":
            _plot_taxonomy_mahlke(ax_class, spectra)
            _plot_albedo(ax_spec, spectra)
        elif taxonomy == "demeo":
            _plot_taxonomy_demeo(ax_class, spectra)
        elif taxonomy == "tholen":
            _plot_taxonomy_tholen(ax_class, spectra)
            _plot_albedo(ax_spec, spectra)

        ax_class.set_title(
            f"Classification following {taxonomies.FORMAT[taxonomy]}",
            loc="left",
            size=12,
        )

    # ------
    # Save, show, return
    fig.tight_layout()

    if save is not None:
        fig.savefig(save)
        logger.info(f"Figure stored under {save}")
    elif show:
        plt.show()

    return fig, ax


def _plot_spectrum(ax, spec, **kwargs):
    """Plot the spectrum.

    Parameters
    ----------
    spec

    """

    if spec.source == "Gaia" and spec.host == "Gaia":
        return plot_gaia_spectrum(ax, spec, **kwargs)

    ax.plot(spec.wave, spec.refl, c=spec._color, label=spec.name)

    if spec.refl_err is not None:
        if not isinstance(spec.refl_err, np.ndarray):
            raise TypeError(
                f"The 'refl_err' attribute is of type {type(spec.refl_err)}, expected np.ndarray."
            )
        ax.fill_between(
            spec.wave,
            spec.refl + spec.refl_err / 2,
            spec.refl - spec.refl_err / 2,
            color=spec._color,
            alpha=0.3,
            ec="none",
        )

    ax.set(xlabel=r"Wavelength / µm", ylabel="Reflectance")
    ax.legend(ncols=4, frameon=False)


def plot_gaia_spectrum(ax, spec, **kwargs):
    """Plot a Gaia spectrum.

    Parameters
    ----------
    ax : matplotlib.axes.Axis
        The axis to plot to.
    spec : classy.spectra.Spectrum
        The Gaia spectrum to plot.
    """

    # Line to guide the eye
    ax.plot(spec.wave, spec.refl, ls=":", lw=1, c="black", zorder=100, label=spec.name)

    refl_err = np.array([0] * len(spec)) if spec.refl_err is None else spec.refl_err

    # Errorbars colour-coded by photometric flag
    props = dict(lw=1, capsize=3, ls="", zorder=100)
    props.update(kwargs)

    ax.errorbar(spec.wave, spec.refl, yerr=refl_err, c="black", **props)

    f1 = spec.flag == 1
    f2 = spec.flag == 2

    if any(f1):
        ax.errorbar(
            spec.wave[f1], spec.refl[f1], yerr=refl_err[f1], c="orange", **props
        )

    if any(f2):
        ax.errorbar(spec.wave[f2], spec.refl[f2], yerr=refl_err[f2], c="red", **props)


def _plot_taxonomy_mahlke(ax, spectra):
    """Add histogram of most probable classes following Mahlke+ 2022."""
    width = 0.8 / len(spectra)

    for i, spec in enumerate(spectra):
        # Was the spectrum classified following Mahlke+ 2022?
        if not hasattr(spec, "class_A"):
            continue

        for x, class_ in enumerate(classy.taxonomies.mahlke.defs.CLASSES):
            ax.bar(
                x - 0.3 + i * width if len(spectra) > 1 else x,
                getattr(spec, f"class_{class_}"),
                fill=True,
                color=spec._color,
                width=width,
                alpha=0.7,
                label=f"{spec.name if hasattr(spec, 'name') else ''}: {spec.class_}"
                if x == 0
                else None,
            )

    ax.set_xticks(
        [i for i, _ in enumerate(classy.taxonomies.mahlke.defs.CLASSES)],
        classy.taxonomies.mahlke.defs.CLASSES,
    )

    ax.set(ylim=(0, 1))
    ax.legend(title="Most Likely Class", frameon=True, edgecolor="none")
    ax.grid(c="gray", alpha=0.4, zorder=-100)


def _plot_taxonomy_demeo(ax, spectra):
    taxonomies.demeo.plot_pc_space(ax, spectra)


def _plot_taxonomy_tholen(ax, spectra):
    taxonomies.tholen.plot_pc_space(ax, spectra)


def _plot_albedo(ax, spectra):
    """Add albedo of spectra on inset-axis."""

    ax_alb = ax.inset_axes([0.05, 0.95, 0.2, 0.05])

    for spec in spectra:
        if not hasattr(spec, "target"):
            continue

        ax_alb.plot([spec.target.albedo.value], [0], color=spec._color, marker="x")

    ax_alb.set(xlabel="Albedo")
    ax_alb.set_yticks([], [])


# def current_plot_spectra(spectra, taxonomy=None, save=None, templates=None):
#     """Plot spectra. Called by 'classy spectra [id]'.
#
#     Parameters
#     ----------
#     spectra : list of classy.spectra.Spectrum
#         The spectra to plot.
#     taxonomy : str
#         The taxonomic system to plot. Choose from ['mahlke', 'demeo', 'tholen'].
#         Default is None, in which case no classification results are added.
#     save : str
#         Path to save the figure under. Default is None, which opens the
#         plot instead of saving it.
#     """
#
#     # Give user some degree of freedom in taxonomy specification
#     if taxonomy is not None:
#         if taxonomy.lower() not in classy.taxonomies.SYSTEMS:
#             raise ValueError(
#                 f"Unknown taxonomy '{taxonomy}'. Choose from {classy.taxonomies.SYSTEMS}."
#             )
#
#     # Ensure uniform plot appearance
#     mpl.rcParams.update(mpl.rcParamsDefault)
#
#     # Add color information to spectrum
#     colors = get_colors(len(spectra), cmap="jet")
#     lines, labels = [], []  # for the global legend
#
#     # Build figure instance
#     if taxonomy is not None:
#         fig, axes = plt.subplots(
#             ncols=3, figsize=(16, 7), gridspec_kw={"width_ratios": [4, 1, 4]}
#         )
#         ax_spec, ax_pv, ax_classes = axes
#     else:
#         fig, ax_spec = plt.subplots(figsize=(10, 7))
#
#     # 1. Plot spectra, grouped by source
#     _sources = sorted(set(spec.source for spec in spectra))
#
#     for source in _sources:
#         lines_source, labels_source = [], []
#         for spec in spectra:
#             if spec.source != source:
#                 continue
#             if taxonomy == "mahlke" and spec.source != "Gaia":
#                 # spec.wave_plot = spec._wave_pre_norm
#                 # spec.refl_plot = spec._refl_pre_norm
#                 spec._wave_preprocessed = spec._wave_pre_norm
#                 spec._refl_preprocessed = spec._refl_pre_norm
#             if not hasattr(spec, "wave_plot"):
#                 spec.wave_plot = spec.wave
#                 spec.refl_plot = spec.refl
#
#             spec._color = colors.pop() if source != "Gaia" else "black"
#
#             if source == "Gaia":
#                 user_line, user_label = plot_gaia_spectrum(ax_spec, spec)
#             else:
#                 user_line, user_label = plot_user_spectrum(ax_spec, spec)
#
#             for line, label in zip(user_line, user_label):
#                 lines_source.append(line)
#                 labels_source.append(label)
#
#         (dummy,) = ax_spec.plot([], [], alpha=0)
#         lines += [dummy, dummy] + lines_source
#         labels += ["", source] + labels_source
#
#     # (dummy,) = ax_spec.plot([], [], alpha=0)
#     # (l1,) = ax_spec.plot([], [], ls="-", c="black", lw=1)
#     # (l2,) = ax_spec.plot([], [], ls="-", c="black", alpha=0.3, lw=3)
#     # lines += [dummy, l1, l2]
#     # labels += ["", "Reflectance", "Uncertainty"]
#
#     if taxonomy is not None:
#         (l3,) = ax_spec.plot([], [], ls=":", c="gray")
#         lines += [dummy, l3]
#         labels += ["", "Taxonomy Limits"]
#
#     if templates is not None:
#         plot_class_templates(ax_spec, taxonomy, templates)
#         if taxonomy is None or taxonomy == "mahlke":
#             scheme = "Mahlke+ 2022"
#         elif taxonomy == "bus":
#             scheme = "Bus and Binzel 2002"
#         elif taxonomy == "tholen":
#             scheme = "Tholen 1984"
#         elif taxonomy == "demeo":
#             scheme = "DeMeo+ 2009"
#         (l3,) = ax_spec.plot([], [], ls=(1, (1, 7)), alpha=0.3, c="gray")
#         lines += [dummy, dummy, l3]
#         labels += ["", "Class Templates", f"Complex {templates} - {scheme}"]
#
#     leg = ax_spec.legend(
#         lines,
#         labels,
#         edgecolor="none",
#         # ncols=4,
#         # loc="upper center",
#         # loc="lower left",
#         loc="center right",
#         # bbox_to_anchor=(0.5, 1.3),
#         fontsize=8,
#     )
#     ax_spec.add_artist(leg)
#
#     if taxonomy is not None:
#         wave = getattr(taxonomies, taxonomy).WAVE
#         lower, upper = min(wave), max(wave)
#         ax_spec.axvline(lower, ls=":", zorder=-10, c="gray")
#         ax_spec.axvline(upper, ls=":", zorder=-10, c="gray")
#
#     # ensure that there is space for the legend by adding empty space
#     xmin, xmax = ax_spec.get_xlim()
#     xmax += 1 / 2.8 * (xmax - xmin)
#
#     ymin, ymax = ax_spec.get_ylim()
#     if ymax - ymin < 0.1:
#         ymin -= 0.05
#         ymax += 0.05
#
#     ax_spec.set(
#         xlabel=r"Wavelength / µm",
#         ylabel="Reflectance",
#         xlim=(xmin, xmax),
#         ylim=(ymin, ymax),
#     )
#
#     # 2. Add pV axis
#     if taxonomy is not None:
#         for i, spec in enumerate(spectra):
#             ax_pv.errorbar(
#                 i, spec.pV, yerr=spec.pV_err, capsize=3, marker=".", c=spec._color
#             )
#
#         ticklabels = [
#             spec.shortbib if hasattr(spec, "shortbib") else "" for spec in spectra
#         ]
#         ax_pv.set_xticks(range(len(spectra)), ticklabels, rotation=90)
#
#         ymin, ymax = ax_pv.get_ylim()
#         ymin = 0 if ymin < 0.1 else ymin
#         ymax += 0.051
#
#         ax_pv.set(xlabel="pV", ylim=(ymin, ymax), xlim=(-0.5, len(spectra) - 0.5))
#
#     # 3. Add classes
#     if taxonomy is not None:
#         if taxonomy == "mahlke":
#             width = 0.8 / len(spectra)
#
#             for i, spec in enumerate(spectra):
#                 if not hasattr(spec, "class_A"):
#                     continue  # spec was not classified following Mahlke+ 2022
#                 for x, class_ in enumerate(classy.defs.CLASSES):
#                     ax_classes.bar(
#                         x - 0.3 + i * width if len(spectra) > 1 else x,
#                         getattr(spec, f"class_{class_}"),
#                         fill=True,
#                         color=spec._color,
#                         width=width,
#                         alpha=0.7,
#                         label=f"{spec.shortbib if hasattr(spec, 'shortbib') else ''}: {spec.class_}"
#                         if x == 0
#                         else None,
#                     )
#             ax_classes.set(ylim=(0, 1))
#             ax_classes.set_xticks(
#                 [i for i, _ in enumerate(classy.defs.CLASSES)], classy.defs.CLASSES
#             )
#             ax_classes.legend(title="Most Likely Class", frameon=True, edgecolor="none")
#             ax_classes.grid(c="gray", alpha=0.4, zorder=-100)
#         elif "tholen" in taxonomy:
#             ax_classes = taxonomies.tholen.plot_pc_space(ax_classes, spectra)
#         elif "demeo" in taxonomy:
#             ax_classes = taxonomies.demeo.plot_pc_space(ax_classes, spectra)
#
#     if spec.name is not None:
#         ax_spec.set_title(f"({spec.number}) {spec.name}", loc="left", size=10)
#     if taxonomy is not None:
#         if taxonomy == "tholen":
#             taxonomy = "Tholen 1984"
#         if taxonomy == "mahlke":
#             taxonomy = "Mahlke+ 2022"
#         if taxonomy == "demeo":
#             taxonomy = "DeMeo+ 2009"
#         ax_classes.set_title(
#             f"Classification following {taxonomy}", loc="left", size=10
#         )
#
#     fig.tight_layout()
#
#     if save is None:
#         plt.show()
#     else:
#         fig.savefig(save)
#         logger.info(f"Figure stored under {save}")
#
#
# def plot_smass_spectrum(ax, spec):
#     """Plot a SMASS spectrum.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axis
#         The axis to plot to.
#     spec : classy.spectra.Spectrum
#         The SMASS spectrum to plot.
#     """
#
#     # Error-interval
#     if hasattr(spec, "refl_interp"):
#         l1 = ax.errorbar(
#             spec.wave,
#             spec.refl,
#             yerr=spec.refl_err,
#             c=spec._color,
#             alpha=0.4,
#             capsize=3,
#             ls="",
#         )
#         ax.plot(spec.wave_interp, spec.refl_interp, c=spec._color)
#
#     else:
#         # Line
#         (l1,) = ax.plot(
#             spec.wave,
#             spec.refl,
#             c=spec._color,
#             ls="-",
#             alpha=0.5,
#         )
#
#         ax.fill_between(
#             spec.wave,
#             spec.refl + spec.refl_err / 2,
#             spec.refl - spec.refl_err / 2,
#             color=spec._color,
#             alpha=0.3,
#             ec="none",
#         )
#
#     line = [l1]
#     label = [spec.shortbib]
#     return line, label
#
#
# def old_plot_gaia_spectrum(ax, spec):
#     """Plot a Gaia spectrum.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axis
#         The axis to plot to.
#     spec : classy.spectra.Spectrum
#         The Gaia spectrum to plot.
#     """
#
#     # Line to guide the eye
#     ax.plot(spec.wave_plot, spec.refl_plot, ls=":", lw=1, c=spec._color, zorder=100)
#
#     # Errorbars colour-coded by photometric flag
#     props = dict(lw=1, capsize=3, ls="", zorder=100)
#     l0 = ax.errorbar(
#         spec.wave,
#         spec.refl,
#         yerr=spec.refl_err,
#         c=spec._color,
#         **props,
#     )
#
#     lines = [l0]  # to construct Gaia-specific legend
#
#     f1 = spec.flag == 1
#     f2 = spec.flag == 2
#
#     if any(f1):
#         l1 = ax.errorbar(
#             spec.wave[f1],
#             spec.refl[f1],
#             yerr=spec.refl_err[f1],
#             c="orange",
#             **props,
#         )
#         lines.append(l1)
#
#     if any(f2):
#         l2 = ax.errorbar(
#             spec.wave[f2],
#             spec.refl[f2],
#             yerr=spec.refl_err[f2],
#             c="red",
#             **props,
#         )
#         lines.append(l2)
#
#     labels = [f"Flag {i}" for i, _ in enumerate(lines)]
#
#     if hasattr(spec, "refl_interp"):
#         (l3,) = ax.plot(
#             # classy.defs.WAVE_GRID,
#             spec.wave_interp,
#             spec.refl_interp,
#             ls="-",
#             lw=1,
#             c=spec._color,
#             zorder=100,
#         )
#     # lines.append(l3)
#
#     # Add Gaia-specific legend
#     # labels += ["Preprocessed"]
#     # leg = ax.legend(
#     #     lines,
#     #     labels,
#     #     facecolor="white",
#     #     edgecolor="none",
#     #     loc="lower center",
#     #     title="Gaia",
#     # )
#     # ax.add_artist(leg)
#     return lines, labels
#
#
# def plot_akari_spectrum(ax, spec):
#     """Plot an AKARI spectrum.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axis
#         The axis to plot to.
#     spec : classy.spectra.Spectrum
#         The Gaia spectrum to plot.
#     """
#
#     # Line to guide the eye
#     ax.plot(spec.wave, spec.refl, ls=":", lw=1, c=spec._color, zorder=100)
#
#     # Errorbars colour-coded by photometric flag
#     props = dict(lw=1, capsize=3, ls="", zorder=100)
#     l0 = ax.errorbar(
#         spec.wave[spec.flag != 1],
#         spec.refl[spec.flag != 1],
#         yerr=spec.refl_err[spec.flag != 1],
#         c=spec._color,
#         **props,
#     )
#
#     lines = [l0]  # to construct AKARI-specific legend
#
#     f1 = spec.flag == 1
#
#     if any(f1):
#         l1 = ax.errorbar(
#             spec.wave[f1],
#             spec.refl[f1],
#             yerr=spec.refl_err[f1],
#             c=spec._color,
#             **props,
#             alpha=0.3,
#         )
#         lines.append(l1)
#
#     labels = [f"Flag {i}" for i, _ in enumerate(lines)]
#
#     if hasattr(spec, "refl_interp"):
#         (l3,) = ax.plot(
#             spec.wave_interp,
#             spec.refl_interp,
#             ls="-",
#             lw=1,
#             c=spec._color,
#             zorder=100,
#         )
#     # lines.append(l3)
#
#     # Add Gaia-specific legend
#     # labels += ["Preprocessed"]
#     # leg = ax.legend(
#     #     lines,
#     #     labels,
#     #     facecolor="white",
#     #     edgecolor="none",
#     #     loc="lower center",
#     #     title="Gaia",
#     # )
#     # ax.add_artist(leg)
#     return lines, labels
#
#
# def plot_ecas_spectrum(ax, spec):
#     """Plot an ECAS spectrum.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axis
#         The axis to plot to.
#     spec : classy.spectra.Spectrum
#         The Gaia spectrum to plot.
#     """
#
#     # Line to guide the eye
#     ax.plot(spec.wave, spec.refl, ls="--", lw=1, c=spec._color, zorder=100)
#
#     # Errorbars colour-coded by photometric flag
#     props = dict(lw=1, capsize=3, ls="", zorder=100)
#
#     l0 = ax.errorbar(
#         spec.wave[spec.flag != 1],
#         spec.refl[spec.flag != 1],
#         yerr=spec.refl_err[spec.flag != 1],
#         c=spec._color,
#         **props,
#     )
#
#     lines = [l0]  # to construct AKARI-specific legend
#
#     f1 = spec.flag == 1
#
#     if any(f1):
#         l1 = ax.errorbar(
#             spec.wave[f1],
#             spec.refl[f1],
#             yerr=spec.refl_err[f1],
#             c=spec._color,
#             **props,
#             alpha=0.3,
#         )
#         lines.append(l1)
#
#     labels = [f"Flag {i}" for i, _ in enumerate(lines)]
#
#     if hasattr(spec, "refl_interp"):
#         (l3,) = ax.plot(
#             # classy.defs.WAVE_GRID,
#             spec.wave_interp,
#             spec.refl_interp,
#             ls="-",
#             lw=1,
#             c=spec._color,
#             zorder=100,
#         )
#     # lines.append(l3)
#
#     # Add Gaia-specific legend
#     # labels += ["Preprocessed"]
#     # leg = ax.legend(
#     #     lines,
#     #     labels,
#     #     facecolor="white",
#     #     edgecolor="none",
#     #     loc="lower center",
#     #     title="Gaia",
#     # )
#     # ax.add_artist(leg)
#     return lines, labels
#
#
# def plot_user_spectrum(ax, spec):
#     """Plot a user provided spectrum.
#
#     Parameters
#     ----------
#     ax : matplotlib.axes.Axis
#         The axis to plot to.
#     spec : classy.spectra.Spectrum
#         The SMASS spectrum to plot.
#     """
#
#     if spec.is_smoothed:
#         (l1,) = ax.plot(
#             spec.wave,
#             spec.refl,
#             c=spec._color,
#             ls="-",
#             alpha=1,
#         )
#         ax.plot(
#             spec._wave_original,
#             spec._refl_original,
#             c=spec._color,
#             ls="-",
#             alpha=0.3,
#         )
#
#     else:
#         # Plot original
#         if not hasattr(spec, "_refl_preprocessed"):
#             wave = spec.wave
#             refl = spec.refl
#             err = spec.refl_err
#         else:
#             wave = spec._wave_preprocessed
#             refl = spec._refl_preprocessed
#             err = np.nan
#
#         (l1,) = ax.plot(
#             wave,
#             refl,
#             c=spec._color,
#             ls="-",
#             alpha=0.5,
#         )
#
#         if err is not None:
#             ax.fill_between(
#                 wave,
#                 refl + err / 2,
#                 refl - err / 2,
#                 color=spec._color,
#                 alpha=0.3,
#                 ec="none",
#             )
#
#     line = [l1]
#
#     if hasattr(spec, "shortbib"):
#         label = spec.shortbib
#     elif hasattr(spec, "source"):
#         label = spec.source
#     else:
#         label = "User"
#     label = [label]
#     return line, label
#
#
# def plot_class_templates(ax, scheme, complex):
#     """Add class templates of taxonomic scheme to figure."""
#     if scheme is None:
#         scheme = "mahlke"
#
#     if scheme not in ["bus", "demeo", "mahlke", "tholen"]:
#         raise ValueError(f"Unknown taxonomy '{scheme}' for class templates.")
#
#     templates = getattr(taxonomies, scheme).load_templates()
#
#     for class_, spec in templates.items():
#         if class_ not in taxonomies.COMPLEXES[complex]:
#             continue
#
#         ax.plot(spec.wave, spec.refl, ls=(1, (1, 7)), alpha=0.3, c="gray", zorder=-100)
#         for w, r in zip(spec.wave[::2], spec.refl[::2]):
#             ax.text(
#                 w,
#                 r,
#                 class_,
#                 size=6,
#                 c="gray",
#                 ha="center",
#                 va="center",
#                 clip_on=True,
#                 alpha=0.5,
#             )
