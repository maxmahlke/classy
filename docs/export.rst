:tocdepth: 2

.. _export:

Plotting And Exporting
======================

Templates


Storing to file
---------------

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

.. _plotting:

Plotting
--------

.. tab-set::

    .. tab-item:: Command Line

        The quickest way to visualize spectra of an asteroids is the command line.

        .. code-block:: shell

           $ classy spectra vesta

        This will open a plot of the spectra. You can further instruct to ``-c|--classify``
        the spectra in a given ``-t|--taxonomy``.

        .. code-block:: shell

           $ classy spectra vesta -c   # '--taxonomy mahlke' is the default
           $ classy spectra vesta -c --taxonomy tholen

        To only use spectra from one or many sources, use ``-s|--source``.

        .. code-block:: shell

           $ classy spectra vesta -c --taxonomy tholen --source ECAS --source Gaia

        If you set ``--save``, the figure is stored in the current working directory.

        .. code-block:: shell

           $ classy spectra vesta -c --taxonomy tholen --source ECAS --source Gaia --save
           INFO     [classy] Figure stored under sources/4_Vesta_classy.png

    .. tab-item:: python

        Both a ``Spectrum`` and many ``Spectra`` can be plotted using the ``.plot()`` method.

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(43)
           >>> spectra.plot()

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
