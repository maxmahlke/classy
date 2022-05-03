from collections import Counter
import logging
from pathlib import Path

import classy
import numpy as np
import pandas as pd


class Classifier:
    def __init__(self, path_data):
        """Create a classification pipeline directed at a preprocessed data file.

        Parameters
        ----------
        path_data : str
            Path to preprocessed data in a CSV file.
        """
        self.path_data = Path(path_data)
        self.read_and_verify_data()

    def read_and_verify_data(self):
        """Read in user data and do sanitary check."""
        classy.preprocessing.Preprocessor.read_and_verify_data(self)

    def classify(self, skip_validation=False):
        """Classify the preprocessed observations."""
        # TODO Switch from pd.DataFrame entirely to OOP approach

        # Instantiate MCFA model instance if not done yet
        model = classy.mcfa.load_model()

        # Get only the classification columns
        data_input = self.data[classy.defs.COLUMNS["all"]].values

        # Compute resonsibility matrix based on observed values only
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

                    # self.spectra[i].detect_features(feature, skip_validation)

                    if sample[feature]:
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


class NotClassifiedError:
    pass
