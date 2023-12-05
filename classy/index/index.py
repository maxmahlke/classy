"""Module to manage the global spectra index in classy."""
import re
import asyncio
import aiohttp
from datetime import datetime
import sys

import numpy as np
import pandas as pd
import rocks

from classy import config
from classy.log import logger
from classy import sources

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


# @functools.cache
def load():
    """Load the global spectra index.

    Returns
    -------
    pd.DataFrame
        The global spectra index. Empty if index does not exist yet.
    """
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
    entries["date_obs"] = entries["date_obs"].apply(lambda d: convert_to_isot(d))

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
    MODULES = ["cds", "pds", "m4ast", "akari", "smass", "mithneos", "gaia"]
    DESCS = {
        "cds": f"[dim]{'[93] CDS':>22}[/dim]",
        "pds": f"[dim]{'[3369] PDS':>22}[/dim]",
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
            pbar.update(tasks[module], start=True)
            getattr(sources, module)._build_index()
            pbar.update(tasks[module], visible=False)

            # Update overall bar
            pbar.update(overall_progress_task, completed=i + 1)

        pbar.update(
            overall_progress_task,
            completed=len(MODULES),
            total=len(MODULES),
            description=f"{'All done!':>22}",
        )


# ------
# Asynch phase angle query
def get_or_create_eventloop():
    """Enable asyncio to get the event loop in a thread other than the main thread

    Returns
    --------
    out: asyncio.unix_events._UnixSelectorEventLoop
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


def batch_phase():
    # might have changed during runtime
    idx = load()  # .__wrapped__()

    # Get subindex with valid observation dates
    idx_phase = idx.loc[~pd.isna(idx.date_obs)][["name", "date_obs"]]

    from rich.progress import Progress

    with Progress(disable=False) as progress_bar:
        progress = progress_bar.add_task(
            f"Querying Miriade for {len(idx_phase.groupby('name'))} asteroids",
            total=len(idx_phase.groupby("name")),
        )

        # Run async loop to get ssoCard
        loop = get_or_create_eventloop()
        phases = loop.run_until_complete(
            _get_datacloud_catalogue(idx_phase, progress_bar, progress)
        )

    for index, phase, err_phase in phases:
        idx.loc[index, "phase"] = phase
        idx.loc[index, "err_phase"] = err_phase

    save(idx)


async def _get_datacloud_catalogue(idx_phase, progress_bar, progress):
    """Get catalogue asynchronously. First attempt local lookup, then query SsODNet.

    Parameters
    ----------
    id_catalogue : list
        Asteroid - catalogue combinations.
    progress : bool or tdqm.std.tqdm
        If progress is True, this is a progress bar instance. Else, it's False.
    local : bool
        If False, forces the remote query of the ssoCard. Default is True.

    Returns
    -------
    list of dict
        list containing len(id_) list with dictionaries corresponding to the
    catalogues of the passed identifiers. If the catalogue is not available, the dict
    is empty.
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
        tasks = [
            asyncio.ensure_future(
                _local_or_remote_catalogue(ind, obs, session, progress_bar, progress)
            )
            # for name, obs in idx_phase.groupby("name")
            for ind, obs in idx_phase.iterrows()
        ]

        results = await asyncio.gather(*tasks)
    return results


sema = asyncio.Semaphore(50)
# lock = asyncio.Lock()


async def _local_or_remote_catalogue(index, obs, session, progress_bar, progress):
    """Check for presence of ssoCard in cache directory. Else, query from SsODNet."""
    # print(obs)

    # epochs = obs.date_obs.values
    epoch = obs.date_obs
    epochs = epoch.split(",")
    name = obs["name"]
    # index = obs.index

    # Handle multi-epoch spectra by recording number of epochs per spectrum
    # n_epochs = [len(epoch.split(",")) for epoch in epochs]
    # epochs = [epoch.split(",") for epoch in epochs]
    # epochs = [e for epoch in epochs for e in epoch]

    async with sema:
        phases = []
        for epoch in epochs:
            try:
                phase, _ = await _get_phase_angle(name, epoch, session)
            except aiohttp.client_exceptions.ClientConnectorError:
                logger.error(
                    "The Miriade query for one asteroid-epoch pair failed. The corresponding phase is set to NaN."
                )
                phase = np.nan
            phases.append(phase)
        # phases, epoch_im = await _get_phase_angle(name, epochs, session)

    # print(list(zip(epochs, epoch_im)))

    # Average multi-epoch spectra
    # from itertools import islice
    #
    # res = [
    #     list(islice(phases, sum(n_epochs[:i]), sum(n_epochs[:i]) + ele))
    #     for i, ele in enumerate(n_epochs)
    # ]
    #
    # print(phases)
    # breakpoint()
    # print(list(zip(index, phases, epoch_im)))
    # phases = [np.mean(r) for r in res]
    # err_phases = [np.std(r) for r in res]

    # err_phases = phases
    phase = np.mean(phases)
    err_phase = np.std(phases)
    #
    progress_bar.update(progress, advance=1)
    return index, phase, err_phase


async def _get_phase_angle(name, epochs, session):
    """Query quaero and parse result for a single object.

    Parameters
    ----------
    id_ssodnet : str
        Asteroid ID from SsODNet.
    catalogue : str
        Datacloud catalogue name.
    session : aiohttp.ClientSession
        asyncio session

    Returns
    -------
    dict
        SsODNet response as dict if successful. Empty if query failed.
    """
    # Pass sorted list of epochs to speed up query

    # ------
    # Query Miriade for phase angles
    URL = "http://vo.imcce.fr/webservices/miriade/ephemcc_query.php"

    params = {
        "-name": f"a:{name}",
        "-mime": "json",
        "-tcoor": "5",
        "-tscale": "UTC",
        "-ep": epochs,
    }

    # print(params)
    # epochs = {"epochs": io.StringIO("\n".join(epochs))}
    # epochs_file = {"epochs": str.encode("\n".join(epochs))}
    # async with session.post(url=URL, params=params, data=epochs_file) as response:
    async with session.post(url=URL, params=params) as response:
        response_json = await response.json()
    # response = await

    # if not response.ok:
    #     return {"data": {"phase": np.nan}}, ""

    # response_json = await response.json()
    phase = [data["phase"] for data in response_json["data"]]
    # print(phase)
    epoch_im = [data["epoch"][:-3] for data in response_json["data"]]
    # if any(ep_im not in epochs for ep_im in epoch_im):
    #     print(list(zip(epochs, epoch_im)))
    #     breakpoint()
    # # sso = response_json["sso"]["name"]
    return phase, epoch_im  # , sso


def convert_to_isot(dates):
    """Convert list of dates to ISOT format.

    Parameters
    ----------
    dates : str or list of str
        The dates to convert.
    format : str
        The current format string of the dates.
    """
    if pd.isna(dates) or not dates:
        return ""

    if isinstance(dates, str):
        dates = dates.split(",")

    FORMATS = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y/%m/%d_%H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]

    converted = []

    for date in dates:
        for format in FORMATS:
            try:
                date = datetime.strptime(date, format).isoformat(sep="T")
                converted.append(date)
            except ValueError:
                continue
            else:
                break
        else:
            raise ValueError(f"Unknown time format: {dates}. Expected ISO-T.")
    date_obs = ",".join(converted)
    return date_obs


