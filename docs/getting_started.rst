.. _getting_started:

Getting Started
===============

A word on notation: All example code preceded by a ``$`` is to be run on your terminal,
while ``>>>`` indicates that this code should be run in a ``python`` interpreter or a ``python``
script.

Installation
------------

``classy`` is available on the `python package index <https://pypi.org>`_ as
``space-classy``. To get the complete package and all dependencies, run

.. code-block:: bash

   $ pip install space-classy[gui]  # install complete version

The feature detection and preprocessing modules of ``classy`` require the
``pyqtgraph`` and ``pyside6`` packages, which depend on the large (in terms of
filesize) ``Qt`` library. You might want to opt out of these installs if you do
not intend to make use of these parts of ``classy`` (though usage will be quite
limited). In this case, you can run

.. code-block:: bash

   $ pip install space-classy  # install lite version

The minimum ``python`` version is ``3.8``.


After installing, the ``classy`` command is available on your command line.
If you run it without argument, the help text will appear, as shown below. Typically, you will
later add an argument such as ``status``, ``spectra``, or ``classify``, which are explained in
later parts of this documentation.
In ``python``, you can import the ``classy`` module after installation.

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
        add       Add a local spectra collection.
        classify  Classify spectra in classy index.
        docs      Open documentation in browser.
        features  Run interactive feature detection for selected spectra.
        smooth    Run interactive smoothing for selected spectra.
        spectra   Search for spectra in classy index.
        status    Manage the index of asteroid spectra.

  .. tab-item :: python

    .. code-block:: python

       >>> import classy

.. _adding_spectra:

Adding Spectra
--------------

``classy`` revolves around reflectance spectra. To get started, you can
retrieve all `public asteroid spectra <public_data>`_ by running the following
command on your terminal:

.. code-block:: shell

  $ classy status

At the shown prompt, type ``2`` and hit Enter to download public spectra.\ [#f1]_

.. code-block:: shell

  $ classy status

  Contents of /home/max/.cache/classy:

      0 asteroid reflectance spectra from 0 sources

  Choose one of these actions:
  [0] Do nothing [1] Manage the cache [2] Retrieve all spectra (0): 2

Alternatively, you can :ref:`add you own observations <private_data>`.
Once you have populated the ``classy`` database, you can start :ref:`exploring it <selecting_spectra>`.

.. rubric:: Footnotes
   :caption:

.. [#f1] If you care about the directory where the data is stored, have a look :ref:`here <cache_directory>`.
