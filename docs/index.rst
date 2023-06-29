##########
``classy``
##########

.. |br| raw:: html

     <br>

.. raw:: html

    <style> .gray {color:#979eab} </style>

.. role:: gray


A ``python`` tool to classify asteroid reflectance spectra in the framework of the
asteroid taxonomy presented in `Mahlke, Carry, and Mattei 2022
<https://arxiv.org/abs/2203.11229>`_ and to compare with spectra in
public repositories (e.g. Gaia, SMASS, MITHNEOS).\ [#f1]_

.. image:: gfx/ceres_classification.png
 :align: center
 :class: only-light
 :width: 1000

.. image:: gfx/ceres_classification_dark.png
 :align: center
 :class: only-dark
 :width: 1000

.. card:: → Classify Your Observation
    :text-align: center
    :link: https://example.com

.. highlight:: python


|br|

:octicon:`telescope;1em` **Quick query and download of reflectance spectra in public repositories**.


.. grid:: 2

    .. grid-item-card::
      :link: public_data
      :link-type: ref

      Quick look-up and visualization of public spectra in different repositories.


    .. grid-item-card::
      :link: available_data
      :link-type: ref

      Automatic ingestion of relevant metadata such as flags and bibliographic
      references.

|br|
:octicon:`beaker;1em` **Taxonomic classification of reflectance spectra.**

.. grid:: 2

    .. grid-item-card::
      :link: core
      :link-type: ref

      Classify your own and public observations.


    .. grid-item-card::
      :link: plotting
      :link-type: ref

      Visualize the classification results and store them to file.

|br|

:octicon:`zap;1em` **And more!**

.. grid:: 2

    .. grid-item-card::
      :link: getting_data
      :link-type: ref

      Automatic retrieval of most-likely visual albedo to improve classification
      accuracy.

    .. grid-item-card::
      :link: available_data
      :link-type: ref

      Are my spectra available through ``classy``?

.. rubric:: Footnotes
   :caption:


.. [#f1] Latest version: 0.5  - `What's new? <https://github.com/maxmahlke/classy/blob/master/CHANGELOG.md>`_  | Comment, bug or feature request? `Email me <https://www.ias.universite-paris-saclay.fr/annuaire?nom=mahlke>`_ or open an issue on `GitHub <https://github.com/maxmahlke/classy/issues>`_.

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   Home<self>
   Install<getting_started>
   Basic Usage<core>
   Public Data<data>
   Taxonomies<taxonomies>
   Tutorials<tutorial>
.. glossary
