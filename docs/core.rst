:tocdepth: 2

.. _core:

Basic Usage
===========

``classy`` is a tool for the analysis of reflectance spectra. Every spectrum is
represented the ``Spectrum`` class.

Getting Data
------------

The ``Spectrum`` class stores the data and metadata of the spectra. It is the
main interface to classify and plot observations. You can build a spectrum in
two ways: from your own data or by retrieving data from :ref:`public
repositories<available_data>`. Each ``Spectrum`` can contain any metadata you
require, provided as arguments to the constructor or set via the dot-notation.

.. tab-set::

  .. tab-item:: Your Data

    Use the ``classy.Spectrum`` class to ingest your own data. Required
    arguments are ``wave``, the list of wavelength values, and ``refl``, the
    list of reflectance values.

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

    The defined attributes for each public repository are described in the :ref:`Public Data <available_data>` section.
    You can select one or more specific repositories using the ``source`` argument.

    .. code-block:: python

      spectra = classy.Spectra(4, source=['SMASS', 'ECAS'])

    Combining your observations with literature ones is straight-forward.

    .. code-block:: python

       my_lutetia = classy.Spectrum(...) # see description of 'Your Data'
       lutetia_literature = classy.Spectra(21)  # returns a list of classy.Spectrum objects
       lutetia_spectra = [my_lutetia] + [lutetia_literature]  # add my_lutetia to the literature results

  .. tab-item:: Arguments

        Arguments for ``classy.Spectrum``.

        .. _predefined_keywords:

        Required Arguments - can't do much without these:

        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Accepted values   | Explanation                                                                                                                                                                                                                                                         |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``wave``            | ``list of float`` | The wavelength bins of the spectrum **in micron**.                                                                                                                                                                                                                  |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``refl``            | ``list of float`` | The reflectance values of the spectrum.                                                                                                                                                                                                                             |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        Pre-defined Arguments - these will be considered in the analysis/plots if provided:

        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Accepted values   | Explanation                                                                                                                                                                                                                                                         |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``refl_err``        | ``list of float`` | The uncertainty of the reflectance values of the spectrum.                                                                                                                                                                                                          |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``pV``              | ``float``         | The albedo of the observed asteroid. If it is ``None``, ``classy`` will look it up using `rocks <https://github.com/maxmahlke/rocks>`_.                                                                                                                             |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``pV_err``          | ``float``         | The uncertainty of the albedo.                                                                                                                                                                                                                                      |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``albedo``          | ``float``         | Same as ``pV``.                                                                                                                                                                                                                                                     |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``albedo_err``      | ``float``         | Same as ``pV_err``.                                                                                                                                                                                                                                                 |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``flag``            | ``list of int``   | Flag value of the reflectance values. A nice system is the one by Gaia: ``0`` - good, ``1`` - mediocre, ``2``- bad.                                                                                                                                                 |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``name``            | ``str``           | The name of the observed asteroid. If it is ``None`` but ``number`` was provided, ``classy`` will fill it in using `rocks <https://github.com/maxmahlke/rocks>`_.                                                                                                   |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``number``          | ``float``         | The number of the observed asteroid. If it is ``None`` but ``name`` was provided, ``classy`` will fill it in using `rocks <https://github.com/maxmahlke/rocks>`_.                                                                                                   |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

        Other Arguments - for your convenience only:

        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | Parameter           | Accepted values   | Explanation                                                                                                                                                                                                                                                         |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
        | ``*``               | ``*``             | Any other parameter passed to ``Spectrum`` instance will be added and made accessible as attribute. This allows storing of metadata which is useful to your specific analysis. E.g. ``my_obs = Spectrum([...], phase_angle=45)`` -> ``my_obs.phase_angle # 45``     |
        +---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Preprocessing
-------------

In most cases, reflectance spectra need to be preprocessed prior to the
classification. ``classy`` offers some preprocessing functionality. All functions
describe below can be applied to either a single ``class.Spectrum`` or to many ``classy.Spectra``.

