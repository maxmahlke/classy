:tocdepth: 2

.. _core:

Basic Usage
===========

``classy`` is a tool for the analysis of reflectance spectra. Every spectrum is
represented the ``Spectrum`` class.

Typical analysis steps are:

- **Loading Data** - either ingesting your own or retrieving spectra from public repositories
- **Preprocessing** - this includes primarily feature recognition and smoothing
- **Classification** - the main use case of ``classy``
- **Plotting / Exporting** - visualising or storing the analysis results

Each step is explained further below.

Loading Data
------------

.. _getting_data:

The ``Spectrum`` class stores the data and metadata of the spectra. You can build a spectrum in
two ways: from your own data or by retrieving data from :ref:`public
repositories<public_data>`. Each ``Spectrum`` can contain any metadata you
require.

.. tab-set::

  .. tab-item:: Your Data

    Use the ``classy.Spectrum`` class to ingest your own data. Required
    arguments are ``wave``, the list of wavelength values, and ``refl``, the
    list of reflectance values.

    +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Parameter           | Accepted values   | Explanation                                                                                                                                                                                                                                                         |
    +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ``wave``            | ``list of float`` | The wavelength bins of the spectrum **in micron**.                                                                                                                                                                                                                  |
    +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
    | ``refl``            | ``list of float`` | The reflectance values of the spectrum.                                                                                                                                                                                                                             |
    +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

    .. code-block:: python

      import classy

      # Define dummy data
      wave = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
      refl = [0.85, 0.94, 1, 1.05, 1.02, , 1.02, 1.04, 1.07]

    There are further optional keywords with a pre-defined meaning to
    ``classy``. For example, by providing a ``number``, the asteroid name is
    automatically looked up using `rocks <https://github.com/maxmahlke/rocks>`_
    and added as the ``name`` attribute. If you do not provide an albedo via
    the ``albedo`` or ``pV`` argument, ``classy`` also looks up a value from
    the literature. See a list of these pre-defined keywords in the last tab.

    .. code-block:: python

      number = 1

    Any other arguments you pass are automatically added to the ``Spectrum``,
    which is useful to define metadata relevant for
    your analysis.

    .. code-block:: python

      phase_angle = 23  # in degree

    The final constructor for a spectrum could look like this. Instead of the long
    ``phase_angle``, we give the attribute the shorter name ``phase``. We can choose
    these names at our will.

    .. code-block:: python

      spec = classy.Spectrum(
          wave=wave,
          refl=refl,
          number=number,  # 'name' is automatically set to name of asteroid
          phase=phase_angle,
      )

    All attributes can be accessed and edited via the dot notation.

    .. code-block:: python

      spec.date_obs = '2020/02/01'  # adding metadata to existing spectrum

      print(f"{spec.name} was observed at {spec.phase}deg phase angle.")  # accessing metadata via the dot-notation

  .. tab-item:: Public Data

    ``classy`` sources several public repositories of asteroid reflectance spectra. To get
    the spectra of a specific asteroid, you provide its name, designation, or number to the ``classy.Spectra``
    class.

    .. code-block:: python

      import classy

      spectra = classy.Spectra(4)  # look up spectra of (4) Vesta

    ``classy.Spectra`` is a list of ``classy.Spectrum`` instances. You can use a ``for``-loop
    to access the individual spectra.

    .. code-block:: python

       for spec in spectra:
           print(spec.source, spec.shortbib, spec.wave.min(), spec.wave.max())

    This prints:

    .. code-block:: shell

      Gaia Galluccio+ 2022 0.374 1.034
      SMASS Xu+ 1995 0.422 1.0066
      SMASS Bus and Binzel+ 2002 0.435 0.925
      SMASS Burbine and Binzel 2002 0.902 1.644
      ECAS Zellner+ 1985 0.337 1.041

    The defined attributes for each public repository are described in the :ref:`Public Data <public_data>` section.
    You can select one or more specific repositories using the ``source`` argument.

    .. code-block:: python

      spectra = classy.Spectra(4, source=['SMASS', 'ECAS'])

    Combining your observations with literature ones is straight-forward.

    .. code-block:: python

       my_lutetia = classy.Spectrum(...) # see description of 'Your Data'
       lutetia_literature = classy.Spectra(21)  # returns a list of classy.Spectrum objects
       lutetia_spectra = [my_lutetia] + [lutetia_literature]  # add my_lutetia to the literature results

  .. tab-item:: Metadata

        You can provide any argument you like to ``classy.Spectrum`` to store metadata relevant for your analysis. However, some
        keywords are special to ``classy`` and can be used your analysis:

        .. _predefined_keywords:

        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Accepted values   | Explanation                                                                                                                                             |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``refl_err``        | ``list of float`` | The uncertainty of the reflectance values of the spectrum.                                                                                              |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``name``            | ``str``           | The name of the observed asteroid. It is used to identify the asteroid using `rocks <https://github.com/maxmahlke/rocks>`_.                             |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``number``          | ``float``         | The number of the observed asteroid. It is used to identify the asteroid using `rocks <https://github.com/maxmahlke/rocks>`_.                           |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``albedo``          | ``float``         | The albedo of the observed asteroid. If the asteroid was identified, it is looked up with `rocks <https://github.com/maxmahlke/rocks>`_.                |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``albedo_err``      | ``float``         | The uncertainty of the albedo.                                                                                                                          |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``pV``              | ``float``         | Same as ``albedo``.                                                                                                                                     |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``pV_err``          | ``float``         | Same as ``albedo_err``.                                                                                                                                 |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``e``, ``h``, ``k`` | ``-``             | Reserved for the corresponding spectral features, see Preprocessing > Feature Detection.                                                                |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``date_obs``        | ``str``           | Observation epoch of the spectrum in `ISOT format <https://en.wikipedia.org/wiki/ISO_8601>`_:                                                           |
        |                     |                   | ``YYYY-MM-DDTHH:MM:SS``. It is used to compute the phase angle of the asteroid at the epoch of observation.                                             |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``phase``           | ``float``         | The phase angle at the epoch of observation in degree.                                                                                                  |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+

        The computation of the phase angle from the epoch of observation uses the `Miriade <https://ssp.imcce.fr/webservices/miriade/>`_ webservice. The query results
        are cached to speed up repeated queries.

        All public spectra further have the attributes below, while additional
        attributes are available on a per-source basis, see the individual
        repository descriptions.

        +------------------------------+---------------------------------------------------------------------------------------------------------------------+
        | Attribute                    | Description                                                                                                         |
        +------------------------------+---------------------------------------------------------------------------------------------------------------------+
        | ``shortbib``                 | Short version of reference of the spectrum.                                                                         |
        +------------------------------+---------------------------------------------------------------------------------------------------------------------+
        | ``bibcode``                  | Bibcode of reference publication of the spectrum.                                                                   |
        +------------------------------+---------------------------------------------------------------------------------------------------------------------+
        | ``source``                   | String representing the source of the spectrum (e.g. ``'24CAS'``).                                                  |
        +------------------------------+---------------------------------------------------------------------------------------------------------------------+

        A lot of effort further went into extracting the ``date_obs`` parameters of these spectra from the literature.
        This is not possible in some cases. If the time of the day is not know, ``HH:MM:SS`` is set to ``00:00:00``.
        If the date is not know, the ``date_obs`` attribute is an empty string.
        If the spectrum is an average of observations at different dates, all dates are given,
        separated by a ``,``: ``2004-03-02T00:00:00,2004-05-16T00:00:00``.



