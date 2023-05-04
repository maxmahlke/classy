MITHNEOS
--------



The mithneos observation log is incomplete and does not included the references
that the spectra were published in. I went through literature and files to
recover as much metadata as possible, but I cannot guarantuee that it is 100%
accurate. If not date-obs is given for a spectrum, I could not find it in any
log or publication. If you have more information, please submit it!

Binzel+ 2019 published 805 spectra and 559 here carry this bibliographic
reference as they are the only spectrum of this asteroid in MITHNEOS. The only
way to identify the rest is to visually compare the published
spectra to the spectra in MITHNEOS as there is no metadata file.

``MIT-Hawaii Near-Earth Object Spectroscopic Survey``

.. tab-set::

  .. tab-item:: Basics

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |  1 902            | 0.44µm (varies)       | 2.48µm (varies)        | `Binzel+ 2019 <https://ui.adsabs.harvard.edu/abs/2019Icar..324...41B>`_             |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+

    .. image:: gfx/sources/mithneos_toro.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/sources/mithneos_toro_dark.png
       :class: only-dark
       :align: center
       :width: 600

  .. tab-item:: Data

    When the first MITHNEOS spectrum is requested, ``classy`` downloads the entire
    database (34MB) to the :ref:`cache directory<cache_directory>` for quick access.

    The following attributes are copied from the MITHNEOS website and added to each spectrum.
    The following attributes are copied from the SMASS website and added to each spectrum.
    See the `SMASS website <https://smass.mit.edu>`_ for details.

    +------------------------------+----------------------------------------------------------------------------------------+
    | Attribute                    | Description                                                                            |
    +------------------------------+----------------------------------------------------------------------------------------+
    | ``flag``                     | Column 4 of SMASS data, equal to number of SpeX nights averaged. ``0`` flags bad data. |
    +------------------------------+----------------------------------------------------------------------------------------+

    These attributes are added by ``classy``.

    +------------------------------+-----------------------------------------------------------------------------+
    | Attribute                    | Description                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``name``                     | Name or provisional designation of the target asteroid.                     |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``number``                   | Number of the target asteroid.                                              |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``shortbib``                 | ``'Binzel+ 2019'``                                                          |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``bibcode``                  | ``'2019Icar..324...41B'``                                                   |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``source``                   | ``'MITHNEOS'``                                                              |
    +------------------------------+-----------------------------------------------------------------------------+

  .. tab-item:: Taxonomies

    MITHNEOS observations can be classified in the following taxonomies.

    +-----------------------------------+------------------------------------+---------------------------------+
    | Tholen 1984                       | DeMeo+ 2009                        | Mahlke+ 2022                    |
    +-----------------------------------+------------------------------------+---------------------------------+
    | Mostly no (depends on wavelength) | Mostly no (depends on wavelength)  | Yes (:math:`\lambda \geq 0.45`) |
    +-----------------------------------+------------------------------------+---------------------------------+

  .. tab-item:: Usage

    From the command line:

    .. code-block:: bash

        $ classy spectra toro --source MITHNEOS
        INFO     [classy] Looking for reflectance spectra of (1685) Toro
        INFO     [classy] Found 1 spectrum in MITHNEOS

    In a script:

    .. code-block:: python

       >>> import classy
       >>> spectra = classy.Spectra("toro", source="MITHNEOS")

  .. tab-item:: Tutorials

    Relevant tutorials are

    - :ref:`Excluding points based on SNR or flag values<excluding_refl>`

    Please feel free to `contribute a tutorial <https://github.com/maxmahlke/classy/issues>`_ should you find an interesting use case.
