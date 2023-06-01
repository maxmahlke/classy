import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

REFERENCES = {
    "BINZELETAL2001": ["2001MPSA..36S..20B", "Binzel+ 2001"],
    "CLARKETAL2004": ["2004AJ....128.3070C", "Clark+ 2004"],
    "CLARKETAL2009B": ["2009Icar..202..119C", "Clark+ 2009"],
    "CLARKETAL2010": ["2010JGRE..115.6005C", "Clark+ 2010"],
    "MOSKOVITZETAL2008B": ["2008ApJ...682L..57M", "Moskovitz+ 2008"],
    "MOSKOVITZETAL2010": ["2010Icar..208..773M", "Moskovitz+ 2010"],
    "OCKERT-BELLETAL2008": ["2008Icar..195..206O", "Ockert-Bell+ 2008"],
    "OCKERT-BELLETAL2010": ["2010Icar..210..674O", "Ockert-Bell+ 2010"],
    "RIVKINETAL2005": ["2005Icar..175..175R", "Rivkin+ 2005"],
    "SHEPARDETAL2008": ["2008Icar..193...20", "Shepard+ 2008"],
    "SUNSHINEETAL2004": ["2004MPS...39.1343S", "Sunshine+ 2004"],
    "SUNSHINEETAL2007B": ["2007MPS...42..155S", "Sunshine+ 2007"],
    "SUNSHINEETAL2008": ["2008Sci...320..514S", "Sunshine+ 2008"],
}


def _create_index(PATH_REPO):
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

            # Convert ref from XML to bibcode and shortbib
            bibcode, shortbib = REFERENCES[ref]

            # Identify asteroid
            name, number = rocks.id(id_)

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": shortbib,
                    "bibcode": bibcode,
                    "filename": str(file_).split("/classy/")[1],
                    "source": "Misc",
                    "host": "pds",
                    "collection": "irtf",
                    "public": True,
                },
                index=[0],
            )

            # Add spectrum metadata
            data = _load_data(entry.squeeze())
            entry["wave_min"] = min(data["wave"])
            entry["wave_max"] = max(data["wave"])
            entry["N"] = data["wave"]

            entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame

    """
    file_ = config.PATH_CACHE / meta.filename
    data = pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r"\s+")
    data = data[data.wave != 0]
    return data
