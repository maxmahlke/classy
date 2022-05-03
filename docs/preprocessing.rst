Preprocessing
=============

Preprocessing is either done as first step in the ``classify`` routine or called separately via

.. code-block:: bash

    $ classy preprocess path/to/observations.csv

In either case, the preprocessed observations are saved to a file carrying the same name as the input file
but including a `_preprocessed` suffix before the extension.

.. code-block:: bash

    $ ls
    my_observations.csv
    $ classy preprocess my_observations.csv
    $ ls
    my_observations_preprocessed.csv

Preprocessing consists of the following steps:

- Resampling the spectrum to the classifcation wavelength grid
  - Smoothing with Savitzky-Golay Filter
  - Resampling

Requirements for the input data:

- Samples in rows, features in columns
- Numeric column names should be wavelengths, albedo column should be pV
- Run with logging level debug to get a list of columns identified in the data

When smoothing, the window size and polynomial degree are saved to the
preprocessed data. If the columns "smooth_window" and "smooth_degree" are found,
the smoothing is done automatically.
