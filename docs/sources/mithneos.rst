MITHNEOS
--------

``MIT-Hawaii Near-Earth Object Spectroscopic Survey``

.. image:: gfx/sources/mithneos_toro.png
   :class: only-light
   :align: center
   :width: 600

.. image:: gfx/sources/mithneos_toro_dark.png
   :class: only-dark
   :align: center
   :width: 600

.. tab-set::

  .. tab-item:: Overview

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 537               | 0.337µm               | 2.49µm                 | `Binzel+ 2019 <https://ui.adsabs.harvard.edu/abs/2019Icar..324...41B>`_             |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 88                | 0.65µm                | 2.49µm                 | `DeMeo+ 2019  <https://ui.adsabs.harvard.edu/abs/2019Icar..322...13D>`_             |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 475               | 0.36µm                | 2.49μm                 | `Marsset+ 2022 <https://ui.adsabs.harvard.edu/abs/2022AJ....163..165M>`_            |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 36                | 0.35μm                | 2.49μm                 | `Polishook+ 2014  <https://ui.adsabs.harvard.edu/abs/2014Icar..233....9P>`_         |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 769               | 0.35μm                | 2.49μm                 | Unpublished*                                                                        |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+

    .. important::

        Binzel+ 2019 published 805 spectra, however, it is not evident which
        MITHNEOS spectra this includes. 537 of the 805 can be identified
        as they are the only spectrum of the respective asteroid in MITHNEOS.
        These spectra are associated to Binzel+ 2019 in ``classy``.
        To identify the remaining published spectra, it is necessary to
        visually compare the published spectra to the spectra in MITHNEOS.
        Feel free to contribute should you have identified a misreferenced spectrum.

  .. tab-item:: Attributes

    The following attributes are copied from the MITHNEOS website and added to each spectrum.
    The following attributes are copied from the SMASS website and added to each spectrum.
    See the `SMASS website <https://smass.mit.edu>`_ for details.

    +------------------------------+-------------------------------------------------------------------------------------------+
    | Attribute                    | Description                                                                               |
    +------------------------------+-------------------------------------------------------------------------------------------+
    | ``flag``                     | Column 4 of MITHNEOS data, equal to number of SpeX nights averaged. ``0`` flags bad data. |
    +------------------------------+-------------------------------------------------------------------------------------------+
