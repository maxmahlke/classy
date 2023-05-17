Install
========

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
         docs     Open the classy documentation in browser.
         spectra  Retrieve, plot, classify spectra of an individual asteroid.

  .. tab-item :: python

    .. code-block:: python

       >>> import classy


To get started, you can retrieve all `public asteroid spectra <available_data>`_ using the ``$ classy status`` command.

.. code-block:: shell

  $ classy status

  Contents of /home/max/.cache/classy:

      0 asteroid reflectance spectra from 0 sources

  Choose one of these actions:
  [0] Do nothing [1] Clear the cache [2] Retrieve all spectra (0): 2

.. _cache_directory:

Cache Directory
---------------

``classy`` caches data from online repositories of reflectance spectra on your
machine. The location depends on your platform and system language. For English
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
