import pandas as pd
import rocks

from classy import config
from classy import index

SHORTBIB, BIBCODE = "Popescu+ 2019", " 2019A&A...627A.124P"

DATA_KWARGS = {"names": ["wave", "refl", "refl_err"], "delimiter": "\s+"}


def _build_index(PATH_REPO):
    # Change file permissions, they arrive restricted from CDS

    # Actual index
    cat = pd.read_fwf(
        PATH_REPO / "log.dat",
        colspecs=[(0, 11), (34, 51), (71, 88)],
        names=["designation", "date_obs", "file"],
    )
    entries = []

    for _, row in cat.iterrows():
        # Identify asteroid
        name, number = rocks.id(row.designation)

        # Create index entry
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "date_obs": row.date_obs,
                "shortbib": SHORTBIB,
                "bibcode": BIBCODE,
                "filename": str(
                    (PATH_REPO / f"spec/{row.file}").relative_to(config.PATH_DATA)
                ),
                "source": "Misc",
                "host": "CDS",
                "module": "J_AA_627_A124",
            },
            index=[0],
        )

        entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)
