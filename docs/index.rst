##########
``classy``
##########

.. |br| raw:: html

     <br>

.. raw:: html

    <style> .gray {color:#979eab} </style>

.. role:: gray

A tool to acquire, explore, analyse, and classify asteroid reflectance spectra. Originally designed for classification in the taxonomy of
`Mahlke, Carry, and Mattei 2022 <https://arxiv.org/abs/2203.11229>`_, it now offers multiple taxonomic systems and a suite of qualitfy-of-life features
for spectroscopic analysis.\ [#f1]_

.. image:: gfx/ceres_classification.png
 :align: center
 :class: only-light
 :width: 1000

.. image:: gfx/ceres_classification_dark.png
 :align: center
 :class: only-dark
 :width: 1000

.. card:: Classify Your Observation →
  :text-align: center
  :link: https://google.com

  Coming soon.

.. highlight:: python

|br|

:octicon:`telescope;1em` **Explore and compare.**

link to examples of:

select syntax
combination of own and literature data
feature detection
public data
classification
plotting and exporting or preprocessing

.. grid:: 2

    .. grid-item-card::
      :link: public_data
      :link-type: ref

      I have observed a spectrum of (13) *Egeria*. Who else has observed this asteroid?
      In what wavelength ranges?


      Search and explore public spectra based on spectra- and target properties.
      68,250 public spectra and counting.


    .. grid-item-card::
      :link: public_data
      :link-type: ref

      How do my spectra of the *Polana* family compare to those in the literature?

      Combine spectra in your analysis.
      Full bibliographic references and ingestion of metadata of public spectra.

|br|
:octicon:`beaker;1em` **Analyse and classify.**

.. grid:: 2

    .. grid-item-card::
      :link: core
      :link-type: ref

      Which public spectra show hydration features?

      Persistent pre-processing and Feature inspection


    .. grid-item-card::
      :link: plotting
      :link-type: ref

      What taxonomic class is my spectrum according to Tholen 1984, DeMeo+ 2009,
      and Mahlke+ 2022?

      Taxonomic classification in multiple systems

|br|

:octicon:`zap;1em` **Less ugh, more fun!**

.. grid:: 2

    .. grid-item-card::
      :link: getting_data
      :link-type: ref

      Automatic retrieval of target properties such as albedo, family, and computation of phase angle at epoch of observation.

    .. grid-item-card::
      :link: public_data
      :link-type: ref

      Preprocess a spectrum once and then never again.
      Simple and intuitive syntax.



.. rubric:: Footnotes
   :caption:


.. [#f1] Latest version: 0.7.1  - `What's new? <https://github.com/maxmahlke/classy/blob/master/CHANGELOG.md>`_  | Comment, bug or feature request? `Email me <https://www.ias.universite-paris-saclay.fr/annuaire?nom=mahlke>`_ or open an issue on `GitHub <https://github.com/maxmahlke/classy/issues>`_.

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Welcome to classy

   Home<self>
   Getting Started<getting_started>

.. toctree::
   :maxdepth: 2
   :caption: Spectra Analysis
   :hidden:

   Basic Usage<core>
   Selecting Spectra<select>
   Preprocessing<preprocessing>
   Feature Detection<features>
   Classifying<classifying>
   Plotting and Exporting<export>

.. toctree::
   :maxdepth: 2
   :caption: Data and Taxonomies
   :hidden:

   Public Data<data>
   Private Data<private>
   Taxonomies<taxonomies>

.. toctree::
   :maxdepth: 2
   :caption: Reference
   :hidden:

   Tutorials<tutorial>
   Configuration<configuration>
   Appendix<appendix>

.. glossary

.. Advanced Usage<advanced>
