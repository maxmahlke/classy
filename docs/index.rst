##########
``classy``
##########

.. |br| raw:: html

     <br>

.. raw:: html

    <style> .gray {color:#979eab} </style>

.. role:: gray

.. TODO: Update the general description once feature complete

A ``python`` tool to classify asteroid reflectance spectra in the framework of the
asteroid taxonomy presented in `Mahlke, Carry, and Mattei 2022
<https://arxiv.org/abs/2203.11229>`_ and to compare with spectra in
public repositories.\ [#f1]_

.. image:: gfx/ceres_classification.png
 :align: center
 :class: only-light
 :width: 1000

.. image:: gfx/ceres_classification_dark.png
 :align: center
 :class: only-dark
 :width: 1000


.. highlight:: python


|br|

:octicon:`telescope;1em` **Your spectra or the ones from public repositories**.

.. grid:: 2

    .. grid-item-card::
      :link: public_data
      :link-type: ref

      Who has observed spectra of (13) *Egeria*? In which wavelength range?


    .. grid-item-card::
      :link: public_data
      :link-type: ref

      Automatic ingestion of relevant metadata such as flags and bibliographic
      references.

|br|
:octicon:`beaker;1em` **Taxonomic classification and more.**

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

:octicon:`zap;1em` **Less ugh, more fun!**

.. grid:: 2

    .. grid-item-card::
      :link: getting_data
      :link-type: ref

      Automatic retrieval of albedo and computation of phase angle.

    .. grid-item-card::
      :link: public_data
      :link-type: ref

      Preprocess a spectrum once and then never again.



.. .. card:: Classify Your Observation →
..     :text-align: center
..     :link:

.. rubric:: Footnotes
   :caption:


.. [#f1] Latest version: 0.7.1  - `What's new? <https://github.com/maxmahlke/classy/blob/master/CHANGELOG.md>`_  | Comment, bug or feature request? `Email me <https://www.ias.universite-paris-saclay.fr/annuaire?nom=mahlke>`_ or open an issue on `GitHub <https://github.com/maxmahlke/classy/issues>`_.

.. toctree::
   :maxdepth: 2
   :hidden:

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
