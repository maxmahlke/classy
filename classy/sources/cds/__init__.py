from . import j_aa_568_l7, j_aa_627_a124

from pathlib import Path
import shutil

from classy import config
from classy.utils.logging import logger
from classy import sources
from classy import utils

REPOSITORIES = {
    "J_AA_568_L7": "http://cdsarc.u-strasbg.fr/viz-bin/nph-Cat/tar.gz?J/A+A/568/L7",
    "J_AA_627_A124": "http://cdsarc.u-strasbg.fr/viz-bin/nph-Cat/tar.gz?J/A+A/627/A124",
}


def _retrieve_spectra():
    """Retrieve all PDS spectra to pds/ in the cache directory."""

    # Create directory structure and check if the spectrum is already cached
    PATH_CDS = config.PATH_DATA / "cds/"

    for repo, URL in REPOSITORIES.items():
        PATH_ARCHIVE = (PATH_CDS / repo).with_suffix(".tar.gz")
        PATH_ARCHIVE.parent.mkdir(parents=True, exist_ok=True)

        # The terrible concoction is necessary to remove the .tar.gz
        PATH_DESTINATION = Path(PATH_ARCHIVE.parent / Path(PATH_ARCHIVE.stem).stem)

        # One CDS folder is write-protected. Purge
        if PATH_DESTINATION.is_dir():
            shutil.rmtree(Path(PATH_ARCHIVE.parent / Path(PATH_ARCHIVE.stem).stem))

        # Download repository
        if PATH_ARCHIVE.is_file():
            logger.debug(f"cds/{repo} - Using cached archive file at \n{PATH_ARCHIVE}")
        else:
            success = utils.download.archive(URL, PATH_ARCHIVE)

            if not success:
                continue

        utils.unpack(PATH_ARCHIVE, encoding="tar.gz")


def _build_index():
    # Create directory structure and check if the spectrum is already cached
    PATH_CDS = config.PATH_DATA / "cds/"

    for repo, _ in REPOSITORIES.items():
        PATH_ARCHIVE = PATH_CDS / repo
        # Add spectra to index
        PATH_REPO = PATH_ARCHIVE.with_suffix("")
        getattr(sources.cds, repo.lower())._build_index(PATH_REPO)
