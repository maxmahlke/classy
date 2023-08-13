import pandas as pd

from classy import config
from classy import index
from classy import tools

SHORTBIB, BIBCODE = "Usui+ 2019", "2019PASJ...71....1U"


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

    data = pd.read_csv(
        PATH_DATA,
        delimiter="\s+",
        names=[
            "wave",
            "refl",
            "refl_err",
            "flag_err",
            "flag_saturation",
            "flag_thermal",
            "flag_stellar",
        ],
    )

    # Add a joint flag, it's 1 if any other flag is 1
    data["flag"] = data.apply(
        lambda point: 1
        if any(
            bool(point[flag])
            for flag in ["flag_err", "flag_saturation", "flag_thermal", "flag_stellar"]
        )
        else 0,
        axis=1,
    )

    # No metadata to record
    return data, {}


def _retrieve_spectra():
    """Download the AcuA-spec archive to cache."""
    URL = "https://darts.isas.jaxa.jp/pub/akari/AKARI-IRC_Spectrum_Pointed_AcuA_1.0/AcuA_1.0.tar.gz"

    PATH_AKARI = config.PATH_CACHE / "akari"
    PATH_AKARI.mkdir(parents=True, exist_ok=True)

    # Retrieve spectra
    tools.download_archive(URL, PATH_AKARI / "AcuA_1.0.tar.gz", encoding="tar.gz")

    # Catch if download failed
    if not (PATH_AKARI / "AcuA_1.0/target.txt").is_file():
        return

    # Create index
    akari = pd.read_csv(
        PATH_AKARI / "AcuA_1.0/target.txt",
        delimiter="\s+",
        names=["number", "name", "obs_id", "date", "ra", "dec"],
        dtype={"number": int},
    )
    akari = akari.drop_duplicates("number")

    # Drop (4) Vesta and (4015) Wilson-Harrington as there are no spectra of them
    akari = akari[~akari.number.isin([4, 4015])]

    # Add filenames
    akari["filename"] = akari.apply(
        lambda row: f"{row.number:>04}_{row['name']}.txt", axis=1
    )

    akari = akari.drop(columns=["ra", "dec"])

    # Create index to apped to classy index
    entries = []

    for _, row in akari.iterrows():
        name, number = row["name"], row.number
        filename = f"akari/AcuA_1.0/reflectance/{row.filename}"

        # Append to index
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "filename": filename,
                "shortbib": SHORTBIB,
                "bibcode": BIBCODE,
                "date_obs": row.date,
                "source": "AKARI",
                "host": "AKARI",
                "module": "akari",
            },
            index=[0],
        )

        data, _ = _load_data(entry.squeeze())
        entry["wave_min"] = min(data["wave"])
        entry["wave_max"] = max(data["wave"])
        entry["N"] = len(data)
        entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)
