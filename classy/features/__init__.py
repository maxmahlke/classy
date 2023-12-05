def store_features(features):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        features["number"] = features["number"].astype("Int64")
    features.to_csv(config.PATH_DATA / "features.csv", index=True)


def load_features():
    """Load the feature index."""
    if not (config.PATH_DATA / "features.csv").is_file():
        # Creating indices
        ind = pd.MultiIndex(
            levels=[[], []],
            codes=[[], []],
            names=["filename", "feature"],
            columns=["is_present"],
        )
        return pd.DataFrame(index=ind)
    return pd.read_csv(
        config.PATH_DATA / "features.csv",
        index_col=["filename", "feature"],
        dtype={"is_present": bool},
    )
