Classifying Spectra
===================

``classy`` can taxonomically classify asteroid spectra and return the
classification results as well as visualize them. Classification results might
be more reliable after :ref:`preprocessing <preprocessing>` the spectra and
:ref:`identifying features <features>` relevant for the class assignment. All
tasks can be done via the command line interface and the ``python`` interface.


.. tab-set::

    .. tab-item:: Command Line

        Classify all available spectra of (4) *Vesta*.

        .. code-block:: shell

           $ classy classify vesta

        By default, this prints a table of available spectra and their classification result. Use the ``--plot`` flag
        to visualise the classification result.

    .. tab-item:: python

        Classify all available spectra of (4) *Vesta*.

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(4)
           >>> spectra.classify()

        ``classy`` automatically applies the required preprocessing (e.g. normalising,
        resampling) for the respective taxonomic scheme. This happens "under the hood"
        and does not change the ``wave`` and ``refl`` attributes of the ``Spectrum``.

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
and the resulting class is an empty string ``""``.\ [#f1]_
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

By default, only the spectra themselves are plotted. If you specify the ``taxonomy``
keyword, the classification results in the specified taxonomic system are added to the
figure. Note that you have to call ``.classify()`` before.

.. code-block:: python

    >>> spectra.classify()  # taxonomy='mahlke' is default
    >>> spectra.classify(taxonomy='demeo')
    >>> spectra.plot(taxonomy='mahlke')  # show classification results following Mahlke+ 2022
    >>> spectra.plot(taxonomy='demeo')  # show classification results following DeMeo+ 2009

By providing a filename to the ``save`` argument, you can instruct ``classy`` to save the figure
to file instead of opening it.

.. code-block:: python

    >>> spectra.plot(save='figures/vesta_classified.png')

Exporting the Result
--------------------

Both ``Spectrum`` and ``Spectra`` have a ``to_csv`` method which allows storing
the classification results to ``csv`` format.

.. code-block:: python

   >>> import classy
   >>> spectra = classy.Spectra(3)
   ...  [classy] Found 1 spectrum in Gaia
   ...  [classy] Found 5 spectra in SMASS
   >>> spectra.classify()
   ...  [classy] [(3) Juno] - [Gaia]: S
   ...  [classy] [(3) Juno] - [spex/sp96]: S
   ...  [classy] [(3) Juno] - [smass/smassir]: S
   ...  [classy] [(3) Juno] - [smass/smass1]: S
   ...  [classy] [(3) Juno] - [smass/smass2]: S
   ...  [classy] [(3) Juno] - [smass/smass2]: S
   >>> spectra.to_csv('class_juno.csv')

.. rubric:: Footnotes
   :caption:


.. [#f1] If the missing part represents less than a given limit, the spectrum
   will be extrapolated linearly to cover the required range for
   classification. This is most useful for the Gaia DR3 spectra (0.374 - 1.034μm) and the Tholen
   taxonomy (0.337 - 1.041µm). More on this limit and its configuration can be found :ref:`here
   <extrapolation_limit>`.
