.. _core:

Adding Data
===========

.. ``classy`` serves to taxonomically classify reflectance spectra of asteroids.
.. Two steps are necessary: (1) retrieve or provide data and metadata to
.. ``classy`` and (2) classify the observation.

``classy`` is centered around the analysis of reflectance spectra. Every
spectrum (public or your own data) is represented by an instance of the ``Spectrum`` class.

.. While I talk about reflectance spectra here, note that Tholen 1984 and
.. Mahlke+ 2022 use the visual albedo in their taxonomic systems.
.. Note::

   While I talk about reflectance spectra here, note that the visual albedo is
   part of the Mahlke+ 2022 taxonomy. ``classy`` makes use of the albedo
   (:ref:`see below <visual_albedo>`), however, for simplicity, the class is called
   ``Spectrum``.

Building a Spectrum
-------------------

The ``Spectrum`` class stores the data and metadata of the spectra. It is the
main interface to classify and plot data.

.. code-block:: python

  spec = classy.Spectrum(wave, refl)

There are two mandatory arguments: ``wave`` - the wavelength bins of the spectrum, ``refl`` - the reflectance values of the spectrum.
The remaining arguments are optional. All parameters are outlined in detail below.

+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Parameter           | Mandatory | Accepted values   | Default value | Explanation                                                                                                                                                                                                                                                         |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``wave``            | Yes       | ``list of float`` | ``-``         | The wavelength bins of the spectrum **in micron**.                                                                                                                                                                                                                  |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``refl``            | Yes       | ``list of float`` | ``-``         | The reflectance values of the spectrum.                                                                                                                                                                                                                             |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``refl_err``        | No        | ``list of float`` | ``None``      | The uncertainty of the reflectance values of the spectrum.                                                                                                                                                                                                          |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``pV``              | No        | ``list of float`` | ``None``      | The albedo of the observed asteroid. If it is ``None``, ``classy`` will look it up using `rocks <https://github.com/maxmahlke/rocks>`_.                                                                                                                             |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``pV_err``          | No        | ``list of float`` | ``None``      | The uncertainty of the albedo.                                                                                                                                                                                                                                      |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``name``            | No        | ``str``           | ``None``      | Name of the spectrum, serving as its unique identifier. E.g. ``TNG_0812_ceres``.                                                                                                                                                                                    |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``flag``            | No        | ``list of int``   | ``None``      | Flag value of the reflectance values. For public data, they follow Gaia: 0 - good, 1 - mediocre, 2- bad. For your data, you can use your own system.                                                                                                                |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``asteroid_name``   | No        | ``str``           | ``None``      | The name of the observed asteroid. If it is ``None`` but ``asteroid_number`` was provided., ``classy`` will fill it in using `rocks <https://github.com/maxmahlke/rocks>`_.                                                                                         |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``asteroid_number`` | No        | ``float``         | ``None``      | The number of the observed asteroid. If it is ``None`` but ``asteroid_name`` was provided., ``classy`` will fill it in using `rocks <https://github.com/maxmahlke/rocks>`_.                                                                                         |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``preprocessed``    | No        | ``bool``          | ``False``     | Whether the provided reflectance values and albedo have been preprocessed following Mahlke+ 2022.                                                                                                                                                                   |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``*``               | No        | ``*``             |   ``-``       | Any other parameter passed to ``Spectrum`` instance will be added and made accessible as attribute. This allows storing of metadata which is useful to your specific analysis. E.g. ``my_obs = Spectrum([...], phase_angle=45)`` -> ``my_obs.phase_angle # 45``     |
+---------------------+-----------+-------------------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. Note::

   In practice, the optional ``name`` and ``asteroid_number`` | ``asteroid_name``
   arguments should be provided as they are required for storing results and
   retrieving more information on the target from the literature.

.. Retrieving spectra from literature
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..
.. ``classy`` is aware of several :ref:`online repositories <available_data>` of
.. reflectance spectra. After providing the name, designation, or number of any
.. asteroid, these repositories are searched and spectra of the referenced
.. asteroid are downloaded. Indices of the data in the repositories as well as the
.. requested spectra are :ref:`cached on your computer <cache_directory>` for
.. quick executions of repeated queries.
..
.. .. tab-set::
..
..   .. tab-item:: Command Line
..
..       .. code-block:: bash
..
..           $ classy spectra ceres
..
..           $ classy spectra ceres --source Gaia,SMASS
..
..   .. tab-item :: python
..
..
..      .. code-block:: python
..
..        >>> import classy
..        >>> spectra = classy.spectra(1)  # provide number, name, or designation
..
..     You can select sources by providing the ``source`` argument.
..
..      .. code-block:: python
..
..        >>> spectra = classy.spectra(1, source="Gaia")  # only Gaia
..        >>> spectra = classy.spectra(1, source=["Gaia", "SMASS"])  # Gaia and SMASS
..
.. Providing your own spectra
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^

