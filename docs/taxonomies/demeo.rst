DeMeo+ 2009
-----------

.. image:: gfx/classes_demeo.png
   :align: center
   :class: only-light
   :width: 500

.. image:: gfx/classes_demeo_dark.png
   :align: center
   :class: only-dark
   :width: 500

.. tab-set::

  .. tab-item:: Overview

    +-------------------+------------------------------------------+
    | Observables       | Reflectance Spectra                      |
    +-------------------+------------------------------------------+
    | Wavelength Range  | 0.45-2.45µm                              |
    +-------------------+------------------------------------------+
    | Number of Classes | 24\ [#f2]_                               |
    +-------------------+------------------------------------------+
    | Class Assignment  | Absolute                                 |
    +-------------------+------------------------------------------+

  .. tab-item:: Classes

    There are 24 main classes. The S-type and A and Q classes can carry a ``w``
    suffix indicating a weathered, reddened appearance.

    The class templates for the complexes ``C``, ``S``, and ``X`` can be added
    to spectra plots using the ``--templates`` argument of ``$ classy spectra``:

    .. code-block:: bash

      $ classy spectra Eos --templates M --taxonomy demeo

    In a script, they can be loaded using the ``classy.taxonomies.demeo.load_templates()`` function,
    which returns a ``dict`` containing the classes as keys and the template spectra as values.

  .. tab-item:: Preprocessing

    The following preprocessing steps are automatically done when using the ``classy.Spectrum.classify()``
    method:

    - :ref:`Feature Detection <feature_detection>`

    - :ref:`Resampling <resampling>` to common wavelength grid

    - :ref:`Remove the slope <slope_removal>` of the spectrum

    - :ref:`Normalisation <norm_mixnorm>` to 0.55μm

    The preprocessing does not change the ``wave`` and ``refl`` attributes of the
    spectrum.

  .. tab-item:: Classification

    The decision tree outlined in Appendix B in DeMeo+ 2009 is used to compute
    the class based on the principal scores and the slope of the spectrum.
    Several branches of the tree end in multiple classes and require the user
    to inspect the presence of features. ``classy`` automatically does this.
    The feature detection is not perfect and visual inspection is encouraged.

    Other branches do not have a clear distinction defined. For example, a
    spectrum might either be a D- or an A-type depending on its scores.

    In this case, ``classy`` makes use of the class templates by computing the
    correlation coefficient between the spectrum and the (slope-removed) class
    templates. This is applied to differentiate D and A, C and X,

    The resulting class is assigned to the ``class_demeo`` attribute. The principal
    components scores are accessible via the ``scores_demeo`` attribute.

    .. code-block:: bash

       $ classy spectra nysa --classify --taxonomy demeo --source MITHNEOS

    .. image:: gfx/taxonomies/nysa_demeo.png
       :align: center
       :class: only-light
       :width: 800

    .. image:: gfx/taxonomies/nysa_demeo_dark.png
       :align: center
       :class: only-dark
       :width: 800

.. Sidenote: The missing data mean
.. +++++++++++++++++++++++++++++++
..
.. As DeMeo+ 2009 demeaned the reflectance spectra prior to the PCA, **the same
.. mean value** of each reflectance bin has to subtracted from new reflectance
.. spectra to be projected into the same principal space. I could not find the
.. original mean values in the source publication\ [#f3]_, so I computed it myself
.. using the spectra from DeMeo+ 2009 and give it here for completeness:
..
.. .. code-block:: python
..
..    [0.8840578, 0.94579985, 1.04016798, 1.07630094, 1.10387232, 1.10729138,
..     1.07101476, 1.02252107, 0.99167561, 0.98766575, 1.00292349, 1.02223844,
..     1.04660108, 1.07201578, 1.08967345, 1.10014259, 1.11101667, 1.12359452,
..     1.13128556, 1.13642896, 1.13467689, 1.12810013, 1.11471935, 1.09802574,
..     1.07842635, 1.06127665, 1.04536074, 1.03360292, 1.02395605, 1.01587389,
..     1.01034821, 1.00915786, 1.01078308, 1.01245031, 1.01298133, 1.01314109,
..     1.01236654, 1.01140562, 1.01090655, 1.00955344]
..
.. Note that this is not the exact mean as I did not have the original spectra of
.. (41) *Daphne*, (82) *Alkmene*, and (3788) *Steyaert*. However, compared to the
.. published scores, I get an average difference of 0.0003 using scores I compute
.. with this data mean, which is sufficiently accurate for any purposes.
