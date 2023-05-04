import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

REFERENCES = {"L04": ["2004Icar..172..179L", "Lazzaro+ 2004"]}


def _create_index(PATH_REPO):
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
            ref = "L04"

            # Convert ref from lbl to bibcode and shortbib
            bibcode, shortbib = REFERENCES[ref]

            # Identify asteroid
            id_ = id_.split()[0]
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
                    "source": "S3OS2",
                    "host": "pds",
                    "collection": "s3os2",
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


# def load_index():
#     """Load the S3OS2 reflectance spectra index."""
#
#     PATH_INDEX = config.PATH_CACHE / "s3os2/index.csv"
#
#     if not PATH_INDEX.is_file():
#         retrieve_spectra()
#
#     return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})
#
#
# def load_spectrum(spec):
#     """Load a cached S3OS2 spectrum."""
#     PATH_SPEC = config.PATH_CACHE / f"s3os2/EAR_A_I0052_8_S3OS2_V1_0/{spec.filename}"
#
#     data = pd.read_csv(PATH_SPEC, names=["wave", "refl", "err"], delimiter=r"\s+")
#     data = data[data.wave != 0]
#
#     spec = core.Spectrum(
#         wave=data["wave"],
#         refl=data["refl"],
#         refl_err=data["err"],
#         source="S3OS2",
#         name=spec["name"],
#         number=spec.number,
#         bibcode="2004Icar..172..179L",
#         shortbib="Lazzaro+ 2004",
#     )
#     spec._source = "S3OS2"
#     return spec
#
#
# def retrieve_spectra():
#     """Retrieve all S3OS2 spectra to s3os2/ the cache directory."""
#
#     URL = "https://sbnarchive.psi.edu/pds3/non_mission/EAR_A_I0052_8_S3OS2_V1_0.zip"
#
#     # Create directory structure and check if the spectrum is already cached
#     PATH_S3OS2 = config.PATH_CACHE / "s3os2/"
#     PATH_S3OS2.mkdir(parents=True, exist_ok=True)
#
#     logger.info("Retrieving all S3OS2 reflectance spectra [6.3MB] to cache...")
#
#     response = requests.get(URL)
#     files = zipfile.ZipFile(io.BytesIO(response.content))
#     files.extractall(PATH_S3OS2)
#     index = pd.DataFrame()
#
#     for file_ in (PATH_S3OS2 / "EAR_A_I0052_8_S3OS2_V1_0/data").glob("*/*tab"):
#         id_ = file_.name.split("_")[0]
#         name, number = rocks.id(id_)
#
#         entry = pd.DataFrame(
#             data={
#                 "name": name,
#                 "number": number,
#                 "filename": str(file_).split("EAR_A_I0052_8_S3OS2_V1_0/")[1],
#             },
#             index=[0],
#         )
#
#         index = pd.concat([index, entry])
#
#     index["number"] = index["number"].astype("Int64")
#     index.to_csv(PATH_S3OS2 / "index.csv", index=False)