You can provide your own observations using the ``Spectrum`` class.

.. code-block:: python

   import classy

   my_wave = []
   my_refl = []

   spectrum_name = "x_feb28"
   asteroid_name = "lutetia"

   my_lutetia = classy.Spectrum(wave=my_wave, refl=my_refl, name=spectrum_name, asteroid_name=asteroid_name)

Note that, in the example above, the ``asteroid_number`` as well as ``pV`` and ``pV_err`` are
automatically filled in using `rocks <https://github.com/maxmahlke/rocks>`_ as
the provided ``asteroid_name`` can be resolved using ``rocks.id`` as (21) Lutetia.

Using many Spectra
------------------

The ``classy.Spectra`` class creates a list of ``classy.Spectrum`` instances by querying
the online repositories for spectra of the provided id.
Combining your observations with literature ones is straight-forward.

.. code-block:: python

   lutetia_literature = classy.Spectra(21)  # returns a list of classy.Spectrum objects
   lutetia_spectra = [my_lutetia] + [lutetia_literature]  # add my_lutetia to the literature results

Shortcuts for classying, plotting, and storing the results (see below) are implemented:


.. code-block:: python

   lutetia_spectra.classify()
   lutetia_spectra.plot(add_classes=True)
   lutetia_spectra.to_csv('classes_lutetia.csv')

.. A special role is given to the ``.flag`` attribute, which can be used to flag
.. noisy data as done in the Gaia spectra. Any datapoint flagged with 0 is
.. considered high quality and will be fully weighted during the preprocessing.
.. Points with flag 1 get 50% weight, points with flag 2 are ignored.

.. Taxonomic Classification
.. ------------------------
..
.. .. Once the data is in place, ``classy`` can classify any ``Spectrum`` in :ref:`different taxonomic systems <available_taxonomies>`.
.. Once the data is in place, ``classy`` can classify any ``Spectrum`` in the :ref:`taxonomic system <available_taxonomies>` by Mahlke+ 2022.
..
.. .. tab-set::
..
..   .. tab-item:: Command Line
..
..       .. code-block:: bash
..
..           $ classy spectra ceres --classify
..
..       .. image:: gfx/ceres_classification.png
..          :align: center
..          :class: only-light
..          :width: 600
..
..       .. image:: gfx/ceres_classification_dark.png
..          :align: center
..          :class: only-dark
..          :width: 600
..
..   .. tab-item :: python
..
..      .. By default, ``Spectrum.classify`` classifies the spectrum in the Mahlke+ 2022 taxonomic system. You can choose different systems using the ``system`` argument.
..      .. The possible values are ["Tholen", "Bus", "DeMeo", "Mahlke"].
..      .. code-block:: python
..
..        >>> import classy
..        >>> spectra = classy.spectra("ceres")
..        >>> for spec in spectra:
..        ...     spec.classify()
..
..      The classification results are stored as attributes: the ``.class_``
..      attribute contains the most probable class (``str``), while ``.class_A`` contains the
..      probability of the spectrum to belong to class A, ``class_B`` to class B,
..      and so forth.
..
..      .. code-block:: python
..
..         >>> for spec in spectra:
..         ...     print(f"[{spec.name}] Most likely class: {spec.class_}")
..         ...     print(f"[{spec.name}] Probability to be a B-type: {spec.class_B}")

.. Plotting the results
.. --------------------
..
.. .. tab-set::
..
..   .. tab-item:: Command Line
..
..       Plotting your observations via the command line is coming soon.
..
..       .. .. code-block:: bash
..       ..
..       ..     .. $ classy spectra ceres --classify
..
..
..   .. tab-item:: python
..
..       .. code-block:: python
..
..          >>> import classy
..          >>> spectra = classy.spectra(1)
..          >>> for spec in spectra:
..          ...     spec.classify()
..          >>> classy.plotting.plot(spectra, add_classes=True)
..
..
Storing results to file
-----------------------

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
