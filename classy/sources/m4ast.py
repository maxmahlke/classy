from urllib.request import urlretrieve

import pandas as pd
import rocks

from classy import config
from classy import core
from classy import index
from classy.log import logger
from classy import tools


REFERENCES = {
    "2016A%26A...586A.129M": ["2016A&A...586A.129M", "Morate+ 2016"],
    "2016A&A...586A.129M": ["2016A&A...586A.129M", "Morate+ 2016"],
    "2001Icar..151..139B": ["2001Icar..151..139B", "Binzel+ 2001"],
    "2011A%26A...530L..12D": ["2011A&A...530L..12D", "de León+ 2011"],
    "2011A&A...530L..12D": ["2011A&A...530L..12D", "de León+ 2011"],
    "2015A%26A...581A...3B": ["2015A&A...581A...3B", "Birlan+ 2015"],
    "2015A&A...581A...3B": ["2015A&A...581A...3B", "Birlan+ 2015"],
    "2016Icar..269....1F": ["2016Icar..269....1F", "Fornasaier+ 2016"],
    "2009Icar..200..480B": ["2009Icar..200..480B", "Binzel+ 2009"],
    "2018RoAJ...28...33B": ["2018RoAJ...28...33B", "Birlan & Nedelcu 2018"],
    "2016RoAJ...26..127B": ["2016RoAJ...26..127B", "Birlan 2016"],
    "1993JGR....98.3031M": ["1993JGR....98.3031M", "McFadden+ 1993"],
    "2007A%26A...473L..33N": ["2007A&A...473L..33N", "Nedelcu+ 2007"],
    "2007A&A...473L..33N": ["2007A&A...473L..33N", "Nedelcu+ 2007"],
}


def _retrieve_spectra():
    """Retrieve all M4AST spectra to m4ast/ the cache directory."""

    # Create directory structure
    PATH_M4AST = config.PATH_CACHE / "m4ast/"
    PATH_M4AST.mkdir(parents=True, exist_ok=True)

    logger.info("Retrieving all M4AST reflectance spectra to cache...")

    catalogue = load_catalogue()

    # Add to global spectra index.
    entries = []
    logger.info("Indexing M4AST spectra...")

    from rich.progress import (
        BarColumn,
        DownloadColumn,
        Progress,
        TextColumn,
        MofNCompleteColumn,
    )

    progress = Progress(
        TextColumn("{task.description}", justify="right"),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        disable=False,
    )
    with progress:
        task = progress.add_task("M4AST", total=len(catalogue))

        for _, row in catalogue.iterrows():
            progress.update(task, advance=1)

            # Download spectrum
            filename = row.access_url.split("/")[-1]

            # urlretrieve(row.access_url, PATH_M4AST / filename)

            name, number = rocks.id(row.target_name)
            date_obs = ""

            if not pd.isna(row.bib_reference):
                bib = row.bib_reference.split("/")[-1]
                bib = REFERENCES[bib][0]
                ref = REFERENCES[bib][1]
            else:
                bib = "Unpublished"
                ref = "Unpublished"

            # Do not index these spectra - already in SMASS/PRIMASS
            if ref in ["Binzel+ 2001", "Morate+ 2016"]:
                continue

            data = _load_data(PATH_M4AST / filename)
            wave = data["wave"]

            # ------
            # Append to index
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "filename": f"m4ast/{filename}",
                    "shortbib": ref,
                    "bibcode": bib,
                    "wave_min": min(wave),
                    "wave_max": max(wave),
                    "N": len(wave),
                    "date_obs": date_obs,
                    "source": "M4AST",
                    "host": "m4ast",
                    "collection": "m4ast",
                    "public": True,
                },
                index=[0],
            )
            entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)
    logger.info(f"Added {len(entries)} M4AST spectra to the classy index.")


def load_spectrum(spec):
    """Load a cached M4AST spectrum."""
    PATH_SPEC = config.PATH_CACHE / spec.filename

    data = _load_data(PATH_SPEC)

    spec = core.Spectrum(
        wave=data["wave"],
        refl=data["refl"],
        source="M4AST",
        name=spec["name"],
        number=spec.number,
        bibcode=spec.bibcode,
        shortbib=spec.shortbib,
        host="m4ast",
        date_obs=spec.date_obs,
        filename=spec.filename,
    )
    return spec


def load_catalogue():
    PATH_CAT = config.PATH_CACHE / "m4ast/m4ast.csv"
    if not PATH_CAT.is_file():
        tools._retrieve_from_github(host="m4ast", which="m4ast", path=PATH_CAT)
    return pd.read_csv(PATH_CAT)


def _load_data(PATH):
    data = pd.read_csv(PATH, names=["wave", "refl"], delimiter=r"\s+", skiprows=9)
    return data
