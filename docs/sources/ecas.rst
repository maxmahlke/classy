ECAS
----

``Eight Color Asteroid Survey``

.. image:: gfx/sources/ecas_palisana.png
   :class: only-light
   :align: center
   :width: 600

.. image:: gfx/sources/ecas_palisana_dark.png
   :class: only-dark
   :align: center
   :width: 600

.. tab-set::

  .. tab-item:: Overview

    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | Number of Spectra | :math:`\lambda_{min}` | :math:`\lambda_{max}`  | Reference                                                                           |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+
    | 911               | 0.337µm               | 1.041µm                | `Zellner+ 1985 <https://ui.adsabs.harvard.edu/abs/1985Icar...61..355Z>`_            |
    +-------------------+-----------------------+------------------------+-------------------------------------------------------------------------------------+


    The available spectra are the single-epoch spectra, not the average spectra as e.g. used in Tholen (1984).

  .. tab-item:: Attributes

    Compared to the original catalogue, cells with value ``-9.999`` are replaced with ``np.nan`` values.
