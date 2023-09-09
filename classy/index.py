"""Module to manage the global spectra index in classy."""
import asyncio
import aiohttp
from datetime import datetime
import functools
import sys

import numpy as np
import pandas as pd

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
    "N",
    "wave_min",
    "wave_max",
]


@functools.cache
def load():
    """Load the global spectra index.

    Returns
    -------
    pd.DataFrame
        The global spectra index. Empty if index does not exist yet.
    """
    if not (config.PATH_CACHE / "index.csv").is_file():
        if "status" not in sys.argv and "add" not in sys.argv:
            logger.error(
                "No spectra available. Run '$ classy status' to retrieve them."
            )
        return pd.DataFrame(
            data={key: [] for key in ["name", "source", "filename", "host"]}, index=[]
        )

    index = pd.read_csv(
        config.PATH_CACHE / "index.csv",
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
    index.to_csv(config.PATH_CACHE / "index.csv", index=True, index_label="filename")


def add(entries):
    """Add entries to the global spectra index.

    Parameters
    ----------
    entries : list of pd.DataFrame
        The entries to add to the index.
    """

    # Add missing column
    entries["phase"] = np.nan

    # Convert all observation epochs to ISO-T format
    entries["date_obs"] = entries["date_obs"].apply(lambda d: convert_to_isot(d))

    # Format for adding to index
    entries = entries.loc[
        :, [c for c in COLUMNS if c not in ["N", "wave_min", "wave_max"]]
    ]

    # Add data columns
    entries = entries.set_index("filename")
    entries = sources._add_spectra_properties(entries)

    # Skip the cache of the load function as we change the index
    index = load.__wrapped__()

    # Append new entries and drop duplicate filenames
    index = index.reset_index()  # drop-duplicates does not work on index column...
    entries = entries.reset_index()

    index = pd.concat([index, entries])
    index = index.drop_duplicates(subset="filename", keep="last")
    index = index.set_index("filename")

    save(index)


def build():
    """Retrieve all public spectra that classy knows about."""
    from rich import console

    with console.Console().status("Indexing spectra...", spinner="dots8Bit"):
        for module in ["pds", "cds", "m4ast", "akari", "smass", "mithneos", "gaia"]:
            getattr(sources, module)._build_index()


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
    idx = load()

    idx["phase"] = np.nan
    idx["epoch_im"] = np.nan
    idx["sso"] = np.nan

    # Get subindex with valid observation dates
    idx_phase = idx.loc[~pd.isna(idx.date_obs)][["name", "date_obs"]]

    # Exclude those with multiple date_obs for now
    # These are done in a second loop and get an err_phase != 0
    # idx_phase = idx_phase[~idx_phase.date_obs.str.contains(",")]

    # idx_phase = idx_phase.loc[idx_phase["name"] == "Iva"]
    # idx_phase = idx_phase.loc[idx_phase["name"].isin(["Iva"])]
    # idx_phase = idx_phase.loc[idx_phase["number"] == 25]
    # idx_phase = idx_phase[:500]

    from rich.progress import Progress

    with Progress(disable=False) as progress_bar:
        progress = progress_bar.add_task(
            "Add phase", total=len(idx_phase.groupby("name"))
        )

        # Run async loop to get ssoCard
        loop = get_or_create_eventloop()
        phases = loop.run_until_complete(
            _get_datacloud_catalogue(idx_phase, progress_bar, progress)
        )

    # for entry in phases[0]:
    # entry = list(entry)[0]
    # index, phase, err_phase, epoch_im = entry
    # for result in phases:
    for index, phase, err_phase in phases:
        # print(index, phase)
        idx.loc[index, "phase"] = phase
        idx.loc[index, "err_phase"] = err_phase
        # idx.loc[index, "epoch_im"] = epoch_im
        # print(index, phase, idx.loc[index, "date_obs"], epoch_im)
        # idx.loc[index, "sso_im"] = sso_im

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
            phase, _ = await _get_phase_angle(name, epoch, session)
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

    for format in FORMATS:
        try:
            date_obs = ",".join(
                [datetime.strptime(date, format).isoformat(sep="T") for date in dates]
            )
        except ValueError:
            continue
        else:
            break
    else:
        raise ValueError(f"Unknown time format: {dates}. Expected ISO-T.")

    return date_obs


def load_smoothing():
    """Load the feature index."""
    if not (config.PATH_CACHE / "smoothing.csv").is_file():
        return pd.DataFrame()
    return pd.read_csv(
        config.PATH_CACHE / "smoothing.csv",
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
        config.PATH_CACHE / "smoothing.csv", index=True, index_label="filename"
    )


def store_features(features):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        features["number"] = features["number"].astype("Int64")
    features.to_csv(config.PATH_CACHE / "features.csv", index=True)


def load_features():
    """Load the feature index."""
    if not (config.PATH_CACHE / "features.csv").is_file():
        # Creating indices
        ind = pd.MultiIndex(
            levels=[[], []], codes=[[], []], names=["filename", "feature"]
        )
        return pd.DataFrame(index=ind)
    return pd.read_csv(
        config.PATH_CACHE / "features.csv", index_col=["filename", "feature"]
    )
