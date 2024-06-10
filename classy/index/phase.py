import aiohttp
import asyncio
import warnings

import numpy as np
import pandas as pd
import requests

from classy import index
from classy import utils
from classy.utils.logging import logger


def add_phase_to_index():
    """Add phase angle information to classy index by quering the Miriade service."""

    # Get subindex with valid observation dates
    idx = index.load()
    idx_phase = idx.loc[~pd.isna(idx.date_obs)][["name", "date_obs"]]

    # Run async loop to get phase info while displaying progress
    with utils.progress.mofn as mofn:
        print("")
        task = mofn.add_task("Querying Miriade", total=len(idx_phase))

        loop = get_or_create_eventloop()
        phases = loop.run_until_complete(_run_async_loop(idx_phase, mofn, task))

    # Store results in index
    for i, phase, err_phase in phases:
        idx.loc[i, "phase"] = phase
        idx.loc[i, "err_phase"] = err_phase

    index.save(idx)


async def _run_async_loop(idx_phase, mofn, progress):
    """Run the asyncronous phase-query event loop.

    Parameters
    ----------
    idx_phase : pd.DataFrame
        Subset of classy index that contains date_obs information.
    mofn : rich.progress.Progress
        Progress bar instance showing progress.
    task : progress task
        Progress task ID for external updates.

    Returns
    -------
    list of [idx_phase, phase, err_phase]
    """
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(sock_connect=10)
    ) as session:
        tasks = [
            asyncio.ensure_future(
                _get_phase_asyncronous(ind, obs, session, mofn, progress)
            )
            # NOTE: Grouping by asteroid and sending multiple epochs not possible with async framework
            for ind, obs in idx_phase.iterrows()
        ]
        results = await asyncio.gather(*tasks)
    return results


async def _get_phase_asyncronous(idx, obs, session, mofn, progress):
    """Get phase angle asynchronously from Miriade.

    Parameters
    ----------
    idx : float
        Index number from classy index referring to this spectrum.
    obs : pd.Series
        Row from classy index containing one asteroid and one or more epochs.
    session : aiohttp.ClientSession
        The ongoing http session.
    mofn : rich.progress.Progress
        Progress bar instance showing progress.
    task : progress task
        Progress task ID for external updates.

    Returns
    -------
    idx, float, float
        The unchanged obervation index and the corresponding phase and uncertainty.
    """

    # There might be more than one epochs
    epoch = obs.date_obs
    epochs = epoch.split(",")

    # Limit number of simultaneous queries
    async with asyncio.Semaphore(50):
        phases = []
        for epoch in epochs:
            try:
                phase = await _get_phase_angle(obs["name"], epoch, session)
            except (
                aiohttp.client_exceptions.ClientConnectorError,
                aiohttp.client_exceptions.ContentTypeError,
                aiohttp.client_exceptions.ServerTimeoutError,
                KeyError,
            ):
                logger.error(
                    f"The following Miriade query failed (phase is set to NaN): {obs['name']} - {epoch}"
                )
                phase = np.nan
            phases.append(phase)

    mofn.update(progress, advance=1)

    with warnings.catch_warnings():  # hides warnings if phase = [np.nan]
        warnings.simplefilter("ignore")
        return idx, np.nanmean(phases), np.nanstd(phases)


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
    URL = "http://ssp.imcce.fr/webservices/miriade/api/ephemcc.php"

    params = {
        "-name": f"a:{name}",
        "-mime": "json",
        "-tcoor": "5",
        "-tscale": "UTC",
        "-ep": epochs,
    }

    async with session.post(url=URL, params=params) as response:
        response_json = await response.json()

    return response_json["data"][0]["Phase"]


def get_or_create_eventloop():
    """Enable asyncio to get the event loop in a thread other than the main thread

    Returns
    --------
    asyncio.unix_events._UnixSelectorEventLoop
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


def query_miriade_syncronously(name, epochs):
    """Gets asteroid ephemerides from IMCCE Miriade.

    Parameters
    ----------
    name : str
        Name or designation of asteroid.
    epochs : list
        List of observation epochs in iso format.

    Returns
    -------
    :returns: pd.DataFrame - Input dataframe with ephemerides columns appended
                     False - If query failed somehow
    """

    # Pass sorted list of epochs to speed up query
    files = {"epochs": ("epochs", "\n".join(sorted(epochs)))}

    # ------
    # Query Miriade for phase angles
    url = "http://vo.imcce.fr/webservices/miriade/ephemcc_query.php"

    params = {
        "-name": f"a:{name}",
        "-mime": "json",
        "-tcoor": "5",
        "-output": "--jul",
        "-tscale": "UTC",
    }

    # Execute query
    try:
        # TODO: Use urllib instead to remove requests dependency
        # or use only requests throughout classy
        r = requests.post(url, params=params, files=files, timeout=50)
    except requests.exceptions.ReadTimeout:
        return False
    j = r.json()

    # Read JSON response
    try:
        ephem = pd.DataFrame.from_dict(j["data"])
    except KeyError:
        return False

    return ephem
