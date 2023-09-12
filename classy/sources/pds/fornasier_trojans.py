import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

REFERENCES = {
    "FORNASIERETAL2004": ["2004Icar..172..221F", "Fornasier+ 2004"],
    "FORNASIERETAL2007": ["2007Icar..190..622F", "Fornasier+ 2007"],
}

DATA_KWARGS = {"names": ["wave", "refl", "refl_err"], "delimiter": r"\s+"}


def _build_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in (PATH_REPO / "data").iterdir():
        if not dir.is_dir():
            continue

        # Extract meta from XML file
        for xml_file in dir.glob("**/*xml"):
            id_, ref, date_obs = pds.parse_xml(xml_file)
            file_ = xml_file.with_suffix(".tab")

            # Identify asteroid
            name, number = rocks.id(id_)

            # The XML always contains both references, so default is Fornasier+ 2004
            if number in [
                23549,
                24452,
                47967,
                124729,
                5511,
                51359,
                11663,
                32794,
                56968,
                99328,
                105685,
                120453,
                9030,
                11488,
                31820,
                48252,
                84709,
                4829,
                30698,
                31821,
                76804,
                111113,
            ]:
                ref = "FORNASIERETAL2007"

            # Convert ref from XML to bibcode and shortbib
            bibcode, shortbib = REFERENCES[ref]

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": shortbib,
                    "bibcode": bibcode,
                    "filename": file_.relative_to(config.PATH_DATA),
                    "source": "Misc",
                    "host": "PDS",
                    "module": "fornasier_trojans",
                },
                index=[0],
            )
            entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)


def _transform_data(_, data):
    """Apply module-specific data transforms."""
    data["wave"] /= 10000

    meta = {}
    return data, meta
