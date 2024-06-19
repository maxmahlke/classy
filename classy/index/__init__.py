import re
import sys

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import features
from classy import sources
from classy import utils
from classy.utils.logging import logger

from . import data, phase  # noqa

COLUMNS = [
    "name",
    "number",
    "filename",
    "shortbib",
    "date_obs",
    "bibcode",
    "host",
    "module",
    "source",
    "phase",
    "err_phase",
    "N",
    "wave_min",
    "wave_max",
]

BFT_SHORT = {
    "albedo": "albedo.value",
    "diameter": "diameter.value",
    "family": "family.family_name",
    "H": "absolute_magnitude.value",
    "taxonomy": "taxonomy.class",
}


def load():
    """Load the global spectra index.

    Returns
    -------
    pd.DataFrame
        The global spectra index. Empty if index does not exist yet.
    """

    # In APP mode, we always want the added bft to avoid rocks queries
    if config.APP_MODE:
        idx = pd.read_parquet(
            config.PATH_DATA / "idx_extended.parquet",
        )
        idx = idx.set_index("filename")
        idx = idx.rename(columns={v: k for k, v in BFT_SHORT.items()})
        return idx

    if not (config.PATH_DATA / "index.csv").is_file():
        if "status" not in sys.argv and "add" not in sys.argv:
            logger.error(
                "No spectra available. Run '$ classy status' to retrieve them."
            )
        return pd.DataFrame(
            data={key: [] for key in ["name", "source", "filename", "host"]}, index=[]
        )

    index = pd.read_csv(
        config.PATH_DATA / "index.csv",
        dtype={"number": "Int64"},
        low_memory=False,
        index_col="filename",
    )
    return index


def query(id=None, **kwargs):
    """Query the index for spectra fitting selection criteria.

    Parameters
    ----------
    id : list of str or int
        List of asteroid identifiers. Optional, default is None.

    Returns
    -------
    pd.DataFrame
        Subset of the classy index fitting the selection criteria.
    """

    # Convert id to query criterion if provided
    if id is not None:
        if not isinstance(id, (list, tuple)):
            id = [id]

        id = [rocks.id(i)[0] for i in id if i is not None]

        if "name" in kwargs:
            logger.warning(
                "Specifying asteroid identifiers overrides the passed 'name' selection."
            )

        kwargs["name"] = id

    idx = load()
    idx["filename"] = idx.index.values  # ensure that filename is searchable as well

    # Separate requested columns into domains
    cols_bft = []
    cols_query = []

    # Get column names from query argument
    if "query" in kwargs:
        cols_query = re.findall(r"[A-Za-z0-9._-]*", kwargs["query"])
        bft_valid_cols = rocks.load_bft(
            full=True, filters=[("sso_name", "==", "")]
        ).columns

        # Ensure valid column names and translate shortforms
        cols_query = [BFT_SHORT[c] if c in BFT_SHORT else c for c in cols_query]
        cols_query = [c for c in cols_query if c in bft_valid_cols or c in idx.columns]

    for col in list(kwargs) + cols_query:
        if col in ["feature", "query"] or col in idx.columns:
            continue
        else:
            if col in BFT_SHORT:
                col = BFT_SHORT[col]
            cols_bft.append(col)

    if cols_bft and not config.APP_MODE:
        bft = rocks.load_bft(columns=cols_bft + ["sso_name"])
        bft = bft.rename(columns={v: k for k, v in BFT_SHORT.items()})

        if "filename" in idx.columns:
            idx.drop(columns=["filename"], inplace=True)

        idx = idx.reset_index(names="filename")
        idx = idx.merge(bft, left_on="name", right_on="sso_name")
        idx = idx.set_index("filename")
        idx = idx.drop(columns=["sso_name"])

    # Filter based on passed selection criteria
    for column, value in kwargs.items():
        if column not in idx.columns.tolist() + ["query", "feature"]:
            raise KeyError(
                f"Unknown index column '{column}'. Choose from {idx.columns.tolist()}."
            )
        if column == "feature":
            continue

        # Special cases: wave_min, wave_max, query
        #
        # Apply wave_min and wave_max as bounds rather than equals
        if column == "wave_min":
            idx = idx.loc[idx[column] <= float(value)]
        elif column == "wave_max":
            idx = idx.loc[idx[column] >= float(value)]
        # Pass query string directly
        elif column == "query":
            # dots in columns have to be escaped
            for col in bft_valid_cols:
                value = value.replace(col, f"`{col}`")
            idx = idx.query(value)
        else:
            # All other cases: first check for comma-split
            if isinstance(value, str):
                value = value.split(",")

                # Numeric or categorical comparison? Numeric
                # forcibly only has two values
                if len(value) == 2:
                    lower, upper = value

                    if column == "date_obs":
                        if lower:
                            idx = idx.loc[idx[column] >= str(lower)]
                        if upper:
                            idx = idx.loc[idx[column] <= str(upper)]
                        continue

                    if any(utils._is_int_or_float(limit) for limit in [lower, upper]):
                        if lower:
                            idx = idx.loc[idx[column] >= float(lower)]
                        if upper:
                            idx = idx.loc[idx[column] <= float(upper)]
                        continue

            # Categorical value: Apply as "is-in"
            if not isinstance(value, (list, tuple)):
                value = [value]

            idx = idx.loc[idx[column].isin(value)]

    if "feature" in kwargs:
        # Only feature entries of spectra we care about
        ftrs = features.load()
        ftrs = ftrs.reset_index(level=1)
        ftrs = ftrs.loc[ftrs.index.isin(idx.index)]

        # Only feature entries of feature we care about
        ftrs = ftrs.loc[ftrs.feature.isin(kwargs["feature"].split(","))]
        ftrs = ftrs[ftrs.is_present]

        idx = idx.loc[idx.index.isin(ftrs.index)]

    return idx.copy()  # return copy to fix SettingWithCopyWarning


