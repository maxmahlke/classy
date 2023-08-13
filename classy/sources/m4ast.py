from urllib.request import urlretrieve

import pandas as pd
import rocks

from classy import config
from classy import index
from classy import progress
from classy import tools


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


def _load_data(idx):
    """Load data and metadata of a cached Gaia spectrum.

    Parameters
    ----------
    idx : pd.Series
        A row from the classy spectra index.

    Returns
    -------
    pd.DataFrame, dict
        The data and metadata. List-like attributes are in the dataframe,
        single-value attributes in the dictionary.
    """

    # Load spectrum data file
    PATH_DATA = config.PATH_CACHE / idx.filename
    data = pd.read_csv(PATH_DATA, names=["wave", "refl"], delimiter=r"\s+", skiprows=9)
    return data, {}


def load_catalogue():
    """Load the M4AST metadata catalogue from cache or from remote."""
    PATH_CAT = config.PATH_CACHE / "m4ast/m4ast.csv"
    if not PATH_CAT.is_file():
        tools._retrieve_from_github(host="m4ast", which="m4ast", path=PATH_CAT)
    return pd.read_csv(PATH_CAT)


def _retrieve_spectra():
    """Retrieve all M4AST spectra to m4ast/ the cache directory."""

    # Create directory structure
    PATH_M4AST = config.PATH_CACHE / "m4ast/"
    PATH_M4AST.mkdir(parents=True, exist_ok=True)

    catalogue = load_catalogue()

    for ind, row in catalogue.iterrows():
        if not pd.isna(row.bib_reference):
            bib = row.bib_reference.split("/")[-1]
            bib = REFERENCES[bib][0]
            ref = REFERENCES[bib][1]
        else:
            bib = "Unpublished"
            ref = "Unpublished"
        catalogue.loc[ind, "bibcode"] = bib
        catalogue.loc[ind, "shortbib"] = ref

    # Do not index these spectra - already in SMASS/PRIMASS
    catalogue = catalogue[~catalogue.shortbib.isin(["Binzel+ 2001", "Morate+ 2016"])]

    # Add to global spectra index.
    entries = []

    with progress.mofn as mofn:
        task = mofn.add_task("M4AST", total=len(catalogue))

        for _, row in catalogue.iterrows():
            # Download spectrum
            filename = row.access_url.split("/")[-1]

            urlretrieve(row.access_url, PATH_M4AST / filename)

            name, number = rocks.id(row.target_name)
            date_obs = ""

            # ------
            # Append to index
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "filename": f"m4ast/{filename}",
                    "shortbib": row.shortbib,
                    "bibcode": row.bibcode,
                    "date_obs": date_obs,
                    "source": "M4AST",
                    "host": "M4AST",
                    "module": "m4ast",
                },
                index=[0],
            )
            data, _ = _load_data(entry.squeeze())
            entry["wave_min"] = min(data["wave"])
            entry["wave_max"] = max(data["wave"])
            entry["N"] = len(data)

            entries.append(entry)
            mofn.update(task, advance=1)

    entries = pd.concat(entries)
    index.add(entries)
