.. _available_data:

Public Data
===========

Reflectance spectra of asteroids may vary due to observational circumanstances,
differences in data processing, and physical processes on the minor body. It is
generally worthwhile to compare spectral observations of individual asteroids
reported by different surveys. ``classy`` sources the databases listed below to
allow for quick comparisons between literature data and your observations.

You can download and visualize a spectrum using the command line via the ``$
classy spectra`` command. The ``python`` interface allows more advanced
analyses and access to the metadata. Examples are given for each data
collection below.

Gaia DR3
--------

.. tab-set::

  .. tab-item:: Basics

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 60 518            | 0.374µm               | 1.034µm                | `Galluccio+ 2022 <https://ui.adsabs.harvard.edu/abs/2022arXiv220612174G/abstract>`_ |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+

    .. image:: gfx/gaia_foshan.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/gaia_foshan_dark.png
       :class: only-dark
       :align: center
       :width: 600

  .. tab-item:: Data

    When the first Gaia spectrum is requested, ``classy`` downloads the entire
    database (in gzip format, 13MB) to the `cache directory`_ for quick access.

    The following attributes are copied from the Gaia archive and added to each spectrum.
    See `Galluccio+ 2022 <https://ui.adsabs.harvard.edu/abs/2022arXiv220612174G/abstract>`_ for details.

    +------------------------------+-------------------------------------------------------------------------+
    | Attribute                    | Description                                                             |
    +------------------------------+-------------------------------------------------------------------------+
    | ``wavelength``               | Wavelength of observation (same as ``wave``).                           |
    +------------------------------+-------------------------------------------------------------------------+
    | ``reflectance_spectrum``     | Reflectance values (same as ``refl``).                                  |
    +------------------------------+-------------------------------------------------------------------------+
    | ``reflectance_spectrum_err`` | Reflectance error values (same as ``refl_err``).                        |
    +------------------------------+-------------------------------------------------------------------------+
    | ``flag``                     | Photometric quality flag ( ``0`` = good, ``1`` = mediore, ``2`` = bad). |
    +------------------------------+-------------------------------------------------------------------------+
    | ``source_id``                | Gaia source ID.                                                         |
    +------------------------------+-------------------------------------------------------------------------+
    | ``number_mp``                | Number of target asteroid.                                              |
    +------------------------------+-------------------------------------------------------------------------+
    | ``solution_id``              | Gaia solution ID.                                                       |
    +------------------------------+-------------------------------------------------------------------------+
    | ``denomination``             | Denomination of target asteroid.                                        |
    +------------------------------+-------------------------------------------------------------------------+
    | ``nb_samples``               |                                                                         |
    +------------------------------+-------------------------------------------------------------------------+
    | ``num_of_spectra``           | Number of individual spectra averaged here.                             |
    +------------------------------+-------------------------------------------------------------------------+

    .. important::
        The Gaia spectra show artifical reddening towards the UV. ``classy``
        automatically applies the correction proposed by `Tinaut-Ruano+ 2023
        <https://arxiv.org/abs/2301.02157>`_.


  .. tab-item:: Taxonomies

    Gaia observations can be classified in the following taxonomic schemes.

    +-----------------------------------+-------------+---------------------------------+
    | Tholen 1984                       | DeMeo+ 2009 | Mahlke+ 2022                    |
    +-----------------------------------+-------------+---------------------------------+
    | Yes (after minimal extrapolation) | No          | Yes (:math:`\lambda \geq 0.45`) |
    +-----------------------------------+-------------+---------------------------------+

  .. tab-item:: Usage

    From the command line:

    .. code-block:: bash

        $ classy spectra 2789 --source Gaia
        INFO     [classy] Looking for reflectance spectra of (2789) Foshan
        INFO     [classy] Found 1 spectrum in Gaia

    In a script:

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

  .. tab-item:: Tutorials

    Relevant tutorials are

    - :ref:`Excluding points based on SNR or flag values<excluding_refl>`

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
