.. _getting_started:

Getting Started
===============

Installation
------------

``classy`` is available on the `python package index <https://pypi.org>`_ as
``space-classy``. To get the complete package and all dependencies, run

.. code-block:: bash

   $ pip install space-classy[gui]

The feature detection and preprocessing modules of ``classy`` require the
``pyqtgraph`` and ``pyside6`` packages, which depend on the large (in terms of
filesize) ``Qt`` library. You might want to opt out of these installs if you do
not intend to make use of these parts of ``classy`` (though usage will be quite
limited!). In this case, you can run

.. code-block:: bash

   $ pip install space-classy

The minimum ``python`` version is ``3.8``. After installing, the ``classy``
executable is available system-wide and the ``classy`` ``python`` module can be
imported.


.. tab-set::

  .. tab-item:: Command Line

    .. code-block:: bash

       $ classy
       Usage: classy [OPTIONS] COMMAND [ARGS]...

         CLI for minor body classification.

       Options:
         --version  Show the version and exit.
         --help     Show this message and exit.

       Commands:
         add      Add a private spectra collection.
         docs     Open the classy documentation in browser.
         spectra  Retrieve, plot, classify spectra of an individual asteroid.
         status   Manage the index of asteroid spectra.

  .. tab-item :: python

    .. code-block:: python

       >>> import classy

.. _adding_spectra:

Adding Spectra
--------------

``classy`` revolves around reflectance spectra. To get started, you can
retrieve all `public asteroid spectra <public_data>`_ using the ``$ classy
status`` command.\ [#f1]_

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

Alternatively, you can :ref:`add you own observations <private_data>`.
Once you have populated the ``classy`` database, you can start :ref:`exploring it <selecting_spectra>`.

.. rubric:: Footnotes
   :caption:

.. [#f1] If you care about the directory where the data is stored, have a look :ref:`here <cache_directory>`.
