#########
Tutorials
#########

.. role:: raw-html(raw)
    :format: html

.. _excluding_refl:

.. dropdown:: Excluding points based on SNR or flag values

   To exclude a reflectance value from the classification, you can set it to ``NaN``.

   .. code-block:: python

        import numpy as np

        import classy

        # Get Gaia spectrum of Ceres
        ceres = classy.Spectra(1, source="Gaia")  # returns classy.Spectra instance

        # "ceres" is now a list of classy.Spectrum entries which only one element, the Gaia spectrum
        # We simplify by removing the list and getting the first entry
        ceres = ceres[0]  # returns classy.Spectrum instance

        # Preprocess, classify and plot the result
        ceres.preprocess()
        ceres.classify()
        ceres.plot(add_classes=True)

        # There are sketchy data points
        # Exclude points where the flag is not 0
        ceres.refl[ceres.flag != 0] = np.nan

        # Exclude the last point
        ceres.refl[-1] = np.nan

        # Preprocess, classify and plot again
        ceres.preprocess()
        ceres.classify()
        ceres.plot(add_classes=True)

.. dropdown:: Classifying all asteroids in Gaia

    ``Lines of code: 5``

    ``Estimated execution time: 16h``

    ``Level of Fun: High``

    I will make a catalogue of classifications available via ``classy`` soon.

    .. code-block:: python

        >>> import classy
        >>> gaia = classy.cache.load_gaia_index() # Get list of asteroids in Gaia
        >>> for _, asteroid in gaia.iterrows():
        ...     spec = classy.Spectra(asteroid['name'], source="Gaia")[0]
        ...     spec.classify()
..
.. .. dropdown:: Store results to ``csv`` table
..
..    To be implemented.
