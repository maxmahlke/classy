SMASS
-----

``Small Main-Belt Asteroid Spectroscopic Survey``


.. tab-set::

  .. tab-item:: Basics

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |               317 | 0.45µm                | 0.98µm                 | `Xu+ 1995 <https://ui.adsabs.harvard.edu/abs/1995Icar..115....1X>`_                 |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                65 | 0.36µm                | 0.95µm                 | `Binzel+ 2001 <https://ui.adsabs.harvard.edu/abs/2001Icar..151..139B>`_             |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |               252 | 0.91µm                | 1.64µm                 | `Burbine and Binzel 2002 <https://ui.adsabs.harvard.edu/abs/2002Icar..159..468B>`_  |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |             1,342 | 0.44µm                | 0.93µm                 | `Bus and Binzel 2002 <https://ui.adsabs.harvard.edu/abs/2002Icar..158..106B>`_      |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |                 4 | 0.45µm                | 2.46µm                 | `Rivkin+ 2004 <https://ui.adsabs.harvard.edu/abs/2004Icar..172..408R>`_             |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+


    .. image:: gfx/sources/smass_vesta.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/sources/smass_vesta_dark.png
       :class: only-dark
       :align: center
       :width: 600

  .. tab-item:: Data

    When a SMASS spectrum is requested for the first time, ``classy`` downloads
    all SMASS spectra (2.8MB) and stores them in the :ref:`cache
    directory<cache_directory>` for quick access.

    These attributes are added to the ``Spectrum`` by ``classy``.

    +------------------------------+-----------------------------------------------------------------------------+
    | Attribute                    | Description                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``name``                     | Name or provisional designation of the target asteroid.                     |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``number``                   | Number of the target asteroid.                                              |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``bibcode``                  | Bibcode of reference publication of the spectrum                            |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``shortbib``                 | Short version of reference of the spectrum.                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``source``                   | ``'SMASS'``                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+

  .. tab-item:: Taxonomies

    SMASS observations can be classified in the following taxonomic schemes.

    +---------------+-------------------------------------------+---------------------------------+
    | Tholen 1984   | DeMeo+ 2009                               | Mahlke+ 2022                    |
    +---------------+-------------------------------------------+---------------------------------+
    | Mostly no.    | No except for ``Rivkin+ 2004`` reference. | Yes (:math:`\lambda \geq 0.45`) |
    +---------------+-------------------------------------------+---------------------------------+

  .. tab-item:: Usage

    From the command line:

    .. code-block:: bash

        $ classy spectra 4 --source SMASS
        INFO     [classy] Looking for reflectance spectra of (4) Vesta
        INFO     [classy] Found 3 spectra in SMASS

    In a script:

    .. code-block:: python

       >>> import classy
       >>> spectra = classy.Spectra(4, source='SMASS')
       [classy] Retrieving all SMASS reflectance spectra [2.8MB] to cache...
       [classy] Found 3 spectra in SMASS
       >>> for spec in spectra:
               print(spec.shortbib, spec.wave.min(), spec.wave.max())
       Xu+ 1995 0.422 1.0066
       Bus and Binzel+ 2002 0.435 0.925
       Burbine and Binzel 2002 0.902 1.644
       >>> spectra.classify()
       >>> for spec in spectra:
               print(spec.class_)
       V
       V
       V

  .. tab-item:: Tutorials

    Relevant tutorials are

    - :ref:`Excluding points based on SNR or flag values<excluding_refl>`

    Please feel free to `contribute a tutorial <https://github.com/maxmahlke/classy/issues>`_ should you find an interesting use case.
