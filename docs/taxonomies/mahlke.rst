.. _mahlke:

Mahlke+ 2022
------------

.. image:: gfx/class_overview.png
   :align: center
   :class: only-light
   :width: 600


.. image:: gfx/class_overview_dark.png
   :align: center
   :class: only-dark
   :width: 600

.. tab-set::

  .. tab-item:: Overview

    +-------------------+------------------------------------------+
    | Observables       | Reflectance Spectra, Visual Albedo       |
    +-------------------+------------------------------------------+
    | Wavelength Range  | 0.45-2.45µm, or any subset of this range |
    +-------------------+------------------------------------------+
    | Number of Classes | 16                                       |
    +-------------------+------------------------------------------+
    | Class Assignment  | Probabilistic                            |
    +-------------------+------------------------------------------+

  .. tab-item:: Classes

    There are 16 classes plus the common placeholder class ``X`` for asteroids
    of either ``E``, ``M``, or ``P`` type without albedo information.

    Any asteroid classified as ``B``, ``C``, or ``P`` type is classified as ``Ch`` if the ``h`` feature is present.
    The classes ``E``, ``M``, ``P`` (and ``X``) can further carry the feature flags ``e`` and ``k``. can further carry the feature flags ``e`` and ``k``
    if the corresponding features are present.

    The spectral class templates can be loaded using the ``classy.taxonomies.mahlke.load_templates()`` function,
    which returns a ``dict`` containing the classes as keys and the template spectra as values.

  .. tab-item:: Preprocessing

    The following preprocessing steps are automatically done when using the ``classy.Spectrum.classify()``
    method:

    - :ref:`Feature Detection <feature_detection>`

    - :ref:`Resampling <resampling>` to common wavelength grid

    - Log-transform of reflectance (``ln``) and albedo (``log10``)

    - :ref:`Normalisation <norm_mixnorm>` using ``mixnorm`` algorithm

    The preprocessing does not change the ``wave`` and ``refl`` attributes of the
    spectrum.

  .. tab-item:: Classification

    The classification results are probabilistic, meaning that the classified
    spectrum has a certain probability to belong to a given class. These probabilities
    are accessible via the ``class_CLASS`` attributes, where ``CLASS`` should
    be replaced by the respective class letter. The most probable class is
    assigned to the ``class_`` attribute.


    .. code-block:: bash

       $ classy classify ceres --plot --taxonomy mahlke

    .. image:: gfx/ceres_classification.png
       :align: center
       :class: only-light
       :width: 800

    .. image:: gfx/ceres_classification_dark.png
       :align: center
       :class: only-dark
       :width: 800


    .. code-block:: python

        >>> import classy
        >>> ceres = classy.Spectra(1, source="ECAS")[0] # get ECAS spectrum of (1) Ceres
        >>> ceres.classify()  # taxonomy='mahlke' is default
        >>> ceres.class_
        'C'
        >>> ceres.class_C
        0.9597002617708775
        >>> ceres.class_B
        0.03962395712733269
