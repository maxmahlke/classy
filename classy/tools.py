import tarfile
from urllib.request import urlretrieve
import urllib
from zipfile import ZipFile

import numpy as np

from classy.log import logger

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    # MofNCompleteColumn,
)


def _retrieve_from_github(host, which, path):
    URL = f"https://raw.githubusercontent.com/maxmahlke/classy/main/data/{host}/{which}.csv"
    path.parent.mkdir(exist_ok=True)

    try:
        urlretrieve(URL, path)
    except:
        urlretrieve(URL.replace("main", "develop"), path)


def find_nearest(array, value):
    """Return index of closest value to target value in array.

    https://stackoverflow.com/a/2566508
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


from functools import partial
from urllib.request import urlopen


def download_archive(URL, PATH_ARCHIVE, unpack=True, remove=True):
    """Download remote archive file to directory. Optionally unpack and remove the file.

    Parameters
    ----------
    URL : str
        The URl to the remote archive.
    PATH_ARCHIVE : pathlib.Path
        The directory to store the archive under.
    unpack : bool
        Whether to unpack the archive in place. Default is True.
    remove : bool
        Whether to remove the archive file after the download. Default is True.
    """

    # Add filename
    if "/pds/" in str(PATH_ARCHIVE):
        PATH_ARCHIVE = PATH_ARCHIVE.parent / URL.split("/")[-1]
    else:
        PATH_ARCHIVE = PATH_ARCHIVE / URL.split("/")[-1]

    download = Progress(
        TextColumn("{task.fields[desc]}"),
        BarColumn(bar_width=None),
        DownloadColumn(),
    )
    with download as prog:
        task = prog.add_task("download", desc=PATH_ARCHIVE.name, start=False)
        success = copy_url(task, URL, PATH_ARCHIVE, prog)

    if not success:
        logger.critical(f"The URL {URL} is currently not reachable. Try again later.")
        return False
    if unpack:
        if PATH_ARCHIVE.name.endswith(".tar.gz"):
            with tarfile.open(PATH_ARCHIVE, mode="r:gz") as archive:
                archive.extractall(PATH_ARCHIVE.parent)
        elif PATH_ARCHIVE.name.endswith(".tar"):
            with tarfile.open(PATH_ARCHIVE, mode="r") as archive:
                archive.extractall(PATH_ARCHIVE.parent)
        elif PATH_ARCHIVE.name.endswith(".zip"):
            with ZipFile(PATH_ARCHIVE, "r") as archive:
                archive.extractall(PATH_ARCHIVE.parent)
    if remove:
        PATH_ARCHIVE.unlink()
    return True


def copy_url(task, url, path, prog):
    """Copy data from a url to a local file."""
    try:
        response = urlopen(url)
    except urllib.error.URLError:
        return False
    # This will break if the response doesn't contain content length
    prog.update(task, total=int(response.info()["Content-length"]))
    with open(path, "wb") as dest_file:
        prog.start_task(task)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            prog.update(task, advance=len(data))
    return True
