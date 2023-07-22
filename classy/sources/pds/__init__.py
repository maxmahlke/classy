from . import (
    ecas,
    fornasier_m_types,
    fornasier_trojans,
    ftcas,
    irtf,
    primass,
    moskovitz_v_types,
    reddy_main_belt,
    reddy_nea,
    reddy_nea_mc,
    reddy_vesta,
    s3os2,
    sawyer,
    scas,
    tfcas,
    vilas,
    willman_iannini,
)

import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from classy import config
from classy import core
from classy import sources
from classy import tools

PATH_PDS = config.PATH_CACHE / "pds/"

REPOSITORIES = {
    "scas": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.7-color-survey.zip",
    "tfcas": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.24-color-survey.zip",
    "ftcas": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.52-color-survey.zip",
    "ecas": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.ecas.phot.zip",
    "fornasier_m_types": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast-m-type.fornasier.spectra.zip",
    "fornasier_trojans": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast-trojan.fornasier-etal.spectra.zip",
    "irtf": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.irtf-spex-collection.spectra.zip",
    "moskovitz_v_types": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast-v-type.moscovitz.spectra.zip",
    "reddy_main_belt": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast-mb.reddy.spectra.zip",
    "reddy_nea": "https://sbnarchive.psi.edu/pds3/non_mission/EAR_A_I0046_5_REDDYSPEC_V1_0.zip",
    "reddy_nea_mc": "https://sbnarchive.psi.edu/pds4/non_mission/ast_spectra_reddy_neos_marscrossers_V1_0.zip",
    "reddy_vesta": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast-vesta.reddy.spectra.zip",
    "willman_iannini": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast-iannini-family.spectra.zip",
    "s3os2": "https://sbnarchive.psi.edu/pds3/non_mission/EAR_A_I0052_8_S3OS2_V1_0.zip",
    "sawyer": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.sawyer.spectra_V1_0.zip",
    "primass": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.primass-l.spectra_V1_0.zip",
    "vilas": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.vilas.spectra.zip",
    # "hendrix_iue": "https://sbnarchive.psi.edu/pds4/non_mission/iue.ast.hendrix.spectra_V2_0.zip",
    # "lebofsky_three_micron": "https://sbnarchive.psi.edu/pds4/non_mission/gbo.ast.lebofsky-etal.3-micron-spectra.zip",
    # "rivkin_three_micron": "https://sbnarchive.psi.edu/pds3/non_mission/EAR_A_3_RDR_RIVKIN_THREE_MICRON_V3_0.zip",
}


def _retrieve_spectra():
    """Retrieve all PDS spectra to pds/ in the cache directory."""

    # Create directory structure and check if the spectrum is already cached
    PATH_PDS = config.PATH_CACHE / "pds/"
    PATH_PDS.mkdir(parents=True, exist_ok=True)

    for repo, URL in REPOSITORIES.items():
        PATH_ARCHIVE = PATH_PDS / URL.split("/")[-1]

        # Download repository
        success = tools.download_archive(URL, PATH_ARCHIVE)

        if not success:
            continue

        # Add spectra to index
        PATH_REPO = PATH_ARCHIVE.with_suffix("")
        getattr(sources.pds, repo)._create_index(PATH_REPO)


def parse_xml(PATH_XML):
    """Parse PDS4 XML metadata.

    Returns
    -------
    str, str, str
        The target identifer, reference string, and date of observation.
        If any property is not found, it is None.
    """

    # Parse XML
    tree = ET.parse(PATH_XML)
    root = tree.getroot()

    # This is the child prefix
    prefix = "{http://pds.nasa.gov/pds4/pds/v1}"

    # Get properties
    date_obs = root.findall(
        f"{prefix}Observation_Area/{prefix}Time_Coordinates/{prefix}start_date_time"
    )
    # Appende Z - Zulu time -> UTC
    date_obs = date_obs[0].text.strip("Z") if date_obs else None

    id_ = root.findall(
        f"{prefix}Observation_Area/{prefix}Target_Identification/{prefix}name"
    )

    if id_:
        id_ = id_[0].text.split(")")[-1]
    else:
        id_ = None

    ref = root.findall(
        f"{prefix}Reference_List/{prefix}External_Reference/{prefix}reference_text"
    )

    ref = ref[0].text if ref else None
    return id_, ref, date_obs


def parse_lbl(file_):
    """Parse PDS3 LBL file.

    Returns
    -------
    str, str, str
        The target identifer, reference string, and date of observation.
        If any property is not found, it is None.
    """
    with file_.open("r") as f:
        f = f.read()
        for line in f.split("\n"):
            if line.startswith("TARGET_NAME"):
                target = line.split("=")[-1].strip('" ')
                id_ = target.split("ASTEROID")[-1]

                break
        else:
            print("unknown id_", file_)
        for line in f.split("\n"):
            if line.startswith("START_TIME"):
                date_obs = line.split("=")[-1].strip('" ')
                break
        else:
            print("unknown date-obs", file_)
        for line in f.split("\n"):
            if line.startswith("REFERENCE_KEY_ID"):
                ref = line.split("=")[-1].strip('" ')
                break
        else:
            print("unknown ref", file_)
            ref = None
    return id_, ref, date_obs


def load_spectrum(meta):
    """Load a cached PDS spectrum.

    Parameters
    ----------
    meta : pd.Series
        Row from the PDS index file.

    Returns
    -------
    classy.Spectrum
    """
    # Each repo handles its own data
    data = getattr(sources.pds, meta.collection)._load_data(meta)

    # Instantiate Spectrum
    spec = core.Spectrum(
        wave=data["wave"],
        refl=data["refl"],
        refl_err=data["refl_err"],
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

    if "flag" in data.columns.values:
        setattr(spec, "flag", data["flag"])

    return spec


def spec():
    PATH_SPEC = config.PATH_CACHE / f"pds/{spec.filename}"

    if spec.repo == "hendrix":
        data = pd.read_csv(PATH_SPEC, names=["wave", "refl", "err"])
        data["wave"] /= 10000
        data = data.loc[data.wave > 0.25]
    else:
        data = pd.read_csv(PATH_SPEC, names=["wave", "refl", "err"], delimiter=r"\s+")
    data = data[data.wave != 0]
    data.err[data.err == -9.999] = np.nan
