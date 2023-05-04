PRIMASS
-------

``PRIMitive Asteroids Spectroscopic Survey``


.. tab-set::

  .. tab-item:: Basics

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                67 | 0.40µm                | 0.86µm                 | `De León+ 2016 <https://ui.adsabs.harvard.edu/abs/2016Icar..266...57D/>`_           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |               101 | 0.40µm                | 0.86µm                 | `Morate+ 2016 <https://ui.adsabs.harvard.edu/abs/2016A&A...586A.129M/>`_            |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                19 | 0.40µm                | 0.86µm                 | `De Prá+ 2018 <https://ui.adsabs.harvard.edu/abs/2018Icar..311...35D/>`_            |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                97 | 0.40µm                | 0.86µm                 | `Morate+ 2018 <https://ui.adsabs.harvard.edu/abs/2018A&A...610A..25M/>`_            |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                73 | 0.40µm                | 0.86µm                 | `Morate+ 2019 <https://ui.adsabs.harvard.edu/abs/2019A&A...630A.141M/>`_            |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                53 | 0.40µm                | 0.86µm                 | `De Prá+ 2020 <https://ui.adsabs.harvard.edu/abs/2020Icar..33813473D/>`_            |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                28 | 0.40µm                | 0.86µm                 | `De Prá+ 2020 <https://ui.adsabs.harvard.edu/abs/2020A%26A...643A.102D/>`_          |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+


    .. image:: gfx/sources/primass_klio.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/sources/primass_klio_dark.png
       :class: only-dark
       :align: center
       :width: 600

  .. tab-item:: Data

    When a PRIMASS spectrum is requested for the first time, ``classy`` downloads
    all PRIMASS spectra (97MB) and stores them in the :ref:`cache
    directory<cache_directory>` for quick access.

    These attributes are added to the ``Spectrum`` by ``classy``.

    +------------------------------+-----------------------------------------------------------------------------+
    | Attribute                    | Description                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``name``                     | Name or provisional designation of the target asteroid.                     |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``number``                   | Number of the target asteroid.                                              |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``bibcode``                  | Bibcode of bibliographic reference.                                         |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``shortbib``                 | Short description of bibliographic reference.                               |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``source``                   | ``'PRIMASS'``                                                               |
    +------------------------------+-----------------------------------------------------------------------------+

    The following metadata provided by PRIMASS is added as well:

    +-------------+------------------------------------------------------+
    | Attribute   | Description                                          |
    +-------------+------------------------------------------------------+
    | ``start_t`` | Time at the start of the observations                |
    +-------------+------------------------------------------------------+
    | ``stop_t``  | Time at the end of the observations                  |
    +-------------+------------------------------------------------------+
    | ``N_exp``   | Number of exposures                                  |
    +-------------+------------------------------------------------------+
    | ``tot_exp`` | Total exposure time                                  |
    +-------------+------------------------------------------------------+
    | ``airmass`` | Airmass at the start of the observation              |
    +-------------+------------------------------------------------------+
    | ``phase``   | Phase angle at the time of the observation           |
    +-------------+------------------------------------------------------+
    | ``r_geo``   | Geocentric distance at the time of the observation   |
    +-------------+------------------------------------------------------+
    | ``r_helio`` | Heliocentric distance at the time of the observation |
    +-------------+------------------------------------------------------+

  .. tab-item:: Taxonomies

    PRIMASS observations can be classified in the following taxonomic schemes.

    +---------------+-------------+---------------------------------+
    | Tholen 1984   | DeMeo+ 2009 | Mahlke+ 2022                    |
    +---------------+-------------+---------------------------------+
    | No            | No          | Yes (:math:`\lambda \geq 0.45`) |
    +---------------+-------------+---------------------------------+

  .. tab-item:: Usage

    From the command line:

    .. code-block:: bash

        $ classy spectra klio --source PRIMASS
        INFO     [classy] Looking for reflectance spectra of (84) Klio
        INFO     [classy] Found 1 spectrum in PRIMASS

    In a script:

    .. code-block:: python

       >>> import classy
       >>> spectra = classy.Spectra(84, source='PRIMASS')
       [classy] Found 1 spectrum in PRIMASS

  .. tab-item:: Tutorials

    Relevant tutorials are

    - :ref:`Excluding points based on SNR or flag values<excluding_refl>`

    Please feel free to `contribute a tutorial <https://github.com/maxmahlke/classy/issues>`_ should you find an interesting use case.
