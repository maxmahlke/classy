.. _advanced:

Advanced Usage
==============

Adding your own data to ``classy``
----------------------------------

``classy`` creates an index of reflectance spectra it knows about. These are primarily on remote
repositories (Gaia, SMASS, ...). You can add data on your computer to this index to simplify your
coding and to extend future analyses.\ [#f1]_

To add your data, you have to create a ``CSV`` file containing one row per spectrum with the following metadata:

- ``name``, ``number``,``date_obs``,``source``,``shortbib``,``bibcode`` - see :ref:`Basic Usage > Metadata<core>`. The data does not need to be complete.
- ``filename`` - the absolute path to the spectrum file

An example could be:

.. code-block::

   name,number,date_obs,source,shortbib,bibcode,filename
   Adeona,145,1999-11-04T05:45:00,F14,Fornasier+ 2014,2014Icar..233..163F,/astro/data/fornasier2014/adeona.txt
   Arethusa,95,1999-03-16T06:52:00,F14,Fornasier+ 2014,2014Icar..233..163F,/astro/data/fornasier2014/cc_arethusa.txt
   Galatea,74,1997-12-13T00:00:00,F14,Fornasier+ 2014,2014Icar..233..163F,/astro/data/fornasier2014/c97_galatea.txt
   Pretoria,790,1999-03-16T23:56:00,F14,Fornasier+ 2014,2014Icar..233..163F,/astro/data/fornasier2014/pretoria.txt


You can then add the spectra by running ``$ classy add /path/to/index.csv``


.. warning::

   The spectra you add are not copied to the cache directory. They need to stay in the location
   from where you add them to ``classy``.

Interactive Smoothing and Feature-Fitting
-----------------------------------------

.. TODO: Write this description

[TBD]

.. [#f1] Even better: you can make the data publicly available and `let me know about it <https://www.ias.universite-paris-saclay.fr/annuaire?nom=mahlke>`_ - I will add it to ``classy``.