def save(index):
    """Save the global spectra index."""

    with np.errstate(invalid="ignore"):
        index["number"] = index["number"].astype("Int64")
        index["N"] = index["N"].astype(int)
    index.to_csv(config.PATH_DATA / "index.csv", index=True, index_label="filename")


def add(entries):
    """Add entries to the global spectra index.

    Parameters
    ----------
    entries : list of pd.DataFrame
        The entries to add to the index.
    """

    # Add missing column
    entries["phase"] = np.nan
    entries["err_phase"] = np.nan

    # Convert all observation epochs to ISO-T format
    entries["date_obs"] = entries["date_obs"].apply(lambda d: utils.convert_to_isot(d))

    # Add data columns
    entries = entries.set_index("filename")

    if not entries.module.values[0] == "gaia":
        entries = sources._add_spectra_properties(entries)
    # else:
    #     breakpoint()

    # Skip the cache of the load function as we change the index
    index = load()  # .__wrapped__()

    # Append new entries and drop duplicate filenames
    index = index.reset_index()  # drop-duplicates does not work index
    entries = entries.reset_index()

    # Format for adding to index
    entries = entries[COLUMNS]
    index = pd.concat([index, entries])
    index = index.drop_duplicates(subset="filename", keep="last").set_index("filename")

    save(index)


def build():
    """Retrieve all public spectra that classy knows about."""
    from rich import progress

    # ------
    # Retrieve index while showing spinner
    MODULES = ["cds", "pds", "m4ast", "akari", "smass", "manos", "mithneos", "gaia"]
    DESCS = {
        "cds": f"[dim]{'[93] CDS':>22}[/dim]",
        "pds": f"[dim]{'[3369] PDS':>22}[/dim]",
        "manos": f"[dim]{'[197] MANOS':>22}[/dim]",
        "m4ast": f"[dim]{'[123] M4AST':>22}[/dim]",
        "akari": f"[dim]{'[64] AKARI':>22}[/dim]",
        "smass": f"[dim]{'[1911] SMASS':>22}[/dim]",
        "mithneos": f"[dim]{'[2256] MITHNEOS':>22}[/dim]",
        "gaia": f"[dim]{'[60518] Gaia':>22}[/dim]",
    }

    with progress.Progress(
        "[progress.description]{task.description}",
        progress.BarColumn(),
    ) as pbar:
        overall_progress_task = pbar.add_task(
            f"{'Indexing Spectra...':>22}", total=len(MODULES)
        )
        tasks = {}

        for module in MODULES:
            tasks[module] = pbar.add_task(
                DESCS[module], visible=True, start=False, total=None
            )

        for i, module in enumerate(MODULES):
            try:
                getattr(sources, module)._build_index()
            except FileNotFoundError:
                pass
            pbar.update(tasks[module], visible=False)

            # Update overall bar
            pbar.update(overall_progress_task, completed=i + 1)

        pbar.update(
            overall_progress_task,
            completed=len(MODULES),
            total=len(MODULES),
            description=f"{'All done!':>22}",
        )
