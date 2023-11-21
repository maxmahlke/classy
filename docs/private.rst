.. _private_data:

Private Data
============

To extend your sample of reflectance spectra with non-public data, you can add
data on your computer to the ``classy`` spectra index.\ [#f1]_
To add your data, you have to create a ``CSV`` file containing one row per spectrum with the following metadata:

- ``filename`` - the absolute path to the spectrum file
- ``name``, ``number``, ``date_obs``, ``source``, ``shortbib``, ``bibcode``.
  The data does not need to be complete.

An example could be:

.. code-block::

   name,number,date_obs,source,shortbib,bibcode,filename
   Adeona,145,1999-11-04T05:45:00,F14,Fornasier+ 2014,2014Icar..233..163F,/home/max/data/fornasier2014/adeona.txt
   Arethusa,95,1999-03-16T06:52:00,F14,Fornasier+ 2014,2014Icar..233..163F,/home/max/data/fornasier2014/cc_arethusa.txt
   Galatea,74,1997-12-13T00:00:00,F14,Fornasier+ 2014,2014Icar..233..163F,/home/max/data/fornasier2014/c97_galatea.txt
   Pretoria,790,1999-03-16T23:56:00,F14,Fornasier+ 2014,2014Icar..233..163F,/home/max/data/fornasier2014/pretoria.txt


You can then add the spectra by running ``$ classy add /path/to/index.csv`` The
spectra are copied to the data directory. The parent directory structure of the
spectra is retained:

.. code-block::

   /home/max/data/demeo2009/ceres.txt -> $CLASSY_DATA_DIR/demeo2009/ceres.txt
   /home/max/data/demeo2009/pallas.txt -> $CLASSY_DATA_DIR/demeo2009/pallas.txt
   /home/max/data/devogele2018/asteroids/henan.txt -> $CLASSY_DATA_DIR/asteroids/henan.txt

.. warning::

   Each spectrum in the ``classy`` index is uniquely and only identified by its filename
   relative to the ``CLASSY_DATA_DIR``. Metadata is not used to tell them
   apart. If you add two different spectra with matching filenames (including
   the parent directory), the second will overwrite the first:

   .. code-block::

     /home/max/data/sunshine2008/asteroids/watsonia.txt -> $CLASSY_DATA_DIR/asteroids/watsonia.txt
     /home/max/data/devogele2018/asteroids/watsonia.txt -> $CLASSY_DATA_DIR/asteroids/watsonia.txt

.. [#f1] Even better: you can make the data publicly available and `let me know about it <https://www.ias.universite-paris-saclay.fr/annuaire?nom=mahlke>`_.
