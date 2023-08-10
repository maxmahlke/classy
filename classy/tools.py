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


def download_archive(URL, PATH_ARCHIVE, unpack=True, remove=True, encoding=None):
    """Download remote archive file to directory. Optionally unpack and remove the file.

    Parameters
    ----------
    URL : str
        The URl to the remote archive.
    PATH_ARCHIVE : pathlib.Path
        The path where the retrieved data/archive is stored.
    unpack : bool
        Whether to unpack the archive in place. Default is True.
    remove : bool
        Whether to remove the archive file after the download. Default is True.
    encoding : str
        The compression encoding. Default is None. Must be specified if unpack is True.
    """

    if unpack and encoding is None:
        raise ValueError("If unpacking, the encoding must be specified.")

    # Create progress bar
    download = Progress(
        TextColumn("{task.fields[desc]}"), BarColumn(bar_width=None), DownloadColumn()
    )

    # Launch download
    with download as prog:
        task = prog.add_task("download", desc=PATH_ARCHIVE.name, start=False)
        success = copy_url(task, URL, PATH_ARCHIVE, prog)

    if not success:
        logger.critical(f"The URL {URL} is currently not reachable. Try again later.")
        return False

    if unpack:
        if encoding == "tar.gz":
            with tarfile.open(PATH_ARCHIVE, mode="r:gz") as archive:
                archive.extractall(PATH_ARCHIVE.parent)
        elif encoding == "tar":
            with tarfile.open(PATH_ARCHIVE, mode="r") as archive:
                archive.extractall(PATH_ARCHIVE.parent)
        elif encoding == "zip":
            with ZipFile(PATH_ARCHIVE, "r") as archive:
                archive.extractall(PATH_ARCHIVE.parent)

    if remove:
        PATH_ARCHIVE.unlink()

    return True


def copy_url(task, url, path, prog):
    """Copy data from a url to a local file."""
    from urllib.request import Request, urlopen  # Python 3

    try:
        req = Request(url)
        req.add_header(
            "User-Agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17",
        )
        response = urlopen(req)
    except urllib.error.URLError:
        return False

    # This will break if the response doesn't contain content length
    if "Content-length" in response.info():
        content_length = int(response.info()["Content-length"])
    else:
        content_length = 100

    prog.update(task, total=content_length)

    with open(path, "wb") as dest_file:
        prog.start_task(task)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            prog.update(task, advance=len(data))
    return True
