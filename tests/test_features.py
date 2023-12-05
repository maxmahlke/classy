SPECTRA = [
    ("smass2_13.txt", "h"),
    ("smass2_19.txt", "h"),
    ("smass2_48.txt", "h"),
    ("smass2_51.txt", "h"),
    ("smass2_130.txt", "h"),
]

# TODO: Test feature inspection of spectrum which is not read from file
# Should just set the feature attributes without storing them

# TODO: Test that feature parameters are loaded into GUI


def test_is_covered():
    """Test the wavelength range check of the feature detection. Uses fake wavelength ranges."""

    # To pass, the wavelength needs to cover the entire feature range
    # and to have at least 4 datapoints inside this range.

    # Checking for one feature is sufficient
    # dense = np.linspace(0.4, 0.6, 100)
    # sparse = np.linspace(0.4, 0.6, 5)
    # below_upper_limit = np.linspace(0.4, defs.FEATURE["e"]["upper"] - 0.05, 10)
    # above_lower_limit = np.linspace(defs.FEATURE["e"]["lower"] + 0.05, 0.6, 10)
    #
    # for wave, is_covered in [
    #     (dense, True),
    #     (sparse, False),
    #     (below_upper_limit, False),
    #     (above_lower_limit, False),
    # ]:
    #     feature = Feature("e", wave, np.ones(wave.shape))
    #     assert feature.is_observed == is_covered