def load_smoothing():
    """Load the feature index."""
    if not (config.PATH_DATA / "smoothing.csv").is_file():
        return pd.DataFrame()
    return pd.read_csv(
        config.PATH_DATA / "smoothing.csv",
        index_col="filename",
        dtype={
            "deg_savgol": int,
            "deg_spline": int,
            "window_savgol": int,
        },
    )


def store_smoothing(smoothing):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        smoothing["number"] = smoothing["number"].astype("Int64")
    smoothing.to_csv(
        config.PATH_DATA / "smoothing.csv", index=True, index_label="filename"
    )


def store_features(features):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        features["number"] = features["number"].astype("Int64")
    features.to_csv(config.PATH_DATA / "features.csv", index=True)


def load_features():
    """Load the feature index."""
    if not (config.PATH_DATA / "features.csv").is_file():
        # Creating indices
        ind = pd.MultiIndex(
            levels=[[], []],
            codes=[[], []],
            names=["filename", "feature"],
            columns=["is_present"],
        )
        return pd.DataFrame(index=ind)
    return pd.read_csv(
        config.PATH_DATA / "features.csv",
        index_col=["filename", "feature"],
        dtype={"is_present": bool},
    )


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

    if cols_bft:
        bft = rocks.load_bft(columns=cols_bft + ["sso_name"])
        bft = bft.rename(columns={v: k for k, v in BFT_SHORT.items()})
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

                    if any(_is_int_or_float(limit) for limit in [lower, upper]):
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
        ftrs = kwargs["feature"].split(",")

        # Only feature entries of spectra we care about
        features = load_features()
        features = features.reset_index(level=1)
        features = features.loc[features.index.isin(idx.index)]

        # Only feature entries of feature we care about
        features = features.loc[features.feature.isin(ftrs)]
        features = features[features.is_present]

        idx = idx.loc[idx.index.isin(features.index)]

    return idx.copy()  # return copy to fix SettingWithCopyWarning


def _is_int_or_float(number):
    """Like isnumeric() for str but supports float."""
    try:
        float(number)
        return True
    except ValueError:
        return False


BFT_SHORT = {
    "albedo": "albedo.value",
    "diameter": "diameter.value",
    "family": "family.family_name",
    "H": "absolute_magnitude.value",
    "taxonomy": "taxonomy.class",
}