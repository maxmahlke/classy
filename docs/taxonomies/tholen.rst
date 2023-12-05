.. _tholen:

Tholen 1984
-----------

.. image:: gfx/tholen1984_classes.png
   :align: center
   :class: only-light
   :width: 800

.. image:: gfx/tholen1984_classes_dark.png
   :align: center
   :class: only-dark
   :width: 800

.. tab-set::

  .. tab-item:: Overview

    +-------------------+------------------------------------+
    | Observables       | Reflectance Spectra, Visual Albedo |
    +-------------------+------------------------------------+
    | Wavelength Range  | 0.337 - 1.041µm                    |
    +-------------------+------------------------------------+
    | Number of Classes | 15                                 |
    +-------------------+------------------------------------+
    | Class Assignment  | Absolute                           |
    +-------------------+------------------------------------+

  .. tab-item:: Classes

    There are 15 classes. Notation used to flag uncertain (U), indecisive (I),
    and noisy (:) data is not kept.

    The spectral class templates can be loaded using the
    ``classy.taxonomies.tholen.load_templates()`` function, which returns a
    ``dict`` containing the classes as keys and the template spectra as values.

  .. tab-item:: Preprocessing

    The following preprocessing steps are automatically done when using the ``classy.Spectrum.classify()``
    method:

    - :ref:`Resampling <resampling>` to common wavelength grid

    - :ref:`Normalisation <norm_mixnorm>` to 0.55μm

    The preprocessing does not change the ``wave`` and ``refl`` attributes of the
    spectrum.

  .. tab-item:: Classification

    Tholen used a minimal-tree algorithm to gradually identify clusters and
    define classes. This means that classes do not have well defined boxes in
    the principal space and no decision tree is in place.

    Following the minimal-tree principle, new observations asteroids are
    assigned to the class of the closest asteroid from the ECAS dataset in
    principal component space. An issue may arise for A, Q, V, which occupy a
    similar small volume.\ [#f3]_

    The resulting class is assigned to the ``class_tholen`` attribute. The principal
    components scores are accessible via the ``scores_tholen`` attribute.

    .. code-block:: shell

        $ classy classify nysa --taxonomy tholen
