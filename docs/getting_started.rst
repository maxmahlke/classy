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

The command line interface has one main function: ``classy spectra``. :ref:`Let's try it out.<available_data>`
