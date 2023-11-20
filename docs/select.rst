.. _selecting_spectra:

Selecting Spectra
=================

``classy`` makes it easy to select a set of spectra based on properties of
either the spectra (e.g. wavelength range, feature presence) or the targets
(e.g. taxonomic class, family membership). After :ref:`adding spectra to the
classy database<adding_spectra>`, you can select spectra by specifying any
combination of desired properties and values. You can do this on the command
line using the ``spectra`` command to explore and visualize, and in a
``python`` script using the ``Spectra`` class for a more detailed analysis,
covered in later chapters of this documentation.

.. tab-set::

    .. tab-item:: Command Line

        List all available spectra of (4) *Vesta*.

        .. code-block:: shell

           $ classy spectra vesta

        By default, this prints a table of available spectra and relevant metadata.

    .. tab-item:: python

        Retrieve all available spectra of (4) *Vesta*.

        .. code-block:: python

           >>> import classy
           >>> classy.Spectra(4)

.. _selection_syntax:

Selection Syntax
----------------

All queries have the following basic syntax:

``[Zero, one, or many target identifiers] [property1 name] [property1 value] [property2 name] [property2 value] [...]``

The first part allows to specify any number of targets directly by passing an `identifier <https://rocks.readthedocs.io/en/latest/glossary.html#term-Identifier>`_:

.. tab-set::

    .. tab-item:: Command Line

        Get all spectra of specified targets.

        .. code-block:: shell

            $ classy spectra vesta             # (4) Vesta
            $ classy spectra 12 21             # (12) Victoria, (21) Lutetia
            $ classy spectra julia sylvia 283  # (87) Sylvia, (89) Julia, (283) Emma

    .. tab-item:: python

        Get all spectra of specified targets.

        .. code-block:: python

            >>> classy.Spectra("vesta")                  # (4) Vesta
            >>> classy.Spectra([12, 21])                 # (12) Victoria, (21) Lutetia
            >>> classy.Spectra(["julia", "sylvia", 283]) # (87) Sylvia, (89) Julia, (283) Emma

