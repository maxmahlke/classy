S3OS2
-----

``Small Solar System Objects Spectroscopic Survey``


.. tab-set::

  .. tab-item:: Basics

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    |               820 | 0.49µm                | 0.92µm                 | `Lazzaro+ 2004 <https://ui.adsabs.harvard.edu/abs/2004Icar..172..179L/>`_           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+


    .. image:: gfx/sources/s3os2_julia.png
       :class: only-light
       :align: center
       :width: 600

    .. image:: gfx/sources/s3os2_julia_dark.png
       :class: only-dark
       :align: center
       :width: 600

  .. tab-item:: Data

    When an S3OS2 spectrum is requested for the first time, ``classy`` downloads
    all S3OS2 spectra (6.3MB) and stores them in the :ref:`cache
    directory<cache_directory>` for quick access.

    These attributes are added to the ``Spectrum`` by ``classy``.

    +------------------------------+-----------------------------------------------------------------------------+
    | Attribute                    | Description                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``name``                     | Name or provisional designation of the target asteroid.                     |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``number``                   | Number of the target asteroid.                                              |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``bibcode``                  | ``'2004Icar..172..179L'``                                                   |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``shortbib``                 | ``'Lazzaro+ 2014'``                                                         |
    +------------------------------+-----------------------------------------------------------------------------+
    | ``source``                   | ``'S3OS2'``                                                                 |
    +------------------------------+-----------------------------------------------------------------------------+

  .. tab-item:: Taxonomies

    S3OS2 observations can be classified in the following taxonomic schemes.

    +---------------+-------------+---------------------------------+
    | Tholen 1984   | DeMeo+ 2009 | Mahlke+ 2022                    |
    +---------------+-------------+---------------------------------+
    | No            | No          | Yes (:math:`\lambda \geq 0.45`) |
    +---------------+-------------+---------------------------------+

  .. tab-item:: Usage

    From the command line:

    .. code-block:: bash

        $ classy spectra 89 --source S3OS2
        INFO     [classy] Looking for reflectance spectra of (89) Julia
        INFO     [classy] Found 1 spectrum in S3OS2

    In a script:

    .. code-block:: python

       >>> import classy
       >>> spectra = classy.Spectra(89, source='S3OS2')
       [classy] Retrieving all S3OS2 reflectance spectra [6.3MB] to cache...
       [classy] Found 1 spectrum in S3OS2

  .. tab-item:: Tutorials

    Relevant tutorials are

    - :ref:`Excluding points based on SNR or flag values<excluding_refl>`

    Please feel free to `contribute a tutorial <https://github.com/maxmahlke/classy/issues>`_ should you find an interesting use case.
