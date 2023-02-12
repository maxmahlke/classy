.. _taxonomy:

Classifying Asteroids
=====================

``classy`` is developed to facilitate the application of the `Mahlke+ 2022
<https://arxiv.org/abs/2203.11229>`_ taxonomy to asteroid reflectance spectra.
A brief overview of the taxonomy:

+-------------------+------------------------------------------+
| Observables       | Reflectance Spectra, Visual Albedo       |
+-------------------+------------------------------------------+
| Wavelength Range  | 0.45-2.45µm, or any subset of this range |
+-------------------+------------------------------------------+
| Number of Classes | 16                                       |
+-------------------+------------------------------------------+
| Class Assignment  | Probabilistic                            |
+-------------------+------------------------------------------+

The three main advantages of the Mahlke+ 2022 over previous systems are the large number
of observables (visible and near-infrared spectra and the visual albedo),
the ability to classify partial observations (e.g. visible-only spectra), and the probabilistic
classification results (e.g. 70% S, 30% A).


.. image:: gfx/class_overview.png
   :align: center
   :class: only-light
   :width: 600


.. image:: gfx/class_overview_dark.png
   :align: center
   :class: only-dark
   :width: 600

Classifying asteroids in this scheme is straight-forward with ``classy``.

.. tab-set::

  .. tab-item:: Command Line

      Provide the ``--classify`` (or the shorter ``-c``) flag to ``classy
      spectra``. The figure shows the input data (the original spectra and the spectra after smoothing
      and resampling; the visual albedo) and the classification results
      (histogram of class probabilities).

      .. code-block:: bash

          $ classy spectra ceres --classify

      .. image:: gfx/ceres_classification.png
         :align: center
         :class: only-light
         :width: 600

      .. image:: gfx/ceres_classification_dark.png
         :align: center
         :class: only-dark
         :width: 600

  .. tab-item :: python

     .. By default, ``Spectrum.classify`` classifies the spectrum in the Mahlke+ 2022 taxonomic system. You can choose different systems using the ``system`` argument.
     .. The possible values are ["Tholen", "Bus", "DeMeo", "Mahlke"].
     .. code-block:: python

       >>> import classy
       >>> spectra = classy.spectra("ceres")
       >>> spectra.classify()

     The classification results are stored as attributes: the ``.class_``
     attribute contains the most probable class (``str``), while ``.class_A`` contains the
     probability of the spectrum to belong to class A, ``class_B`` to class B,
     and so forth.

     .. code-block:: python

        >>> for spec in spectra:
        ...     print(f"[{spec.name}] Most likely class: {spec.class_}")
        ...     print(f"[{spec.name}] Probability to be a B-type: {spec.class_B}")
        [Gaia] Most likely class: C
        [Gaia] Probability to be a B-type: 0.010117828845977783
        [spex/sp41] Most likely class: C
        [spex/sp41] Probability to be a B-type: 0.21453788876533508
        [spex/dm04] Most likely class: C
        [spex/dm04] Probability to be a B-type: 0.10440362244844437
        [smass/smassir] Most likely class: B
        [smass/smassir] Probability to be a B-type: 0.8728849114730683
        [smass/smass2] Most likely class: C
        [smass/smass2] Probability to be a B-type: 0.006173321977258222
        [smass/smass2] Most likely class: C
        [smass/smass2] Probability to be a B-type: 0.006204487290234007