This target selection can be combined with or replaced by queries based on the
spectra and target properties. Accepted property names are explained
:ref:`below <selection_criteria>`. If the property is numeric (e.g. the target's albedo),
you can specify lower and upper limits by separating them with a comma: ``,``. To
specify a one-sided limit, leave one side of the ``,`` blank.


.. tab-set::

    .. tab-item:: Command Line

        Spectra of targets with albedos between 0.03 and 0.04.

        .. code-block:: shell

            $ classy spectra --albedo 0.03,0.04

        Spectra observed at phase angles below 10 degree.

        .. code-block:: shell

            $ classy spectra --phase ,10

    .. tab-item:: python

        Spectra of targets with albedos between 0.03 and 0.04.

        .. code-block:: python

            >>> classy.Spectra(albedo="0.03,0.04")

        Spectra observed at phase angles below 10 degree.

        .. code-block:: python

            >>> classy.Spectra(phase=',10')

An exception are the minimum and the maximum observed wavelength ``wave_min`` and ``wave_max``,
which are upper and lower limits by default.

.. tab-set::

    .. tab-item:: Command Line

        Get spectra of (22) *Kalliope* which cover the entire visible-near-infrared range (0.45-2.45μm).

        .. code-block:: shell

           $ classy spectra 22 --wave_min 0.45 --wave_max 2.45

    .. tab-item:: python

        Get spectra of (22) *Kalliope* which cover the entire visible-near-infrared range (0.45-2.45μm).

        .. code-block:: python

           >>> classy.Spectra(22, wave_min=0.45, wave_max=2.45)


For categorical values (e.g. taxonomy), you can select multiple acceptable
values by separating them with a ``,``.

.. tab-set::

    .. tab-item:: Command Line

        Spectra of B- and C-types with albedos above 0.1.

        .. code-block:: shell

            $ classy spectra --albedo 0.1, --taxonomy B,C

    .. tab-item:: python

        Spectra of B- and C-types with albedos above 0.1.

        .. code-block:: python

            >>> classy.Spectra(albedo="0.1,", taxonomy="B,C")

Finally, you can express all queries in a logical format passed to the ``query`` parameter.
This enables quite complex selection patterns.

.. tab-set::

    .. tab-item:: Command Line

        Spectra of B- and C-types with minimum wavelengths below 0.3μm.

        .. code-block:: shell

           $ classy spectra --wave_min 0.3 --taxonomy B,C
           $ classy spectra --query "wave_min < 0.3 & (taxonomy == 'B' | taxonomy == 'C')" # equivalent

        Spectra of Tirela and Watsonia family members that are not L-types

        .. code-block:: shell

            $ classy spectra --family Tirela,Watsonia --query "taxonomy != 'L'"

    .. tab-item:: python

        Spectra of B- and C-types with minimum wavelengths below 0.3μm.

        .. code-block:: python

           >>> classy.Spectra(wave_min=0.3, taxonomy="B,C")
           >>> classy.Spectra(query="wave_min < 0.3 & (taxonomy == 'B' | taxonomy == 'C')") # equivalent

        Spectra of Tirela and Watsonia family members that are not L-types

        .. code-block:: python

            >>> classy.Spectra(family="Tirela,Watsonia", query="taxonomy != 'L'")


You can learn more about the query syntax `here <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html#pandas.DataFrame.query>`_.


.. _selection_criteria:

Selection Criteria
------------------

Selection criteria for spectra can be divided into spectra-specific (e.g. wavelength range, phase angle)
and target-specific (e.g. taxonomy, albedo).

Spectra-Specific
++++++++++++++++

``classy`` keeps an index of all spectra and the relevant metadata in its
database. Spectra-specific queries can make use of this metadata:

+--------------+-----------------------------------------------+----------------------------------------------------------+
| Property     | Description                                   | Example                                                  |
+==============+===============================================+==========================================================+
| ``wave_min`` | Minimum observed wavelength in μm             | ``$ classy spectra eos --wave_min 0.4``                  |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``wave_max`` | Maximum observed wavelength in μm             | ``$ classy spectra eos --wave_max 1.2``                  |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``phase``    | Phase angle of target at epoch of observation | ``$ classy spectra --phase 0,20``                        |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``source``   | Source of spectrum (e.g. survey like 'Gaia')  | ``$ classy spectra ceres pallas --source MITHNEOS,Gaia`` |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``shortbib`` | Shortbib of source publication                | ``$ classy spectra  --shortbib "Marsset+ 2014"``         |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``date_obs`` | Epoch of observation                          | ``$ classy spectra bennu --date_obs 2008,``              |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``N``        | Number of wavelength samples in spectrum      | ``$ classy spectra vesta --N 500,``                      |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``feature``  | Presence of given feature in spectrum         | ``$ classy spectra egeria --feature h``                  |
+--------------+-----------------------------------------------+----------------------------------------------------------+

Selecting based on feature presence can be done after populating the
feature index via the :ref:`feature detection
<features>` interface. The ``feature`` property one or several of the
``e``, ``h``, and ``k`` features.

.. tab-set::

    .. tab-item:: Command Line

        Spectra of Polana family members which have a 0.7μm band.

        .. code-block:: shell

           $ classy spectra --feature h --family Polana

    .. tab-item:: python

        Spectra of Polana family members which have a 0.7μm band.

        .. code-block:: python

           >>> classy.Spectra(family="Polana", feature="h")

Target-Specific
+++++++++++++++

When selecting spectra based on properties of the targets (e.g. taxonomy,
albedo), ``classy`` uses `rocks <https://github.com/maxmahlke/rocks>`_ to
identify targets fitting these criteria via the `SsODNet ssobft
<https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/>`_, a table containing a
large number of best-estimate properties of all known minor bodies.\ [#f1]_
Valid selection criteria are all `columns in the ssoBFT
<https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/>`_, specified using the
entire column name. Due to the ``.`` in the ssoBFT column names, queries using the ``python`` interface
have to use the ``query`` parameter.

.. tab-set::

    .. tab-item:: Command Line

        Get spectra of potentially hazardous objects.

        .. code-block:: shell

            $ classy spectra --moid.EMB.value ,005 --H ,22

    .. tab-item:: python

        Get spectra of potentially hazardous objects.

        .. code-block:: python

            >>> classy.Spectra(query='moid.EMB.value <= 0.05', H=',22')

Frequently used target properties can be specified using shorthands, analogously to the spectra metadata:\ [#f2]_

+--------------+--------------------+-------------------------------------------------+
| Property     | Description        | Example                                         |
+==============+====================+=================================================+
| ``albedo``   | Visual albedo      | ``$ classy spectra --albedo 0.3,``              |
+--------------+--------------------+-------------------------------------------------+
| ``diameter`` | Diameter in km     | ``$ classy spectra --diameter ,10``             |
+--------------+--------------------+-------------------------------------------------+
| ``family``   | Family name        | ``$ classy spectra --family Hungaria,Eos``      |
+--------------+--------------------+-------------------------------------------------+
| ``H``        | Absolute Magnitude | ``$ classy spectra --H 16.3,17``                |
+--------------+--------------------+-------------------------------------------------+
| ``taxonomy`` | Taxonomic class    | ``$ classy spectra --taxonomy D,Z``             |
+--------------+--------------------+-------------------------------------------------+

.. [#f1]  The first query may trigger the download of the ssoBFT (~450MB) to your computer. More information can be found `here <https://rocks.readthedocs.io/en/latest/cli.html#access-of-ssobft>`_.
.. [#f2]  Your favourite property could use a shorthand form? Request it `here <https://github.com/maxmahlke/classy/issues>`_ or via email.
