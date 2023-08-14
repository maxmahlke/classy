from . import j_aa_568_l7

from classy import config
from classy import core
from classy import sources
from classy import tools

REPOSITORIES = {
    "J_AA_568_L7": "http://cdsarc.u-strasbg.fr/viz-bin/nph-Cat/tar.gz?J/A+A/568/L7"
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

        # Add spectra to index
        PATH_REPO = PATH_ARCHIVE.with_suffix("")
        getattr(sources.cds, repo)._create_index(PATH_REPO)


def load_spectrum(meta):
    """Load a cached CDS spectrum.

    Parameters
    ----------
    meta : pd.Series
        Row from the CDS index file.

    Returns
    -------
    classy.Spectrum
    """
    # Each repo handles its own data
    data = getattr(sources.cds, meta.collection)._load_data(
        config.PATH_CACHE / meta.filename
    )

    if data.shape[1] > 2:
        refl_err = data[:, 2]
    else:
        refl_err = None

    # Instantiate Spectrum
    spec = core.Spectrum(
        wave=data[:, 0],
        refl=data[:, 1],
        refl_err=refl_err,
        name=meta["name"],
        number=meta.number,
        source=meta.source,
        host=meta.host,
        collection=meta.collection,
        filename=meta.filename,
        classy_id=meta.name,  # the classy index index
    )

    # Add further metadata
    for param in ["shortbib", "bibcode", "date_obs"]:
        setattr(spec, param, meta[param])

    # if "flag" in data.columns.values:
    #     setattr(spec, "flag", data["flag"])

    return spec
