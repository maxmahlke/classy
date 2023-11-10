Selecting Spectra
=================

``classy`` makes it easy to select a set of spectra based on properties
of either the spectra (e.g. wavelength range, feature presence) or the targets
(e.g. taxonomic class, family membership). After :ref:`adding spectra to the
classy database<adding_spectra>`, you can select the spectra of interest by specifying
any combination of desired properties and values. You can do this on the command line using the ``spectra`` command
and in a ``python`` script using the ``Spectra`` class.

.. tab-set::

    .. tab-item:: Command Line

        Get all spectra of asteroid (4) Vesta.

        .. code-block:: shell

           $ classy spectra vesta

    .. tab-item:: python

        Get all spectra of asteroid (4) Vesta.

.. _selection_criteria:

Selection Criteria
------------------

Selection criteria for spectra can be divided into spectra-specific (e.g. wavelength range, phase angle)
and target-specific (e.g. taxonomy, albedo).

``classy`` keeps an index of all spectra and the
relevant metadata in its database. Spectra-specific queries can make use of this metadata (the syntax used in the example queries is explained :ref:`below <selection_syntax>`):

+--------------+-----------------------------------------------+----------------------------------------------------------+
| Property     | Description                                   | Example                                                  |
+==============+===============================================+==========================================================+
| ``wave_min`` | Minimum observed wavelength in μm             | ``$ classy spectra eos --wave_min 0.2,0.4``              |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``wave_max`` | Maximum observed wavelength in μm             | ``$ classy spectra eos --wave_max ,1.2``                 |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``phase``    | Phase angle of target at epoch of observation | ``$ classy spectra --phase 0,20``                        |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``source``   | Source of spectrum (e.g. survey like 'Gaia')  | ``$ classy spectra ceres,pallas --source MITHNEOS,Gaia`` |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``shortbib`` | Shortbib of source publication                | ``$ classy spectra  --shortbib "Marsset+ 2014``          |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``date_obs`` | Epoch of observation                          | ``$ classy spectra bennu --date_obs 2008-08-01,``        |
+--------------+-----------------------------------------------+----------------------------------------------------------+
| ``N``        | Number of wavelength samples in spectrum      | ``$ classy spectra vesta --N 500,``                      |
+--------------+-----------------------------------------------+----------------------------------------------------------+

When selecting spectra based on properties of the targets (e.g. taxonomy,
albedo), ``classy`` uses `rocks <https://github.com/maxmahlke/rocks>`_ to
identify targets fitting these criteria via the `SsODNet ssobft
<https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/>`_, a table containing a
large number of best-estimate properties of all known minor bodies.\ [#f1]_
Valid selection criteria are all `columns in the ssoBFT
<https://ssp.imcce.fr/webservices/ssodnet/api/ssobft/>`_, specified using the
entire column name.

.. tab-set::

    .. tab-item:: Command Line

        Get all spectra of asteroid (4) Vesta.

        .. code-block:: shell

            $ classy spectra --moid.EMB.value ,005

    .. tab-item:: python

        Get all spectra of asteroid (4) Vesta.

        .. code-block:: python

            >>> classy.Spectra(query='moid.EMB.value <= 0.05')

Frequently used target properties can be specified using shorthands, analogously to the spectra metadata:

+--------------+--------------------+-------------------------------------------------+
| Property     | Description        | Example                                         |
+==============+====================+=================================================+
| ``albedo``   | Visual albedo      | ``$ classy spectra --albedo 0.3,``              |
+--------------+--------------------+-------------------------------------------------+
| ``diameter`` | Diameter in km     | ``$ classy spectra --diameter ,10``             |
+--------------+--------------------+-------------------------------------------------+
| ``family``   | Family name        | ``$ classy spectra --family hungaria,eos``      |
+--------------+--------------------+-------------------------------------------------+
| ``H``        | Absolute Magnitude | ``$ classy spectra --H 16.3,17``                |
+--------------+--------------------+-------------------------------------------------+
| ``taxonomy`` | Taxonomic class    | ``$ classy spectra --taxonomy D,Z``             |
+--------------+--------------------+-------------------------------------------------+

.. _selection_syntax:

Selection Syntax
----------------

All queries have the following basic syntax:

``[Zero, one, or many target identifiers] [property1 name] [property1 value] [property2 name] [property2 value] [...]``

The first part allows to specify any number of targets directly by passing an `identifier <https://rocks.readthedocs.io/en/latest/glossary.html#term-Identifier>`_.

.. tab-set::

    .. tab-item:: Command Line

        .. code-block:: shell

            $ classy spectra vesta             # (4) Vesta
            $ classy spectra 12 21             # (12) Victoria, (21) Lutetia
            $ classy spectra julia sylvia 283  # (87) Sylvia, (89) Julia, (283) Emma

    .. tab-item:: python

        Get all spectra of asteroid (4) Vesta.

        .. code-block:: python

            >>> classy.Spectra("vesta")                  # (4) Vesta
            >>> classy.Spectra([12, 21])                 # (12) Victoria, (21) Lutetia
            >>> classy.Spectra(["julia", "sylvia", 283]) # (87) Sylvia, (89) Julia, (283) Emma

This target selection can be combined with or replaced by queries based on the
spectra and or target properties. Accepted property names are explained
:ref:`above <selection_criteria>_`. If the property is numeric (e.g. albedo),
you can specify lower and upper limits by separating them with a `,`. To
specify a one-sided limit, leave one side of the `,` blank. For categorical
values (e.g. taxonomy), you can select multiple acceptable values by separating
them with a `,`.

.. tab-set::

    .. tab-item:: Command Line

        Get all spectra of asteroid (22) *Kalliope* which cover the visible-near-infrared range (0.45-2.45μm).

        .. code-block:: shell

           $ classy spectra 22 --wave_min ,0.45 --wave_max 2.45,

        Get all spectra of (221) *Eos* and (599) *Luisa* observed by the MITHNEOS survey.

        .. code-block:: shell

           $ classy spectra 221 599 --source MITHNEOS

        Get all spectra observed by Marsset+ 2014 at phase angles below 20deg.

        .. code-block:: shell

           $ classy spectra --shortbib "Marsset+ 2014" --phase ,20

    .. tab-item:: python

        Get all spectra of asteroid (4) Vesta.

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(4)
           >>> spectra.plot()

        Get all spectra of asteroid (22) *Kalliope* which cover the visible-near-infrared range (0.45-2.45μm).

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(43)
           >>> spectra.plot()

        Get all spectra of (221) *Eos* and (599) *Luisa* observed by the MITHNEOS survey.

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(43)
           >>> spectra.plot()

        Get all spectra observed by AKARI.

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(43)
           >>> spectra.plot()

Finally, you can express all queries in a string-format passed to the ``query`` parameter. This is mandatory
when querying based on columns in the ssoBFT using the ``python`` interface.


.. tab-set::

    .. tab-item:: Command Line

        .. code-block:: shell

           $ classy spectra --query "wave_min > 0.3 & (taxonomy == B | taxonomy == C)"

    .. tab-item:: python

        .. code-block:: python

           >>> import classy
           >>> spectra = classy.Spectra(query="wave_min > 0.3 & (taxonomy == B | taxonomy == C)")
           >>> spectra = classy.Spectra(query="moid.EMB.value < 0.05 & (taxonomy == B | taxonomy == C)")

You can learn more about the syntax `here <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.query.html#pandas.DataFrame.query>`_.


.. [#f1]  The first query may trigger the download of the ssoBFT (~600MB) to your computer. More information can be found `here <https://rocks.readthedocs.io/en/latest/cli.html#access-of-ssobft>`_.
