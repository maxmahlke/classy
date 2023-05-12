
AKARI AcuA
----------

``AKARI Asteroid-catalog-using-AKARI``

.. image:: gfx/sources/akari_egeria.png
   :class: only-light
   :align: center
   :width: 600

.. image:: gfx/sources/akari_egeria_dark.png
   :class: only-dark
   :align: center
   :width: 600
.. tab-set::

  .. tab-item:: Overview

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 64                | 2.5µm                 | 5.0µm                  | `Usui+ 2019 <https://ui.adsabs.harvard.edu/abs/2019PASJ...71....1U>`_               |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+


  .. tab-item:: Attributes

    The following attributes are copied from the AKARI AcuA archive and added to each spectrum.
    See the `AKARI AcuA-spec catalogue description <https://darts.isas.jaxa.jp/astro/akari/data/AKARI-IRC_Spectrum_Pointed_AcuA_1.0.html>`_
    for details.

    +------------------------------+-----------------------------------------------------------------------------+
    | Attribute                    | Description                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``flag_saturation``          | Saturation flag. ``0`` if not contaminated, else ``1``.                     |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``falg_thermal``             | Thermal-emission contamination flag. ``0`` if not contaminated, else ``1``. |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``flag_stellar``             | Stellar contamination flag. ``0`` if not contaminated, else ``1``.          |
    +------------------------------+-----------------------------------------------------------------------------+

    These attributes are added by ``classy``.

    +------------------------------+-----------------------------------------------------------------------------+
    | Attribute                    | Description                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``flag``                     | Merged flag which is ``0`` if all other flag attributes are ``0`` as well.  |
    +------------------------------+-----------------------------------------------------------------------------+
