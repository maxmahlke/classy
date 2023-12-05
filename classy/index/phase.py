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
