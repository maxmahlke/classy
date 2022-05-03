import classy
import pandas as pd


def load(which="classified"):
    """
    Load the original classy data.

    Parameters
    ----------
    which : str
        Which data to load. Choose from ['preprocessed', 'classified']. Default is 'classified'.
    """
    return pd.read_csv(classy.PATH_DATA / f"data/classy_data_{which}.csv")
