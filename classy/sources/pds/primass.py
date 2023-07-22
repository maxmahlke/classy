import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

REFERENCES = {
    "De Leon et al (2016)": ["2016Icar..266...57D", "De León+ 2016"],
    "De Pra et al (2018a)": ["2018Icar..311...35D", "De Prá+ 2018"],
    "De Pra et al (2020a)": ["2020Icar..33813473D", "De Prá+ 2020"],
    "De Pra et al (2020b)": ["2020A%26A...643A.102D", "De Prá+ 2020"],
    "Morate et al (2016)": ["2016A&A...586A.129M", "Morate+ 2016"],
    "Morate et al (2018)": ["2018A&A...610A..25M", "Morate+ 2018"],
    "Morate et al (2019)": ["2019A&A...630A.141M", "Morate+ 2019"],
}


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in (PATH_REPO / "data/spectra").iterdir():
        if not dir.is_dir():
            continue

        # Extract meta from XML file
        for xml_file in dir.glob("**/*xml"):
            id_, ref, date_obs = pds.parse_xml(xml_file)
            file_ = xml_file.with_suffix(".tab")

            # Convert ref from XML to bibcode and shortbib
            if ref is None:
                ref = "Morate et al (2018)"
            elif "PRIMASS visits Hilda" in ref:
                ref = "De Pra et al (2018a)"
            elif "last pieces of" in ref:
                ref = "Morate et al (2019)"
            elif "Sulamitis" in ref:
                ref = "Morate et al (2018)"
            elif "Erigone" in ref:
                ref = "Morate et al (2016)"
            elif "Polana" in ref:
                ref = "De Leon et al (2016)"
            elif "Lixiaohua" in ref:
                ref = "De Pra et al (2020a)"
            elif "comparative analysis" in ref:
                ref = "De Pra et al (2020b)"
            bibcode, shortbib = REFERENCES[ref]

            # Identify asteroid
            name, number = rocks.id(id_)
            if name is None:
                continue

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": shortbib,
                    "bibcode": bibcode,
                    "_filename": str(file_).split("/classy/")[1],
                    "_source": "PRIMASS",
                    "_host": "pds",
                    "_collection": "primass",
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
    return pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r"\s+")
