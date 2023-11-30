Configuration
=============

.. _cache_directory:

Data Directory
--------------

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

.. _extrapolation_limit:

Extrapolation Limit
-------------------

The extrapolation limit is applied when classifying spectra in the Tholen or
the DeMeo taxonomy. If the covered wavelength range is within a given
percentage of the required range, ``classy`` will apply constant extrapolation
to cover the entire range and enable the classification. This limit can be set
via ``classy.defs.EXTRAPOLATION_LIMIT`` and is ``0.1`` (=10%) by default, meaning
that spectra covering 90% of the required wavelength range will be classified.
