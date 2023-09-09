from functools import partial
import tarfile
import urllib
from urllib.request import urlretrieve
from zipfile import BadZipFile, ZipFile

import numpy as np

from classy.log import logger

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
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


def download_archive(
    URL, PATH_ARCHIVE, unpack=True, remove=True, encoding=None, progress=True
):
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
    progress : bool
        Whether to show a download progressbar. Default is True.
    """

    if unpack and encoding is None:
        raise ValueError("If unpacking, the encoding must be specified.")

    # Create progress bar
    download = Progress(
        TextColumn("{task.fields[desc]}"),
        BarColumn(bar_width=None),
        DownloadColumn(),
        disable=not progress,
    )

    # Launch download
    with download as prog:
        desc = PATH_ARCHIVE.name
        # TODO: Specify the task name at the source-module level
        if desc == "J_AA_568_L7.tar.gz":
            desc = "J/A&A/568/L7"
        elif desc == "J_AA_627_A124.tar.gz":
            desc = "J/A&A/627/A124"
        task = prog.add_task("download", desc=desc, start=False)
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
            try:
                with ZipFile(PATH_ARCHIVE, "r") as archive:
                    archive.extractall(PATH_ARCHIVE.parent)
            except BadZipFile:
                logger.critical("The returned file is not a Zip file. Try again later.")
                PATH_ARCHIVE.unlink()
                return False

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
        # CDS does not send content lengthj
        if "568" in url:
            content_length = 851695
        elif "627" in url:
            content_length = 117451

    prog.update(task, total=content_length)

    with open(path, "wb") as dest_file:
        prog.start_task(task)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            prog.update(task, advance=len(data))
    return True
