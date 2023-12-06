from functools import partial
import urllib
from urllib.request import Request, urlopen, urlretrieve

from classy.utils.logging import logger


def from_github(host, which, path):
    """Retrieve a file from the classy github repository.

    Parameters
    ----------
    host : str
        The host directory of the fiel in the classy/data tree.
    which : str
        The filename without suffix.
    path : pathlib.Path
        The output filepath.
    """
    URL = f"https://raw.githubusercontent.com/maxmahlke/classy/main/data/{host}/{which}.csv"
    path.parent.mkdir(exist_ok=True)
    urlretrieve(URL, path)


def archive(URL, PATH_ARCHIVE, remove=False, progress=True):
    """Download remote archive file to directory. Optionally unpack and remove the file.

    Parameters
    ----------
    URL : str
        The URl to the remote archive.
    PATH_ARCHIVE : pathlib.Path
        The path where the retrieved data/archive is stored.
    remove : bool
        Whether to remove the archive file after the download. Default is True.
    progress : bool
        Whether to show a download progressbar. Default is True.
    """

    # Launch download
    # with download as prog:
    desc = PATH_ARCHIVE.name
    # TODO: Specify the task name at the source-module level
    if desc == "J_AA_568_L7.tar.gz":
        desc = "J/A&A/568/L7"
    elif desc == "J_AA_627_A124.tar.gz":
        desc = "J/A&A/627/A124"
    # task = prog.add_task("download", desc=desc, start=False)
    success = copy_url(URL, PATH_ARCHIVE)

    if not success:
        logger.critical(
            f"The URL below is currently not reachable. Try again later.\n{URL}"
        )
        return False

    if remove:
        PATH_ARCHIVE.unlink()

    return True


def copy_url(url, path):
    """Copy data from a url to a local file."""

    try:
        req = Request(url)
        req.add_header(
            "User-Agent",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/8.0 Safari/600.1.17",
        )
        response = urlopen(req, timeout=10)
    except urllib.error.URLError:
        return False

    # This will break if the response doesn't contain content length
    # if "Content-length" in response.info():
    #     content_length = int(response.info()["Content-length"])
    # else:
    #     # CDS does not send content lengthj
    #     if "568" in url:
    #         content_length = 851695
    #     elif "627" in url:
    #         content_length = 117451

    # prog.update(task, total=content_length)

    with open(path, "wb") as dest_file:
        # prog.start_task(task)
        for data in iter(partial(response.read, 32768), b""):
            dest_file.write(data)
            # prog.update(task, advance=len(data))
    return True
