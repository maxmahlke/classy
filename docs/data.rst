.. _available_data:

Public Data
===========

Reflectance spectra of asteroids may vary due to observational circumanstances,
subjective data processing, and physical processes on the minor body. It is
generally worthwhile to compare spectral observations of individual asteroids
reported by different surveys. ``classy`` sources the databases listed below to
allow for quick comparisons between literature data and your observations.

You can download and visualize a spectrum using the command line via ``classy spectra``. The ``python``
interface allows more advanced analyses and access to the metadata. Examples
are given for each data collection below. The :ref:`next part<core>` shows how you can add your own
observations to the data.

Gaia DR3
--------

Gaia DR3 contains reflectance spectra of 60,518 Solar System objects between 0.374µm and 1.034µm, see
`Galluccio+ 2022 <https://ui.adsabs.harvard.edu/abs/2022arXiv220612174G/abstract>`_.
The 16 wavelength bands carry photometric flags between 0 and 2 to signal the reliability.

.. tab-set::

  .. tab-item:: Command Line

      Spectra of any asteroid can be downloaded and plotted using the ``spectra`` command.
      Providing the optional ``--source`` argument let's you select one or more specific sources for the spectrum.

      .. code-block:: bash

          $ classy spectra 2789 --source Gaia  # or Gaia,SMASS to combine sources
          INFO     [classy] Looking for reflectance spectra of (2789) Foshan
          INFO     [classy] Found 1 spectrum in Gaia

    .. image:: gfx/gaia_foshan.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/gaia_foshan_dark.png
       :class: only-dark
       :align: center
       :width: 600


  .. tab-item :: python

     The ``classy.Spectra()`` class accpets the name, number, or designation of
     any asteroid and retrieves the available spectra of the asteroid from the
     online repositories. It returns a list of ``classy.Spectrum``
     objects, which are discussed :ref:`later<core>`. The data and metadata are
     accessible via attributes of the same name

     .. code-block:: python

       >>> import classy
       >>> spectra = classy.Spectra("foshan", source="Gaia")  # 'source' is optional
       >>> spec = spectra[0]  # Source 'Gaia' only returns one spectrum
       >>> spec.refl
       array([1.12654897, 0.74284623, 0.86046103, 0.90853702, 1.        ,
              1.0640868 , 1.0827065 , 1.1361642 , 1.2182618 , 1.2419928 ,
              1.2483387 , 1.2360373 , 1.182964  , 1.1580962 , 1.1734432 ,
              1.3041223 ])
       >>> spec.flag
       array([1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
       >>> spec.num_of_spectra
       21


When the first Gaia spectrum is requested, ``classy`` downloads the entire
database (in gzip format, 13MB) to the `cache directory`_ for quick access. As
the spectra show artifical reddening towards the UV, ``classy`` automatically
applies the correction proposed by `Tinaut-Ruano+
2023 <https://arxiv.org/abs/2301.02157>`_.

SMASS and MITHNEOS
------------------

A large repository of Vis-, NIR-, and VisNIR spectra is available from the
`SMASS and MITHNEOS <http://smass.mit.edu/>`_ repository. ``classy`` can
download these spectra and make them available for comparison.

The metadata includes a flag for each value and the asteroid name and number,
which are accessible via ``.asteroid_name`` and ``.asteroid_number`` for any
literature spectrum.

.. tab-set::

  .. tab-item:: Command Line

      .. code-block:: bash

          $ classy spectra 21
          INFO     [classy] Looking for reflectance spectra of (21) Lutetia
          INFO     [classy] Found 3 spectra in SMASS
          INFO     [classy] Found 1 spectrum in Gaia

    .. image:: gfx/smass_lutetia.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/smass_lutetia_dark.png
       :class: only-dark
       :align: center
       :width: 600


  .. tab-item :: python


     .. code-block:: python

       >>> import classy
       >>> spectra = classy.Spectra(21, source="SMASS") # 'SMASS' refers to both SMASS and MITHNEOS
       INFO     [classy] Found 6 spectra in SMASS
       >>> spectra[0].refl
       array([0.9513, 0.9534, 0.963 , 0.9641, 0.9484, 0.9642, 0.9635, 0.961 ,
              0.9585, 0.9596, 0.9741, 0.9813, 0.9874, 0.9749, 0.9679, 0.9676,
              ...
              1.1272, 1.1278, 1.1303, 1.133 , 1.1288, 1.1279, 1.1226, 1.1296,
              1.1274])
       >>> spectra[0].asteroid_name
       'Lutetia'


AKARI
-----

The `AKARI AcuA-spec
catalogue<https://darts.isas.jaxa.jp/astro/akari/data/AKARI-IRC_Spectrum_Pointed_AcuA_1.0.html>`_
contains reflectance spectra between 2.5-5.0µm of 64 asteroids. Each spectrum has different flag attributes
following the original catalogue (`flag_refl`, `flag_thermal`, `flag_satuartuion`, `flag_stellar`), where `1` marks
possibly affected data points and `0` refers to good data points. `classy` adds the simplified `flag` attribute, which is
`0` if all other flag attributes are `0` as well.

ECAS
----
The `Eight Color Asteroid Survey<https://ui.adsabs.harvard.edu/abs/1985Icar...61..355Z>`_ contains ultra-violet and visible colours
of 589 asteroids, between 0.337µm and 1.041µm. Compared to the original catalogue, cells with value `-9.999` were replaced with `np.nan`
values.


.. table:: Metadata Attributes

   +-------------------------------------------------+------+----------------------------------------------------------------+
   | Name                                            | Type | Description                                                    |
   +-----------+-------------------------------------+------+----------------------------------------------------------------+
   | `flag_S_V`, `flag_U_V`, `flag_B_V`,             | int  | Flag is 0 if the uncertainty of the respective colour is below |
   | `flag_V_W`, `flag_V_X`, `flag_V_P`, `flag_V_Z`  |      | the limit defined in Tholen 1984 for high-quality data, else 1.|
   +-------------------------------------------------+------+----------------------------------------------------------------+
   | `flag`                                          | int  | 1 if any of the individual colour flags is 1, else 0.          |
   +-------------------------------------------------+------+----------------------------------------------------------------+
   | `nights`                                        | int  | The number of averaged nights to observe the colour.           |
   +-------------------------------------------------+------+----------------------------------------------------------------+


SsODNet
-------

As the taxonomies by Mahlke+ 2022 and Tholen 1984 make use of the visual albedo, ``classy`` further
queries the `SsODNet database <https://ssp.imcce.fr/webservices/ssodnet/>`_ via `rocks <https://github.com/maxmahlke/rocks>`_
for values from the literature. See `Berthier+ 2023 <https://arxiv.org/abs/2209.10697>`_ to learn more about SsODNet.

What about X?
-------------

Completeness is important. If there is a public online repository of spectra you
would like to see inlcuded, please `suggest it
<https://github.com/maxmahlke/classy/issues>`_ and it will be added if possible.

.. _cache_directory:

Cache Directory
---------------

``classy`` caches the retrieved spectra as well as index files of the online repositories
on your machine. The location depends on your platform and system language. For English systems:

+----------+-------------------------------------------------------+
| Platform | Directory                                             |
+----------+-------------------------------------------------------+
| Linux    | ``/home/$USER/.cache/classy``                         |
+----------+-------------------------------------------------------+
| Mac      | ``/Users/$USER/Library/Caches/classy``                |
+----------+-------------------------------------------------------+
| Windows  | ``'C:\\Users\\$USER\\AppData\\Local\\classy\\Cache'`` |
+----------+-------------------------------------------------------+

.. .. Note::
..
..    A cache-management command à la ``rocks status`` will come soon.
