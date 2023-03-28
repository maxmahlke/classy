from . import demeo, mahlke, tholen

from classy.log import logger

SYSTEMS = ["mahlke", "demeo", "bus", "tholen"]
SYSTEMS_REF = ["Mahlke+ 2022", "DeMeo+ 2009", "Bus and Binzel 2002", "Tholen 1984"]


def resolve_system(system):
    """Find out which taxonomic system is requested.

    Parameters
    ----------
    system : str
        The user-requested taxonomic system.

    Returns
    -------
    str
        The resolved taxonomic system.
    """
    if system not in SYSTEMS and system not in SYSTEMS_REF:
        raise ValueError(f"Unknown taxonomic system '{system}'. Choose from {SYSTEMS}.")

    if "mahlke" in system.lower():
        return "Mahlke+ 2022"

    if "demeo" in system.lower():
        return "DeMeo+ 2009"

    if "bus" in system.lower():
        return "Bus and Binzel 2002"

    if "tholen" in system.lower():
        return "Tholen 1984"