.. tab-set::

   .. tab-item:: Smoothing

        There are two smoothing methods implemented:

        - Savitzky-Golay filter using `scipy.signal.savgol_filter <https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html>`_

        - Spline smoothing using `scipy.interpolate.UnivariateSpline <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.UnivariateSpline.html>`_

        A ``classy.Spectrum`` can be smoothed using the ``.smooth()`` method. The main
        argument is the ``method``, which is either ``savgol`` or ``spline``. All other
        arguments provided to ``.smooth()`` are passed to the underlying smoothing
        function given above.

        .. code-block:: python

           >>> ceres = classy.Spectra(1, source='Gaia')[0]  # returns classy.Spectrum
           >>> ceres.smooth(method='savgol', window_length=7, polyorder=3)  # args passed to scipy.signal.savgol_filter
           >>> ceres.smooth(method='spline', k=3, s=2)  # args passed to scipy.interpolate.UniVariateSpline

   .. tab-item:: Normalising

        Three normalisation methods can be applied to a ``classy.Spectrum``:

        - ``wave``: normalise a spectrum to unity ``at`` a given wavelength by division
        - ``l2``: set the L2-norm of the spectrum to unity
        - ``mixnorm``: Gaussian Mixture Model normalisation with respect to the
          spectra used to derive the Mahlke+ 2022 taxonomy

        Normalisation is applied using the ``.normalize`` method. The ``method``
        keyword accepts one of the three method names given above. The default
        is ``wave`` and requires to define the wavelength at which to normalise
        using the ``at`` argument. ``classy`` then normalises the spectrum to
        unity in the wavelength bin which is the closest to the provided ``at``
        value.

        .. code-block:: python

           >>> ceres = classy.Spectra(1, source='Gaia')[0]  # returns classy.Spectrum
           >>> ceres.normalise(at=1)  # normalises at closest data point -> 0.99 in this case
           >>> ceres.normalise(method='l2')
           >>> ceres.normalise(method='mixnorm')

        .. important::

           When classifying, ``classy`` will automatically apply the required
           normalisation for the respective taxonomic scheme. This happens "under the
           hood" and does not change your data.

   .. tab-item:: Resampling

        Resampling a ``classy.Spectrum`` can be used for extrapolation or for
        homogenisation of different spectra. The ``.resample()`` method uses
        `scipy.interpolate.interp1d
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.interp1d.html>`_.
        The main argument is ``grid``, which accepts a list of wavelength values
        at which to resample the spectrum. All other arguments are passed to the
        ``scipy.interpolate.interp1d`` function.


        .. important::

           When classifying, ``classy`` will automatically apply the required sampling
           for the respective taxonomic scheme. This happens "under the hood" and does
           not change your data.

        Add truncating here

   .. tab-item:: Filtering

        Filtering by flags

        Most spectra need to be smoothed prior to being classified.

        .. important::

            Generally, set reflectance values to nan instead of removing
            them. This makes it easier as otherwise you have to truncate flag and other
            equal length attributes.

   .. tab-item:: Remove Slope

        pass

.. .. tab-item:: Feature Fitting
..
..     Done when the spectrum is instantiated.
..     Can be rerun by user, eg after smoothing.
..
.. .. important::
..
..   Spectra from public repositories automatically get preprocessed prior to classification
..   using pre-defined parameters. For example, Gaia spectra get extrapolated to the ECAS grid
..   prior to classification following Tholen 1984. Set ``preprocessing=None`` in the ``.classify()``
..   call to avoid this.

Classifying
-----------

A ``classy.Spectrum`` can be classified following different taxonomies using the ``.classify()``
function. The ``taxonomy`` argument can be used to choose between different taxonomies.

.. code-block:: python

   >>> import classy
   >>> ceres = classy.Spectra(1, source='Gaia')[0]
   >>> ceres.classify() # taxonomy='mahlke' is default
   >>> ceres.classify(taxonomy='tholen') # Tholen 1984 (requires extrapolation)
   >>> ceres.classify(taxonomy='demeo') # DeMeo+ 2009 (fails due to wavelength range)

The resulting class is added as ``class_`` attribute to the spectrum. For
``tholen`` and ``demeo``, the attributes are ``class_tholen`` and
``class_demeo`` respectively. Further added attributes depending on the chosen
taxonomy are described in the :ref:`taxonomies <available_taxonomies>` section.

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
