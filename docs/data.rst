.. _available_data:

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

      68024 asteroid reflectance spectra from 11 sources

      24CAS      286    52CAS      146    AKARI       64    ECAS       589
      Gaia     60518    MITHNEOS  1905    Misc       877    PRIMASS    437
      S3OS2      820    SCAS       126    SMASS     2256

  Choose one of these actions:
  [0] Do nothing [1] Clear the cache [2] Retrieve all spectra (0): 2

.. admonition:: Available Data
   :class: important

   Number of Spectra: **68,024**

   Number of Individual Asteroids: **62,045**

The ``python`` interface allows more advanced analyses and access to the
metadata. All public spectra have the attributes below, while additional
attributes are available on a per-source basis, see the individual repository
descriptions.

+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Attribute                    | Description                                                                                                         |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``name``                     | Name or provisional designation of the target asteroid.                                                             |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``number``                   | Number of the target asteroid.                                                                                      |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``shortbib``                 | Short version of reference of the spectrum.                                                                         |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``bibcode``                  | Bibcode of reference publication of the spectrum.                                                                   |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``source``                   | String representing the source of the spectrum (e.g. ``'24CAS'``).                                                  |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+
| ``date_obs``                 | Observation epoch of the spectrum in `ISOT format <https://en.wikipedia.org/wiki/ISO_8601>`_:                       |
|                              | ``YYYY-MM-DDTHH:MM:SS``. If the time of the day is not know, ``HH:MM:SS`` is set to ``00:00:00``.                   |
|                              | If the date is not know, the ``date_obs`` attribute is an empty string.                                             |
|                              | If the spectrum is an average of observations at different dates, all dates are given,                              |
|                              | separated by a ``,``: ``2004-03-02T00:00:00,2004-05-16T00:00:00``.                                                  |
+------------------------------+---------------------------------------------------------------------------------------------------------------------+

.. include:: sources/24cas.rst

.. include:: sources/52cas.rst

.. include:: sources/akari.rst

.. include:: sources/ecas.rst

.. include:: sources/gaia.rst

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
