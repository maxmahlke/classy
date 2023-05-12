.. _available_taxonomies:

Taxonomies
==========

``classy`` is developed to facilitate the application of the `Mahlke+ 2022
<https://arxiv.org/abs/2203.11229>`_ taxonomy to asteroid reflectance spectra.
Nevertheless, it can also be used to classify observations in other
systems: `Tholen 1984 <https://ui.adsabs.harvard.edu/abs/1984PhDT.........3T/abstract>`_
and `DeMeo+ 2009
<https://ui.adsabs.harvard.edu/abs/2009Icar..202..160D/abstract>`_.\ [#f1]_ The
main properties of all systems are summarized below, focusing on their
applicability to data with given properties.

.. include:: taxonomies/mahlke.rst

.. include:: taxonomies/demeo.rst

.. include:: taxonomies/tholen.rst

.. rubric:: Footnotes
   :caption:

.. [#f1] For an in-depth overview of the history of asteroid taxonomies, you can have a look `at this timeline <https://raw.githubusercontent.com/maxmahlke/maxmahlke/main/docs/mahlke_taxonomy_timeline.pdf>`_.
.. [#f2] The Xn class added in Binzel+ 2019 is not included as the k- and n-features are too similar to be separated automatically.
.. [#f3] If you think a different algorithm is more appropriate, let's discuss.
