import numpy as np
import pandas as pd

from classy import config
from classy import core
from classy import sources

from . import akari, cds, gaia, m4ast, manos, mithneos, pds, private, smass

SOURCES = [
    "24CAS",
    "52CAS",
    "AKARI",
    "CDS",
    "ECAS",
    "Gaia",
    "M4AST",
    "MANOS",
    "MITHNEOS",
    "Misc",
    "PRIMASS",
    "S3OS2",
    "SCAS",
    "SMASS",
]


def _retrieve_spectra():
    """Retrieve all public spectra that classy knows about."""
    from rich import progress

    # TODO: Add proper progress per source by passing tasks
    MODULES = [cds, pds, m4ast, akari, smass, manos, mithneos, gaia]

    DESCS = {
        cds: f"[dim]{'[93] CDS':>22}[/dim]",
        pds: f"[dim]{'[3369] PDS':>22}[/dim]",
        manos: f"[dim]{'[197] MANOS':>22}[/dim]",
        m4ast: f"[dim]{'[123] M4AST':>22}[/dim]",
        akari: f"[dim]{'[64] AKARI':>22}[/dim]",
        smass: f"[dim]{'[1911] SMASS':>22}[/dim]",
        mithneos: f"[dim]{'[2256] MITHNEOS':>22}[/dim]",
        gaia: f"[dim]{'[60518] Gaia':>22}[/dim]",
    }

    with progress.Progress(
        "[progress.description]{task.description}",
        progress.BarColumn(),
        transient=True,
        disable=False,
    ) as pbar:
        overall = pbar.add_task("Downloading Spectra...", total=len(MODULES))

        tasks = {}

        for i, module in enumerate(MODULES):
            tasks[module] = pbar.add_task(DESCS[module], visible=True, total=None)
            module._retrieve_spectra()
            pbar.update(tasks[module], total=1)
            pbar.advance(tasks[module])

            # Update overall bar
            pbar.update(overall, completed=i + 1)

        pbar.update(
            overall,
            completed=len(MODULES),
            total=len(MODULES),
        )


def load_data(idx):
    """Load data and metadata of a cached spectrum.

    Parameters
    ----------
    idx : pd.Series
        A row from the classy spectra index.

    Returns
    -------
    pd.DataFrame, dict
        The data and metadata. List-like attributes are in the dataframe,
        single-value attributes in the dictionary.
    """

    host = (
        getattr(sources, idx.host.lower())
        if idx.host.lower() in ["pds", "cds"]
        else sources
    )
    module = getattr(host, idx.module.lower())

    # Load spectrum data file
    PATH_DATA = config.PATH_DATA / idx.name

    if module is private:
        data = _load_private_data(PATH_DATA)
    elif module is gaia:
        data = gaia._load_virtual_file(idx)
    else:
        data = pd.read_csv(PATH_DATA, **module.DATA_KWARGS)

    # Remove invalid data points
    data = data[data.wave > 0]
    data = data[data.refl > 0]

    # Apply module specific data transforms and get metadata if necessary
    if hasattr(module, "_transform_data"):
        data, meta = module._transform_data(idx, data)
    else:
        meta = {}

    return data, meta


def _load_private_data(PATH):
    # Try two different delimiters
    try:
        data = np.loadtxt(PATH)
    except ValueError:
        data = np.loadtxt(PATH, delimiter=",")

    data = pd.DataFrame(data)

    # Rename the columns that are present
    COLS = ["wave", "refl", "refl_err", "flag"]
    data = data.rename(columns={col: COLS.pop(0) for col in data.columns})
    return data


def load_spectrum(idx, skip_target):
    """Load a cached spectrum. This general function applies host- and
    collection specific parameters defined in the collection modules.

    Parameters
    ----------
    idx : pd.Series
        A row from the classy spectra index.

    Returns
    -------
    classy.Spectrum
        The requested spectrum.
    """

    # Load data and metadata
    data, meta = load_data(idx)

    # Add list-type attributes when instantiating
    spec = core.Spectrum(
        target=idx["name"] if not skip_target else None,
        **{col: data[col].values for col in data.columns},
    )

    # Add metadata from index
    for attr in ["shortbib", "bibcode", "host", "source", "date_obs"]:
        setattr(spec, attr, idx[attr])

    if "phase" in idx:
        setattr(spec, "phase", idx["phase"])

    spec.filename = idx.name

    # Add collection-specific metadata
    for attr, value in meta.items():
        setattr(spec, attr, value)
    return spec


def _add_spectra_properties(entries):
    """Add the spectral range properties to a dataframe of index entries."""
    for ind, entry in entries.iterrows():
        data, _ = load_data(entry)
        entries.loc[ind, "wave_min"] = min(data["wave"])
        entries.loc[ind, "wave_max"] = max(data["wave"])
        entries.loc[ind, "N"] = len(data)

    return entries
