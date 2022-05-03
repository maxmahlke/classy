import classy


def load_model():
    """Load the trained MCFA model of the classy taxonomy.

    Returns
    -------
    mcfa.MCFA
        The MCFA model instance trained for the classy taxonomy.
    """
    import mcfa  # skip the heavy tensorflow import if it can be avoided

    return mcfa.from_file(classy.PATH_DATA / "mcfa/mcfa.pkl")
