from datetime import datetime
import json
from urllib.request import urlretrieve

import pandas as pd
import requests
import rocks

from classy import config
from classy import index

SHORTBIB = "Devogèle+ 2019"
BIBCODE = "2019AJ....158..196D"

# ------
# Module definitions
DATES = {
    "2005 EQ95": "09/03/16",
    "1999 SH10": "14/04/30",
    "2004 VJ1": "15/11/04",
    "2007 MK6": "16/06/15",
    "2008 EZ5": "17/03/19",
    "2008 HA2": "15/03/02",
    "2009 CP5": "13/08/16",
    "2010 CE55": "13/08/11",
    "2010 CF19": "13/08/12",
    "2011 BN24": "13/08/11",
    "2012 CO46": "17/09/14",
    "2013 BO76": "13/08/12",
    "2013 PC7": "13/08/12",
    "2013 PH10": "13/08/09",
    "2013 PJ10": "13/08/11",
    "2013 SR": "13/10/09",
    "2013 VY13": "13/12/11",
    "2013 WA44": "13/12/11",
    "2013 WS43": "13/12/11",
    "2013 XV8": "14/02/28",
    "2014 DF80": "14/03/11",
    "2014 FA7": "14/03/27",
    "2014 FB44": "14/04/07",
    "2014 FN33": "14/04/06",
    "2014 FP47": "14/04/07",
    "2014 GG49": "14/04/13",
    "2014 HE177": "14/05/09",
    "2014 HK129": "14/05/18",
    "2014 HS4": "14/04/29",
    "2014 HT46": "14/04/30",
    "2014 JD": "14/05/06",
    "2014 JJ55": "14/05/18",
    "2014 MD6": "14/09/24",
    "2014 OT338": "14/09/24",
    "2014 RC": "14/09/07",
    "2014 RF11": "14/09/21",
    "2014 SB145": "14/10/02",
    "2014 SF304": "14/10/03",
    "2014 SO142": "14/10/01",
    "2014 SU1": "14/10/07",
    "2014 TP57": "14/10/21",
    "2014 TR57": "14/10/25",
    "2014 UC115": "14/12/18",
    "2014 UV210": "14/12/16",
    "2014 VG2": "14/11/24",
    "2014 WC201": "14/11/28",
    "2014 WE120": "14/11/28",
    "2014 WE121": "14/12/18",
    "2014 WF201": "14/11/29",
    "2014 WO69": "14/11/24",
    "2014 WP4": "14/11/28",
    "2014 WR6": "14/11/24",
    "2014 WS7": "14/11/22",
    "2014 WX202": "14/12/01",
    "2014 WX4": "14/11/19",
    "2014 WY119": "14/11/26",
    "2014 YD": "14/12/20",
    "2014 YD42": "15/01/08",
    "2014 YN": "14/12/22",
    "2014 YT34": "15/01/08",
    "2014 YZ8": "15/01/09",
    "2015 AK1": "15/01/14",
    "2015 AZ43": "15/02/16",
    "2015 BF511": "15/02/02",
    "2015 BK4": "15/01/22",
    "2015 BM510": "15/02/02",
    "2015 CF": "15/02/16",
    "2015 CQ13": "15/02/17",
    "2015 CW13": "15/03/15",
    "2015 CZ12": "15/02/16",
    "2015 DC54": "15/02/22",
    "2015 DK200": "15/03/03",
    "2015 DO215": "15/03/03",
    "2015 DP53": "15/02/22",
    "2015 DS": "15/02/25",
    "2015 DS53": "15/03/02",
    "2015 DU": "15/02/22",
    "2015 DZ198": "15/03/03",
    "2015 EE7": "15/04/12",
    "2015 EF": "15/03/11",
    "2015 EK": "15/03/12",
    "2015 FC": "15/03/24",
    "2015 FP": "15/03/24",
    "2015 FW33": "15/03/23",
    "2015 FX33": "15/03/23",
    "2015 HS11": "15/04/28",
    "2015 HV11": "15/05/12",
    "2015 JF": "15/05/12",
    "2015 JR": "15/05/12",
    "2015 JW": "15/05/20",
    "2015 KA": "15/05/19",
    "2015 KE": "15/05/24",
    "2015 LQ21": "15/06/20",
    "2015 MC": "15/06/20",
    "2015 NA14": "15/07/26",
    "2015 OM21": "15/07/27",
    "2015 OQ21": "15/07/23",
    "2015 PK9": "15/08/18",
    "2015 QB": "15/08/18",
    "2015 SA": "15/09/19",
    "2015 TD144": "15/10/19",
    "2015 TL238": "15/10/22",
    "2015 TM143": "15/10/20",
    "2015 TW237": "15/11/10",
    "2015 TZ143": "15/10/22",
    "2015 TZ237": "15/10/21",
    "2015 VA106": "15/11/18",
    "2015 VE66": "15/11/16",
    "2015 VG105": "15/11/15",
    "2015 VN105": "15/11/15",
    "2015 VO105": "15/11/16",
    "2015 VO142": "15/11/21",
    "2015 WA13": "15/12/05",
    "2015 XB": "15/12/05",
    "2015 XE": "15/12/07",
    "2015 XM128": "15/12/28",
    "2015 XO": "15/12/05",
    "2015 YD": "15/12/30",
    "2015 YD1": "15/12/29",
    "2015 YE": "15/12/31",
    "2015 YS9": "15/12/31",
    "2016 BB15": "16/02/03",
    "2016 BC15": "16/02/04",
    "2016 BJ15": "16/02/03",
    "2016 BW14": "16/02/04",
    "2016 CF29": "16/02/07",
    "2016 CG18": "16/02/05",
    "2016 CK29": "16/02/09",
    "2016 CL29": "16/02/07",
    "2016 CO29": "16/02/07",
    "2016 CS247": "16/02/16",
    "2016 CU29": "16/02/10",
    "2016 EB1": "16/03/06",
    "2016 EB28": "16/03/09",
    "2016 EL157": "16/03/16",
    "2016 EN156": "16/03/16",
    "2016 EQ1": "16/03/10",
    "2016 ES1": "16/03/08",
    "2016 FC": "16/03/21",
    "2016 FL12": "16/04/04",
    "2016 FW13": "16/04/04",
    "2016 GB222": "16/04/19",
    "2016 GV221": "16/04/19",
    "2016 HB": "16/04/19",
    "2016 HN2": "16/05/12",
    "2016 HQ19": "16/05/27",
    "2016 JV": "16/06/08",
    "2016 LG49": "16/06/17",
    "2016 LO48": "16/06/15",
    "2016 NC1": "16/07/16",
    "2016 ND1": "16/07/09",
    "2016 NM15": "16/07/16",
    "2016 NN15": "16/07/08",
    "2016 NS": "16/07/17",
    "2016 PX8": "16/08/12",
    "2016 QB2": "16/09/10",
    "2016 QL44": "16/09/09",
    "2016 QS11": "16/09/15",
    "2016 RB1": "16/09/07",
    "2016 RD20": "16/09/27",
    "2016 RD34": "16/09/15",
    "2016 RF34": "16/09/15",
    "2016 RJ18": "16/09/23",
    "2016 RL20": "16/09/27",
    "2016 RM20": "16/09/24",
    "2016 RT33": "16/09/15",
    "2016 RW": "16/09/30",
    "2016 SA2": "16/09/28",
    "2016 SW1": "16/09/28",
    "2016 SZ1": "16/09/29",
    "2016 TB57": "16/10/19",
    "2016 TM56": "16/10/22",
    "2016 XR23": "16/12/23",
    "2016 YC8": "17/01/03",
    "2016 YH3": "16/12/29",
    "2016 YM3": "16/12/29",
    "2017 AR4": "17/01/08",
    "2017 AS4": "17/01/08",
    "2017 AT4": "17/01/08",
    "2017 BK": "17/01/24",
    "2017 BT": "17/01/25",
    "2017 BU": "17/01/25",
    "2017 BW": "17/01/31",
    "2017 CS": "17/06/04",
    "2017 EH4": "17/03/17",
    "2017 FJ": "17/03/19",
    "2017 FK": "17/03/19",
    "2017 JM2": "17/05/14",
    "2017 QB35": "17/09/02",
    "2017 QG18": "17/09/01",
    "2017 QR35": "17/09/06",
    "2017 RB": "17/09/05",
    "2017 RB16": "17/09/26",
    "2017 RS2": "17/09/23",
    "2017 RU2": "17/09/20",
    "2017 RV2": "17/09/20",
    "2017 VA15": "17/10/19",
    "2017 VC14": "17/11/17",
    "2017 VG1": "17/11/19",
    "2017 VR12": "18/02/25",
    "2017 VV12": "17/11/16",
    "2017 VY13": "17/11/23",
    "2017 VZ14": "17/11/23",
    "2017 YF7": "18/01/22",
    "2017 YR3": "18/01/08",
    "2017 YW3": "18/01/08",
    "2018 AF3": "18/01/23",
    "2018 BG1": "18/01/30",
    "2018 DT": "18/02/25",
    "2018 DY3": "18/03/10",
    "2018 EH": "18/03/10",
}