Preprocessing
-------------


Storing to file
---------------

Both ``Spectrum`` and ``Spectra`` have a ``to_csv`` method which allows storing
the classification results to ``csv`` format.

.. code-block:: python

   >>> import classy
   >>> spectra = classy.Spectra(3)
   ...  [classy] Found 1 spectrum in Gaia
   ...  [classy] Found 5 spectra in SMASS
   >>> spectra.classify()
   ...  [classy] [(3) Juno] - [Gaia]: S
   ...  [classy] [(3) Juno] - [spex/sp96]: S
   ...  [classy] [(3) Juno] - [smass/smassir]: S
   ...  [classy] [(3) Juno] - [smass/smass1]: S
   ...  [classy] [(3) Juno] - [smass/smass2]: S
   ...  [classy] [(3) Juno] - [smass/smass2]: S
   >>> spectra.to_csv('class_juno.csv')

.. _plotting:

Plotting
--------

.. tab-set::

    .. tab-item:: Command Line

        The quickest way to visualize spectra of an asteroids is the command line.

        .. code-block:: shell

           $ classy spectra vesta

        This will open a plot of the spectra. You can further instruct to ``-c|--classify``
        the spectra in a given ``-t|--taxonomy``.

        .. code-block:: shell

           $ classy spectra vesta -c   # '--taxonomy mahlke' is the default
           $ classy spectra vesta -c --taxonomy tholen

        To only use spectra from one or many sources, use ``-s|--source``.

        .. code-block:: shell

           $ classy spectra vesta -c --taxonomy tholen --source ECAS --source Gaia

        If you set ``--save``, the figure is stored in the current working directory.

        .. code-block:: shell

           $ classy spectra vesta -c --taxonomy tholen --source ECAS --source Gaia --save
           INFO     [classy] Figure stored under sources/4_Vesta_classy.png

    .. tab-item:: python

        Both a ``Spectrum`` and many ``Spectra`` can be plotted using the ``.plot()`` method.

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(43)
           >>> spectra.plot()

        By default, only the spectra themselves are plotted. If you specify the ``taxonomy``
        keyword, the classification results in the specified taxonomic system are added to the
        figure. Note that you have to call ``.classify()`` before.

        .. code-block:: python

           >>> spectra.classify()  # taxonomy='mahlke' is default
           >>> spectra.classify(taxonomy='demeo')
           >>> spectra.plot(taxonomy='mahlke')  # show classification results following Mahlke+ 2022
           >>> spectra.plot(taxonomy='demeo')  # show classification results following DeMeo+ 2009

        By providing a filename to the ``save`` argument, you can instruct ``classy`` to save the figure
        to file instead of opening it.

        .. code-block:: python

           >>> spectra.plot(save='figures/vesta_classified.png')
