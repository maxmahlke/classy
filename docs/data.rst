.. _public_data:

Public Data
===========

.. Reflectance spectra of asteroids may vary due to observational circumanstances,
.. differences in data processing, and physical processes on the minor body. It is
.. generally worthwhile to compare spectral observations of individual asteroids
.. reported by different surveys.
``classy`` sources the databases listed
alphabetically below to allow for quick comparisons between literature data and
your observations.\ [#f1]_
You can download and visualize a spectrum using the command line via the ``$
classy spectra`` command. To download all spectra from public repositories, use the ``$ classy status``
command.

.. code-block:: shell

  $ classy status

  Contents of /home/max/.cache/classy:

      68356 asteroid reflectance spectra from 14 sources

      24CAS      286    52CAS      146    AKARI       64    CDS         93
      ECAS       589    Gaia     60518    M4AST      123    MITHNEOS  1905
      Misc       902    PDS         91    PRIMASS    437    S3OS2      820
      SCAS       126    SMASS     2256

  Choose one of these actions:
  [0] Do nothing [1] Manage the cache [2] Retrieve all spectra (0): 2

.. admonition:: Available Public Data
   :class: important

   Number of Spectra: **68,280**

   Number of Individual Asteroids: **62,045**

.. include:: sources/24cas.rst

.. include:: sources/52cas.rst

.. include:: sources/akari.rst

.. include:: sources/ecas.rst

.. include:: sources/gaia.rst

.. include:: sources/m4ast.rst

.. include:: sources/mithneos.rst

.. include:: sources/misc.rst

.. include:: sources/primass.rst

.. include:: sources/s3os2.rst

.. include:: sources/scas.rst

.. include:: sources/smass.rst

.. include:: sources/ssodnet.rst

.. rubric:: Footnotes
   :caption:

.. [#f1] Completeness is important. If there is a public online repository of
   spectra you would like to see inlcuded, please `suggest it
   <https://github.com/maxmahlke/classy/issues>`_ and it will be added if
   possible.
