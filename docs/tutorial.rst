#########
Tutorials
#########

.. role:: raw-html(raw)
    :format: html

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
