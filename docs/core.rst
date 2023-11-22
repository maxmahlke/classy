:tocdepth: 3

.. _core:

Basic Usage
===========

``classy`` is a tool for the analysis of reflectance spectra. Every spectrum is
represented the ``Spectrum`` class. This class stores the data and metadata of
the spectrum and its target. You can build a spectrum in two ways: by providing
your own data or by retrieving data from :ref:`public repositories<public_data>`.

.. _getting_data:

Creating a ``Spectrum``
-----------------------

To create a ``Spectrum``, you require a list of wavelength values and a list of
reflectance values. These are the mandatory arguments for the class.

.. code-block:: python

  >>> import classy
  >>> # Define dummy data
  >>> wave = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
  >>> refl = [0.85, 0.94, 1.01, 1.05, 1.04, 1.02, 1.04, 1.07, 1.1]
  >>> spec = classy.Spectrum(wave=wave, refl=refl)

Let's have a look at this spectrum.

.. code-block:: python

   >>> spec.plot()

.. image:: gfx/core/spectrum.png
 :align: center
 :class: only-light
 :width: 600

.. image:: gfx/core/spectrum_dark.png
 :align: center
 :class: only-dark
 :width: 600

There are further optional keywords with a pre-defined meaning to
``classy``. You can specify these when creating the ``Spectrum`` or
at a later point via the dot-notation. For example, the ``refl_err`` attribute
contains the reflectance errors.


.. code-block:: python

   >>> spec.refl_err = [0.05, 0.04, 0.03, 0.05, 0.06, 0.03, 0.03, 0.04, 0.07]
   >>> spec.plot()

.. image:: gfx/core/spectrum_with_error.png
 :align: center
 :class: only-light
 :width: 600

.. image:: gfx/core/spectrum_with_error_dark.png
 :align: center
 :class: only-dark
 :width: 600

``classy`` automatically adds the error bars to the plot as it notices the
``refl_err`` attribute. You can find a list of all required and optional
arguments with a pre-defined meaning for ``classy`` below.

.. _predefined_keywords:

+---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
| Parameter           | Accepted values   | Explanation                                                                                                                                             |
+---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``wave``            | ``list of float`` | The wavelength bins of the spectrum **in micron**.                                                                                                      |
+---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``refl``            | ``list of float`` | The reflectance values of the spectrum.                                                                                                                 |
+---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``refl_err``        | ``list of float`` | The uncertainty of the reflectance values of the spectrum.                                                                                              |
+---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``date_obs``        | ``str``           | Observation epoch of the spectrum in `ISOT format <https://en.wikipedia.org/wiki/ISO_8601>`_:                                                           |
|                     |                   | ``YYYY-MM-DDTHH:MM:SS``.                                                                                                                                |
+---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``phase``           | ``float``         | The phase angle at the epoch of observation in degree.                                                                                                  |
+---------------------+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------+

All attributes can be accessed and edited via the dot notation.

.. code-block:: python

  >>> spec.date_obs = '2020-02-01T00:00:00'  # adding metadata to existing spectrum

  print(f"{spec.name} was observed on {spec.date_obs}.")  # accessing metadata via the dot-notation

Any other arguments you pass to ``classy.Spectrum`` or set via the dot-notation
are automatically added to the ``Spectrum``, which is useful to define metadata
relevant for your analysis, such as flags.

.. code-block:: python

  >>> wave = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
  >>> refl = [0.85, 0.94, 1.01, 1.05, 1.04, 1.02, 1.04, 1.07, 1.1]
  >>> flags = [1, 0, 0, 0, 0, 0, 0, 1, 2]
  >>> spec = classy.Spectrum(wave=wave, refl=refl, flags=flags)

Assigning a Target
++++++++++++++++++

Spectra in ``classy`` are typically associated to a minor body. You can specify
the target of the observation using the ``set_target()`` method. ``classy``
will then resolve the target's identity using `rocks
<https://rocks.readthedocs.io/>`_ and retrieve its physical and dynamical
properties. ``classy`` makes use of this information in various ways,
therefore, it is generally beneficial to specify the target.

.. code-block:: python

   >>> spec.set_target('vesta')  # Assigns rocks.Rock instance to spec.target
   >>> spec.target
   Rock(number=4, name='Vesta')
   >>> print(spec.target.number)
   4
   >>> print(spec.target.albedo.value)
   0.380
   >>> print(spec.target.class_)
   'MB>Inner'
   >>> spec.plot()

If target and observation date ``date_obs`` of a ``Spectrum`` are provided,
``classy`` can query the phase angle at the time of observation from the
`Miriade <https://ssp.imcce.fr/webservices/miriade/>`_ webservice. The query
results are cached to speed up repeated queries.

.. code-block:: python

   >>> spec.query_phase()
   >>> print(f"{spec.target.name} was observed on {spec.date_obs} at a phase angle of {spec.phase:.2f}deg")

Working with ``Spectra``
------------------------

``classy`` is connected to several :ref:`public repositories <public_data>` of asteroid reflectance spectra. The ``Spectra`` class
allows to query these repositories for spectra matching a wide range of criteria to ingest them into your analysis.
For example, you can query all databases for any spectra of an asteroid by providing its name or number.

.. code-block:: python

  >>> spectra = classy.Spectra(221)  # look up spectra of (221) Eos
  >>> print(f"Found {len(spectra)} spectra of (221) Eos)

The ``Spectra`` class is essentially a list of ``Spectrum`` instances. You can the usual ``python`` indexing
and iterations to access the individual spectra.

.. code-block:: python

    >>> for spec in spectra:
    >>>     print(spec.source, spec.shortbib, spec.wave.min(), spec.wave.max())
    >>> eos_gaia = spectra[4]

More examples and advanced query criteria are outlined in the :ref:`Selecting Spectra <selecting_spectra>` chapter.

All literature spectra have their corresponding target assigned automatically.

  >>> spectra = classy.Spectra(shortbib="Morate+ 2016")
  >>> for spec in spectra:
  ...     print(spec.target.name)

Besides the attributes of the ``Spectrum`` class given above, all public
spectra further have the attributes below, while additional attributes are
available on a per-source basis, as given in the :ref:`individual repository
descriptions <public_data>`.

+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Attribute                    | Description                                                                                                         |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``shortbib``                 | Short version of reference of the spectrum.                                                                         |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``bibcode``                  | Bibcode of reference publication of the spectrum.                                                                   |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``source``                   | String representing the source of the spectrum (e.g. ``'24CAS'``).                                                  |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+

A lot of effort further went into extracting the ``date_obs`` parameters of
these spectra from the literature. This is not possible in some cases. If the
time of the day is not know, ``HH:MM:SS`` is set to ``00:00:00``. If the date
is not know, the ``date_obs`` attribute is an empty string. If the spectrum is
an average of observations at different dates, all dates are given, separated
by a ``,``: ``2004-03-02T00:00:00,2004-05-16T00:00:00``.

Combining your observations with literature ones is straight-forward.

.. code-block:: python

    >>> my_lutetia = classy.Spectrum(...)
    >>> lutetia_literature = classy.Spectra(21, source='Gaia')
    >>> lutetia_spectra = my_lutetia + lutetia_literature  # add my_lutetia to the literature results
    >>> lutetia_spectra.plot()