PATH = config.PATH_DATA / "manos"

DATA_KWARGS = {
    "delimiter": r",",
    "skiprows": 6,
    "names": ["wave", "refl", "refl_err"],
}


# ------
# Module functions
def _retrieve_spectra():
    """Download all MANOS spectra to cache."""
    PATH.mkdir(parents=True, exist_ok=True)

    # Download MANOS index
    manos = retrieve_manos_index()

    # There are only VIS spectra for now in MANOS
    for url in manos.url_vis_spectrum.unique():
        if url is None:
            continue
        PATH_OUT = PATH / url.split("/")[-1]

        if PATH_OUT.is_file():
            continue

        urlretrieve(url, PATH_OUT)


def _build_index():
    """Add the AKARI spectra to the classy spectra index."""

    manos = retrieve_manos_index()

    manos["name"], manos["number"] = zip(*rocks.id(manos["primary_designation"]))
    manos["filename"] = manos["url_vis_spectrum"].apply(
        lambda x: str(PATH / x.split("/")[-1])
    )

    manos["date_obs"] = manos["name"].apply(
        lambda x: datetime.strptime(DATES[x], "%y/%m/%d").isoformat(sep="T")
    )
    manos["shortbib"] = SHORTBIB
    manos["bibcode"] = BIBCODE
    manos["source"] = "MANOS"
    manos["host"] = "MANOS"
    manos["module"] = "manos"

    # Et voila
    index.add(manos)


def _transform_data(_, data):
    # No metadata to record
    meta = {}
    return data, meta


def retrieve_manos_index():
    """Retrieve the MANOS index."""
    PATH_IDX = PATH / "index.json"

    if not PATH_IDX.is_file():
        URL = "https://manos.lowell.edu/api/v1/observations/statuses"
        response = requests.get(URL)
        response = response.json()

        with open(PATH_IDX, "w") as f:
            json.dump(response, f)
    else:
        with open(PATH_IDX, "r") as f:
            response = json.load(f)

    # Only keep those with spectra
    for i, entry in enumerate(response):
        for spec in ["vis_spectrum", "nir_spectrum"]:
            if entry[spec]["exists"]:
                response[i][f"url_{spec}"] = entry[spec]["products"]["data"]
            else:
                response[i][f"url_{spec}"] = None
            response[i].pop(spec)

    manos = pd.DataFrame(response)

    manos = manos[
        (manos["url_nir_spectrum"].notnull()) | (manos["url_vis_spectrum"].notnull())
    ]

    return manos
