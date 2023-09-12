import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

SHORTBIB, BIBCODE = "Lazzaro+ 2004", "2004Icar..172..179L"

DATA_KWARGS = {"names": ["wave", "refl", "refl_err"], "delimiter": r"\s+"}


def _build_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in (PATH_REPO / "data").iterdir():
        if not dir.is_dir():
            continue

        # Extract meta from LBL file
        for lbl_file in dir.glob("**/*lbl"):
            id_, _, date_obs = pds.parse_lbl(lbl_file)
            file_ = lbl_file.with_suffix(".tab")

            # Identify asteroid
            id_ = id_.split()[0]
            name, number = rocks.id(id_)

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": SHORTBIB,
                    "bibcode": BIBCODE,
                    "filename": file_.relative_to(config.PATH_DATA),
                    "source": "S3OS2",
                    "host": "PDS",
                    "module": "s3os2",
                },
                index=[0],
            )

            entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)
