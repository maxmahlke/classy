Gaia DR3
--------

.. image:: gfx/sources/gaia_foshan.png
   :class: only-light
   :align: center
   :width: 600

.. image:: gfx/sources/gaia_foshan_dark.png
   :class: only-dark
   :align: center
   :width: 600

.. tab-set::

  .. tab-item:: Overview

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 60 518            | 0.374µm               | 1.034µm                | `Galluccio+ 2022 <https://ui.adsabs.harvard.edu/abs/2022arXiv220612174G/abstract>`_ |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+


  .. tab-item:: Attributes

    .. important::
        The Gaia spectra show artifical reddening towards the UV. ``classy``
        automatically applies the correction proposed by `Tinaut-Ruano+ 2023
        <https://arxiv.org/abs/2301.02157>`_.

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
