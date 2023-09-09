from . import j_aa_568_l7, j_aa_627_a124

from classy import config
from classy import sources
from classy import tools

REPOSITORIES = {
    "J_AA_568_L7": "http://cdsarc.u-strasbg.fr/viz-bin/nph-Cat/tar.gz?J/A+A/568/L7",
    "J_AA_627_A124": "http://cdsarc.u-strasbg.fr/viz-bin/nph-Cat/tar.gz?J/A+A/627/A124",
}


def _retrieve_spectra():
    """Retrieve all PDS spectra to pds/ in the cache directory."""

    # Create directory structure and check if the spectrum is already cached
    PATH_CDS = config.PATH_CACHE / "cds/"

    for repo, URL in REPOSITORIES.items():
        PATH_ARCHIVE = PATH_CDS / repo
        PATH_ARCHIVE.mkdir(parents=True, exist_ok=True)

        # Download repository
        success = tools.download_archive(
            URL, PATH_ARCHIVE / f"{repo}.tar.gz", encoding="tar.gz"
        )

        if not success:
            continue


def _build_index():
    # Create directory structure and check if the spectrum is already cached
    PATH_CDS = config.PATH_CACHE / "cds/"

    for repo, _ in REPOSITORIES.items():
        PATH_ARCHIVE = PATH_CDS / repo
        # Add spectra to index
        PATH_REPO = PATH_ARCHIVE.with_suffix("")
        getattr(sources.cds, repo.lower())._build_index(PATH_REPO)
