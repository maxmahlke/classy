from urllib.request import urlretrieve

import pandas as pd
import rocks

from classy import config
from classy import index


# ------
# Module definitions
REFERENCES = {
    "2016A%26A...586A.129M": ["2016A&A...586A.129M", "Morate+ 2016"],
    "2016A&A...586A.129M": ["2016A&A...586A.129M", "Morate+ 2016"],
    "2001Icar..151..139B": ["2001Icar..151..139B", "Binzel+ 2001"],
    "2011A%26A...530L..12D": ["2011A&A...530L..12D", "de León+ 2011"],
    "2011A&A...530L..12D": ["2011A&A...530L..12D", "de León+ 2011"],
    "2015A%26A...581A...3B": ["2015A&A...581A...3B", "Birlan+ 2015"],
    "2015A&A...581A...3B": ["2015A&A...581A...3B", "Birlan+ 2015"],
    "2016Icar..269....1F": ["2016Icar..269....1F", "Fornasier+ 2016"],
    "2009Icar..200..480B": ["2009Icar..200..480B", "Binzel+ 2009"],
    "2018RoAJ...28...33B": ["2018RoAJ...28...33B", "Birlan & Nedelcu 2018"],
    "2016RoAJ...26..127B": ["2016RoAJ...26..127B", "Birlan 2016"],
    "1993JGR....98.3031M": ["1993JGR....98.3031M", "McFadden+ 1993"],
    "2007A%26A...473L..33N": ["2007A&A...473L..33N", "Nedelcu+ 2007"],
    "2007A&A...473L..33N": ["2007A&A...473L..33N", "Nedelcu+ 2007"],
}

PATH = config.PATH_DATA / "m4ast/"

DATA_KWARGS = {
    "names": ["wave", "refl", "refl_err"],
    "delimiter": r"\s+",
    "skiprows": 9,
}


# ------
# Module functions
def _retrieve_spectra():
    """Retrieve all M4AST spectra to m4ast/ the cache directory."""

    # Create directory structure
    PATH.mkdir(parents=True, exist_ok=True)

    cat = load_catalog()

    for _, row in cat.iterrows():
        filename = row.access_url.split("/")[-1]
        PATH_OUT = PATH / filename

        if not PATH_OUT.is_file():
            urlretrieve(row.access_url, PATH_OUT)


def load_catalog():
    """Load the M4AST metadata catalog from cache or from remote.

    Returns
    -------
    pd.DataFrame
        The M4AST spectra catalog.
    """
    cat = index.data.load_cat(host="m4ast", which="m4ast")

    # Set bibliographic record
    cat.loc[pd.isna(cat.bib_reference), "shortbib"] = "Unpublished"
    cat.loc[pd.isna(cat.bib_reference), "bibcode"] = "Unpublished"

    for ind, row in cat[~pd.isna(cat.bib_reference)].iterrows():
        bib = row.bib_reference.split("/")[-1]
        bib, ref = REFERENCES[bib]

        cat.loc[ind, "bibcode"] = bib
        cat.loc[ind, "shortbib"] = ref

    # Do not index these spectra - already in SMASS/PRIMASS
    cat = cat[~cat.shortbib.isin(["Binzel+ 2001", "Morate+ 2016"])]

    # This spectrum is a copy of 24CAS
    cat = cat[cat["target_name"] != "Oljato"]
    return cat


def _build_index():
    """Build index of M4AST spectra and add to the classy spectra index."""
    entries = load_catalog()

    # Add spectra metadata
    entries["name"], entries["number"] = zip(*rocks.identify(entries.target_name))

    entries["filename"] = entries["access_url"].apply(
        lambda url: f"m4ast/{url.split('/')[-1]}"
    )

    # TODO: Check if there are observation dates available online
    entries["date_obs"] = ""

    entries["source"] = "M4AST"
    entries["host"] = "M4AST"
    entries["module"] = "m4ast"

    # Et voila
    index.add(entries)
