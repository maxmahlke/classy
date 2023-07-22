from urllib.request import urlretrieve

import pandas as pd
import rocks


from classy import config
from classy import core
from classy import index
from classy.log import logger
from classy import tools
from classy import sources


def load_spectrum(spec):
    """Load a cached MITHNEOS spectrum."""
    PATH_SPEC = config.PATH_CACHE / spec.filename

    data = _load_data(PATH_SPEC)
    # 2 - reject. This is flag 0 in MITHNEOS
    flags = [0 if f != 0 else 2 for f in data["flag"].values]

    spec = core.Spectrum(
        wave=data["wave"],
        refl=data["refl"],
        refl_err=data["err"],
        flag=flags,
        filename=spec.filename,
        source="MITHNEOS",
        name=spec["name"],
        number=spec.number,
        bibcode=spec.bibcode,
        shortbib=spec.shortbib,
        host="mithneos",
        date_obs=spec.date_obs,
        classy_id=spec.name,  # the classy index index
    )
    return spec


def load_obslog():
    PATH_LOG = config.PATH_CACHE / "mithneos/obslog.csv"
    if not PATH_LOG.is_file():
        tools._retrieve_from_github(host="mithneos", which="obslog", path=PATH_LOG)
    return pd.read_csv(PATH_LOG)


def _retrieve_spectra():
    PATH_OUT = config.PATH_CACHE / "mithneos/"

    # Start with three archives
    DIR_URLS = [
        ("demeo2019", "http://smass.mit.edu/data/minus/DeMeo2019_spectra.tar"),
        (
            "polishook2014",
            "http://smass.mit.edu/data/minus/Spectra31AsteroidPairs_Polishook.zip",
        ),
    ]
    for dir, URL in DIR_URLS:
        # continue
        (PATH_OUT / dir).mkdir(exist_ok=True, parents=True)
        tools.download_archive(URL, PATH_OUT / dir)
    log = load_obslog()

    # Create index for these archives
    mithneos = pd.DataFrame()
    entries = []

    for dir, _ in DIR_URLS:
        for file_ in (PATH_OUT / dir).glob("**/*txt"):
            if "__MACOS" in str(file_):
                # garbage in archive file
                continue

            if file_.name.startswith("._"):
                # more garbage in archive file
                continue

            if dir == "demeo2019" and "fi" not in file_.name:
                # only add the fi06-fi11 runs here
                continue

            if dir == "polishook2014" and file_.name not in POLISHOOK_DATES:
                # do not index three-point visible spectra
                continue

            id_ = sources.smass.get_id_from_filename(file_)
            name, number = rocks.id(id_)

            date_obs = ""  # get's filled in below

            if dir == "demeo2019":
                shortbib, bibcode = ["DeMeo+ 2019", "2019Icar..322...13D"]
                date_obs = log.loc[
                    (log.run == file_.name.split(".")[1]) & (log["name"] == name),
                    "date_obs",
                ].values[0]
            elif dir == "polishook2014":
                shortbib, bibcode = ["Polishook+ 2014", "2014Icar..233....9P"]

                if file_.name in POLISHOOK_DATES:
                    date_obs = POLISHOOK_DATES[file_.name]

                    if date_obs:
                        date_obs = index.convert_to_isot(date_obs, format="%Y-%m-%d")

            filename = str(file_).split("classy/")[-1]

            data = _load_data(file_)
            wave = data["wave"]
            if pd.isna(date_obs):
                bibcode = ""

            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "filename": filename,
                    "shortbib": shortbib,
                    "bibcode": bibcode,
                    "source": "MITHNEOS",
                    "wave_min": min(wave),
                    "wave_max": max(wave),
                    "N": len(wave),
                    "date_obs": date_obs,
                    "source": "MITHNEOS",
                    "host": "mithneos",
                    "collection": "mithneos",
                    "public": True,
                },
                index=[0],
            )
            mithneos = pd.concat([mithneos, entry], ignore_index=True)
            entries.append(entry)

    # -------
    # Scrap all mithneos runs from website and check for unpublished spectra
    runs = (
        [f"sp{num:>02}" for num in range(1, 131)]
        + [f"sp{num:>02}" for num in range(200, 292)]
        + [f"dm{num:>02}" for num in range(1, 20)]
    )

    from rich.progress import (
        BarColumn,
        DownloadColumn,
        Progress,
        TextColumn,
        MofNCompleteColumn,
    )

    progress = Progress(
        TextColumn("{task.description}", justify="right"),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        disable=False,
    )
    with progress:
        task = progress.add_task("MITHNEOS ObsRuns", total=len(runs))
        for run in runs:
            URL = f"http://smass.mit.edu/data/spex/{run}/"
            _download(URL, PATH_OUT / run)
            progress.update(task, advance=1)

            # check for duplicates
            for file_ in (PATH_OUT / run).glob("**/*txt"):
                if "162117-note" in file_.name or "p2010h2" in file_.name:
                    continue

                id_ = sources.smass.get_id_from_filename(file_)
                if id_ is None:
                    continue
                name, number = rocks.id(id_)

                if name is None:
                    continue

                data = _load_data(file_)
                wave = data["wave"]

                filename = str(file_).split("classy/")[-1]

                match = log.loc[(log.run == run) & (log["name"] == name)]

                if not match.empty:
                    date_obs = match["date_obs"].values[0]

                    if not pd.isna(date_obs) and not "T" in date_obs:
                        date_obs = index.convert_to_isot(date_obs, format="%Y-%m-%d")
                    shortbib = match["shortbib"].values[0]
                    bibcode = match["bibcode"].values[0]
                else:
                    date_obs = ""
                    shortbib = "Unpublished"
                    bibcode = "Unpublished"

                if not shortbib:
                    shortbib = "Unpublished"
                if not bibcode:
                    bibcode = "Unpublished"
                if pd.isna(shortbib):
                    shortbib = "Unpublished"
                if pd.isna(bibcode):
                    bibcode = "Unpublished"
                if pd.isna(date_obs):
                    bibcode = ""

                entry = pd.DataFrame(
                    data={
                        "name": name,
                        "number": number,
                        "filename": filename,
                        "shortbib": shortbib,
                        "bibcode": bibcode,
                        "wave_min": min(wave),
                        "wave_max": max(wave),
                        "N": len(wave),
                        "date_obs": date_obs,
                        "source": "MITHNEOS",
                        "host": "mithneos",
                        "collection": "mithneos",
                        "public": True,
                    },
                    index=[0],
                )
                entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)
    logger.info(f"Added {len(entries)} MITHNEOS spectra to the classy index.")


