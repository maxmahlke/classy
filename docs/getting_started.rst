Getting Started
===============

Install
-------

``classy`` is available on the `python package index <https://pypi.org>`_ as *space-classy*:

.. code-block:: bash

   $ pip install space-classy

The minimum ``python`` version is ``3.8``.
After installing, the ``classy`` executable is available system-wide and the
``classy`` ``python`` module can be imported.


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

.. _cache_directory:

Configuration
-------------

Data Directory
++++++++++++++

``classy`` requires a directory where it can store data on your machine. The
default location depends on your platform and system language. For English
systems:

+----------+-------------------------------------------------------+
| Platform | Directory                                             |
+----------+-------------------------------------------------------+
| Linux    | ``/home/$USER/.cache/classy``                         |
+----------+-------------------------------------------------------+
| Mac      | ``/Users/$USER/Library/Caches/classy``                |
+----------+-------------------------------------------------------+
| Windows  | ``'C:\\Users\\$USER\\AppData\\Local\\classy\\Cache'`` |
+----------+-------------------------------------------------------+

.. admonition:: Multi-user friendly
   :class: important

   The ``classy`` data directory can be shared between different devices
   and users. The filepaths of the spectra are stored relative to the data directory
   location.


You can change the location by setting the
``CLASSY_DATA_DIR`` environment variable.

.. tab-set::

  .. tab-item:: Linux / MacOS

    To set the environment variable once, use

    .. code-block:: bash

       $ export CLASSY_DATA_DIR=/path/to/your/data/directory

    To make the change persistent, add the ``export`` command to the
    initialization file of your shell (e.g. ``.zshrc``, ``.bashrc``)

  .. tab-item :: Windows

    Start Menu -> Advanced System Settings -> Environment Variables

Adding Data
-----------

``classy`` revolves around reflectance spectra. All spectra that you add to
``classy`` are cataloged in an index file. This index is used to select,
filter, and find reflectance spectra in the data directory.

To get started, you can retrieve all :ref:`public asteroid spectra <public_data>`
by using the ``$ classy status`` command and selecting option ``2``.
Alternatively, you can :ref:`add you own observations <private_data>`.
