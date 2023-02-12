from collections import Counter
import logging
from pathlib import Path

import numpy as np
import pandas as pd

import classy.defs
import classy.data
import classy.decision_tree


class Classifier:
    def __init__(self, path_data):
        """Create a classification pipeline directed at a preprocessed data file.

        Parameters
        ----------
        path_data : str
            Path to preprocessed data in a CSV file.
        """
        self.path_data = Path(path_data)
        self.verify_data()

    def verify_data(self):
        """Read in user data and do sanitary check."""
        self.data = pd.read_csv(self.path_data)
        classy.preprocessing.Preprocessor.verify_data(self)

    def classify(self, skip_validation=False):
        """Classify the preprocessed observations."""
        # TODO Switch from pd.DataFrame entirely to OOP approach

        # Instantiate MCFA model instance if not done yet
        model = classy.data.load("mcfa")

        # Get only the classification columns
        data_input = self.data[classy.defs.COLUMNS["all"]].values

        # Compute responsibility matrix based on observed values only
        self.responsibility = model.predict_proba(data_input)

        # Compute latent scores
        self.data_imputed = model.impute(data_input)
        self.data_latent = model.transform(self.data_imputed)

        # Add latent scores and responsibility to input data
        for factor in range(model.n_factors):
            self.data[f"z{factor}"] = self.data_latent[:, factor]

        self.data["cluster"] = np.argmax(self.responsibility, axis=1)

        for i in range(model.n_components):
            self.data[f"cluster_{i}"] = self.responsibility[:, i]

        # Add asteroid classes based on decision tree
        self.data_classified = classy.decision_tree.assign_classes(self.data)

        # Detect features
        self.add_feature_flags()

        # Class per asteroid
        # self.data_classified = _compute_class_per_asteroid(self.data_classified)

        # Print results
        classes = Counter(self.data_classified.class_)
        results_str = ", ".join(
            [f"{count} {class_}" for class_, count in classes.most_common()]
        )
        logging.info(f"Looks like we got {results_str}")

    def plot(self):
        """Display the latent scores of the classified observations."""
        classy.plotting.plot(self.data_classified)

    def add_feature_flags(self):
        """Detect features in spectra and amend the classification."""

        for i, sample in self.data_classified.reset_index(drop=True).iterrows():
            for feature, props in classy.defs.FEATURE.items():
                if sample.class_ in props["candidates"]:

                    if sample[feature] == 1:
                        if feature == "h":
                            self.data_classified.loc[i, "class_"] = "Ch"
                            break
                        else:
                            self.data_classified.loc[i, "class_"] = (
                                self.data_classified.loc[i, "class_"] + feature
                            )

    def to_file(self):
        """Save the classified data to file."""

        if self.data_classified is None:
            raise NotClassifiedError(
                "You have to call the Classifier.classify() function first."
            )

        path_output = Path(
            self.path_data.parent
            / f"{self.path_data.stem if not self.path_data.stem.endswith('_preprocessed') else self.path_data.stem.replace( '_preprocessed', '') }_classified{self.path_data.suffix}"
        )

        self.data_classified.to_csv(path_output, index=False)
        logging.info(f"Stored classified data to {path_output.resolve()}")


def _compute_class_per_asteroid(data):
    """Compute the aggregated most probable class per asteroid.

    Parameters
    ----------
    data : pd.DataFrame
        The classified input observations.

    Returns
    -------
    pd.DataFrame
        The classified input observations with added columns 'class_asteroid' and 'class_asteroid_sf'.
    """

    data["class_asteroid"] = ""
    data["class_asteroid_sf"] = ""

    asteroids = pd.DataFrame()

    for name, spectra in data.groupby("name"):

        # Clear cut case
        if len(spectra) == 1:
            most_likely_class = spectra.class_.values[0][0]
            probabilities = [
                spectra[f"class_{class_}"].values[0] for class_ in classy.defs.CLASSES
            ]
        else:

            # Sum up the class probabilities, take the most likely class
            classes, probabilities = [], []

            for class_ in classy.defs.CLASSES:

                classes.append(class_)

                # Weighted sum based on completeness of observation
                weights = spectra[classy.defs.COLUMNS["all"]].count(axis=1)
                weights = weights.to_numpy()

                # Albedo = 25
                for i, (_, s) in enumerate(spectra.iterrows()):
                    if not pd.isna(s.pV):
                        weights[i] += 24  # already has +1 for albedo

                weights = weights**2
                weights = weights / max(weights)

                probabilities.append(
                    np.average(spectra[f"class_{class_}"].values, weights=weights)
                )

            most_likely_class = classes[np.argmax(probabilities)]

        # Add feature flag
        data.loc[spectra.index, "class_asteroid"] = most_likely_class
        data.loc[spectra.index, "class_asteroid_sf"] = most_likely_class
        most_likely_class_sf = most_likely_class

        if most_likely_class in ["C", "B", "P", "X"] and any(spectra["h"] == 1):
            data.loc[spectra.index, "class_asteroid"] = "Ch"
            data.loc[spectra.index, "class_asteroid_sf"] = "Ch"
            most_likely_class = "Ch"
            most_likely_class_sf = "Ch"
        else:  # Ch cannot have e or k by definition

            if any(
                [
                    most_likely_class.startswith(class_)
                    for class_ in ["E", "M", "P", "X"]
                ]
            ) and any(spectra["e"] == 1):
                data.loc[spectra.index, "class_asteroid"] = data.loc[
                    spectra.index, "class_asteroid"
                ].apply(lambda class_: class_ + "e")
                most_likely_class = most_likely_class + "e"

            if any(
                [
                    most_likely_class.startswith(class_)
                    for class_ in ["E", "M", "P", "X"]
                ]
            ) and any(spectra["k"] == 1):
                data.loc[spectra.index, "class_asteroid"] = data.loc[
                    spectra.index, "class_asteroid"
                ].apply(lambda class_: class_ + "k")
                most_likely_class = most_likely_class + "k"

        # Row for per-asteroid output
        data_asteroid = {}
        data_asteroid["name"] = name
        data_asteroid["number"] = spectra.number.values[0]
        data_asteroid["N"] = len(spectra)
        data_asteroid["class_"] = most_likely_class
        data_asteroid["class_sf"] = most_likely_class_sf

        for c, p in zip(classy.defs.CLASSES, probabilities):
            data_asteroid[f"class_{c}"] = np.round(p, 6)

        for feature in ["e", "h", "k"]:
            presence = (
                1 if any([value == 1 for value in spectra[feature].values]) else 0
            )

            if presence == 0:
                presence = (
                    0
                    if any([value == 0 for value in spectra[feature].values])
                    else np.nan
                )

            data_asteroid[feature] = presence

        asteroids = asteroids.append(
            pd.DataFrame(data=data_asteroid, index=[0]), ignore_index=True
        )
    asteroids["number"] = asteroids["number"].astype("Int64")
    asteroids["e"] = asteroids["e"].astype("Int64")
    asteroids["k"] = asteroids["k"].astype("Int64")
    asteroids["h"] = asteroids["h"].astype("Int64")
    asteroids = asteroids.sort_values("number")
    asteroids.to_csv("/tmp/class_asteroids.csv", index=False)
    return data


class NotClassifiedError:
    pass
