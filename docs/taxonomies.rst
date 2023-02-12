.. _available_taxonomies:

Taxonomic Systems
=================

``classy`` is developed to facilitate the application of the `Mahlke+ 2022
<https://arxiv.org/abs/2203.11229>`_ taxonomy to asteroid reflectance spectra.
Nevertheless, it can also be used to classify observations in three other
systems: `Tholen 1984
<https://ui.adsabs.harvard.edu/abs/1984PhDT.........3T/abstract>`_, `Bus and
Binzel 2002 <https://ui.adsabs.harvard.edu/abs/2002Icar..158..146B/abstract>`_,
`DeMeo+ 2009
<https://ui.adsabs.harvard.edu/abs/2009Icar..202..160D/abstract>`_. The main properties of all four
systems are summarized below, focusing on their applicability to data with given properties.

For an in-depth overview of the history of asteroid taxonomies, you can have a look `at this timeline <https://raw.githubusercontent.com/maxmahlke/maxmahlke/main/docs/mahlke_taxonomy_timeline.pdf>`_.

Mahlke+ 2022
------------

+-------------------+------------------------------------------+
| Observables       | Reflectance Spectra, Visual Albedo       |
+-------------------+------------------------------------------+
| Wavelength Range  | 0.45-2.45µm, or any subset of this range |
+-------------------+------------------------------------------+
| Number of Classes |                                          |
+-------------------+------------------------------------------+
| Class Assignment  | Probabilistic                            |
+-------------------+------------------------------------------+

The three main advantages of the Mahlke+ 2022 taxonomies are the large number
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


.. tab-set::

  .. tab-item:: Command Line

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

     .. code-block:: python

       >>> import classy
       >>> spectra = classy.spectra("ceres")
       >>> for spec in spectra:
       ...     spec.classify() # system="Mahlke+ 2022" is the default
       >>> classy.plotting.plot_spectra(spectra, add_classes=True)


DeMeo+ 2009
-----------

PCA
Reflectance spectra
Complete between 0.45 to 2.45
25 classes


.. image:: gfx/classes_demeo.png
   :align: center
   :class: only-light
   :width: 500



.. image:: gfx/classes_demeo_dark.png
   :align: center
   :class: only-dark
   :width: 500

Bus and Binzel 2002
-------------------

PCA
Reflectance spectra
Complete between 0.45 to ?
22 classes

Tholen 1984
-----------

Reflectance spectra - UV
Albedo
PCA + decision tree
Complete spectra
14 classes