def _download(URL, PATH_OUT):
    import bs4
    import requests

    r = requests.get(URL)

    if not r.ok:
        return

    data = bs4.BeautifulSoup(r.text, "html.parser")
    for l in data.find_all("a"):
        if l["href"].endswith("txt"):
            if "README" in l["href"]:
                continue
            if "READ_ME" in l["href"]:
                continue
            if "speclib-edit-backup" in l["href"]:
                continue

            PATH_OUT.mkdir(exist_ok=True, parents=True)
            urlretrieve(URL + l["href"], PATH_OUT / l["href"])


def _load_data(PATH_SPEC):
    data = pd.read_csv(
        PATH_SPEC,
        names=["wave", "refl", "err", "flag"],
        delimiter="\s+",
        comment="#",
    )

    data = data[data.refl > 0]
    return data


POLISHOOK_DATES = {
    "101703_IR.txt": "2013-10-03",
    "10484_Vis.txt": "2013-05-07",
    "10484_comb_IR.txt": "2011-11-27",
    "13732_IR.txt": "2014-01-07",
    "15107_IR.txt": "2013-01-17",
    "16815_IR.txt": "2013-09-28",
    "17198_comb_IR.txt": "2012-10-18",
    "17288_IR.txt": "2013-04-12",
    "1741_IR.txt": "2013-03-07",
    "19289_IR.txt": "2012-09-11",
    "1979_IR.txt": "2013-03-06",
    "1979_Vis.txt": "2013-05-07",
    "2110_comb_IR.txt": "2011-10-15",
    "25884_comb_IR.txt": "2011-10-25",
    "2897_IR.txt": "2013-03-07",
    "3749_Vis.txt": "2012-02-17",
    "3749_comb_IR.txt": "2012-01-22",
    "38707_IR.txt": "2013-05-12",
    "42946_IR.txt ": "2013-01-17",
    "44612_IR.txt": "2012-09-11",
    "4765_comb_IR.txt": "2013-01-10",
    "4905_IR.txt": "2013-08-08",
    "5026_IR.txt": "2012-04-21",
    "5026_Vis.txt": "2012-06-03",
    "52852_IR.txt": "2012-12-17",
    "54041_comb_IR.txt": "2012-12-14",
    "54827_IR.txt": "2012-08-08",
    "60546_IR.txt": "2013-02-10",
    "6070_IR.txt": "",
    "6070_Vis.txt": "2012-06-01",
    "63440_comb_IR.txt": "2021-11-09",
    "74096_IR.txt": "2013-10-13",
    "8306_IR.txt": "2013-09-07",
    "88604_IR.txt": "2013-06-12",
    "9068_IR.txt": "2013-07-11",
    "92652_IR.txt": "2013-03-06",
    "42946_IR.txt": "2013-01-17",
}
