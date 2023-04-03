Gaia DR3
--------

.. tab-set::

  .. tab-item:: Basics

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 60 518            | 0.374µm               | 1.034µm                | `Galluccio+ 2022 <https://ui.adsabs.harvard.edu/abs/2022arXiv220612174G/abstract>`_ |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+

    .. image:: gfx/sources/gaia_foshan.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/sources/gaia_foshan_dark.png
       :class: only-dark
       :align: center
       :width: 600

  .. tab-item:: Data

    When the first Gaia spectrum is requested, ``classy`` downloads the entire
    database (in gzip format, 13MB) to the :ref:`cache directory<cache_directory>` for quick access.

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

    These attributes are added by ``classy``.

    +------------------------------+-----------------------------------------------------------------------------+
    | Attribute                    | Description                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``name``                     | Name or provisional designation of the target asteroid.                     |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``number``                   | Number of the target asteroid.                                              |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``shortbib``                 | ``'Galluccio+ 2022'``                                                       |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``bibcode``                  | ``'2022arXiv220612174G'``                                                   |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``source``                   | ``'Gaia'``                                                                  |
    +------------------------------+-----------------------------------------------------------------------------+

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
       >>> spectra = classy.Spectra("foshan", source="Gaia")
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

    Please feel free to `contribute a tutorial <https://github.com/maxmahlke/classy/issues>`_ should you find an interesting use case.
