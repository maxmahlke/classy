Classifying Spectra
===================

This chapter assumes that you are familiar with the syntax of :ref:`selecting spectra <selecting_spectra>`.
Classification results might be more reliable after :ref:`preprocessing <preprocessing>` the spectra and :ref:`identifying
features <features>` relevant for the class assignment.

``classy`` can taxonomically classify asteroid spectra and return the
classification results as well as visualize them. All tasks can be done via the
command line interface and the ``python`` interface.

.. tab-set::

    .. tab-item:: Command Line

        Classify all available spectra of (4) *Vesta*.

        .. code-block:: shell

           $ classy classify vesta

        By default, this prints a table of available spectra and their classification result.

    .. tab-item:: python

        Classify all available spectra of (4) *Vesta*.

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(4)
           >>> spectra.classify()

        Iterate over the list of spectra to inspect the classification result:

        .. code-block:: python

           >>> for spec in spectra:
           >>>     print(f"Spectrum of {spec.shortbib} is of class {spec.class_}")

Taxonomy Selection
------------------

Asteroids can be classified in different taxonomic schemes. The chosen scheme
affects the classification procedure (preprocessing steps and classification
logic), the required wavelength range of the spectra, and the classification
output. ``classy`` takes care of the first point, so only the last two points
are relevant for you. You can find an overview of the currently supported
taxonomies and their basic properties :ref:`here <taxonomies>`. To select
the scheme of your choice, use the ``taxonomy`` argument.

+--------------+-----------------------+
| Taxonomy     | Argument Value        |
+--------------+-----------------------+
| Mahlke+ 2022 |  ``mahlke``           |
+--------------+-----------------------+
| DeMeo+ 2009  | ``demeo``             |
+--------------+-----------------------+
| Tholen 1984  | ``tholen``            |
+--------------+-----------------------+

The default value is ``mahlke``.


.. TODO: Add example of classification of spectrum in different schemes, some X type

.. tab-set::

    .. tab-item:: Command Line

        .. code-block:: shell

           $ classy classify vesta --taxonomy demeo

    .. tab-item:: python

        .. code-block:: python

           >>> spectra.classify(taxonomy="demeo")

        The results of the **last** classification is stored in ``class_``. In case you use different schemes for comparison,
        you can access the results using ``class_mahlke``, ``class_demeo``, ``class_tholen``.

        .. code-block:: python

           >>> spectra.classify(taxonomy="demeo")
           >>> spec.class_demeo

If a spectrum cannot be classified in the chosen scheme due to :ref:`insufficient wavelength coverage <taxonomies>`, a warning is printed
and the resulting class is an empty string ``""``.

Classification by-products like principal component scores and class probabilities are also available depending on the chosen taxonomy.
The products of each scheme can be found in the relevant sections of the :ref:`overview <taxonomies>`.

All implemented schemes benefit from knowing the albedo of the target. For ``mahlke`` and ``tholen``, this heavily
influences the resulting classification. For ``demeo``, ``classy`` uses the albedo to resolve branches of the original decision tree
that are unresolved in DeMeo+ 2009, in case the classes are reliably different in albedo (e.g. D and S).

A ``classy.Spectrum`` can be classified following different taxonomies using the ``.classify()``
function. The ``taxonomy`` argument can be used to choose between different taxonomies.

.. code-block:: python

   >>> import classy
   >>> ceres = classy.Spectra(1, source='Gaia')[0]
   >>> ceres.classify() # taxonomy='mahlke' is default
   >>> ceres.classify(taxonomy='tholen') # Tholen 1984 (requires extrapolation)
   >>> ceres.classify(taxonomy='demeo') # DeMeo+ 2009 (fails due to wavelength range)

The resulting class is added as ``class_`` attribute to the spectrum. For
``tholen`` and ``demeo``, the attributes are ``class_tholen`` and
``class_demeo`` respectively. Further added attributes depending on the chosen
taxonomy are described in the :ref:`taxonomies <available_taxonomies>` section.

Visualizing the Result
----------------------

Exporting the Result
--------------------
