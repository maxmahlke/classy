.. _features:

Features
========

A number of taxonomic classes have secondary characters to signal the presence of certain spectral features,
such as ``Ch``, ``Xk``, ``Xn``, ``Ee``. The presence or absence of these features must therefore be determined prior
to taxonomic classification.

``classy`` recognises three spectral absorption features as taxonomically relevant: the ``e``, ``h``, and ``k``
features. They are defined in `Mahlke, Carry, and Mattei 2022 <https://arxiv.org/abs/2203.11229>`_ and plotted below.

.. image:: gfx/feature_flags.png
    :align: center
    :class: only-light
    :width: 600

.. image:: gfx/feature_flags_dark.png
    :align: center
    :class: only-dark
    :width: 600

Detection
---------

Each spectrum in ``classy`` has the ``e``, ``h``, and ``k`` attributes which represent
the absorption features. Each feature has three different attributes which represent its presence or absence:

- ``is_covered``: ``True`` if the spectrum covers the feature wavelength range, else ``False``
- ``is_candidate``: ``True`` if ``is_covered`` but the band has not been inspected yet by the user, else ``False``
- ``is_present``: ``True`` if the presence of the band has been visually confirmed by the user, else ``False``

.. TODO:Turn the paragraph below into a logic diagram

When a spectrum is loaded into ``classy``, its wavelength range is evaluated
and the ``is_covered`` attribute of each of the three features is set
accordingly. If ``is_covered`` is ``True``, the spectrum is a candidate to have
the feature. It is then up to you to visually confirm or deny the presence,
setting `is_present`` into ``True`` or ``False`` depending on the inspection
result. After the inspection, ``is_candidate`` is ``False`` as we now know
whether the feature is present or not.

.. tab-set::

   .. tab-item:: Command Line

       Use
       Only spectra that cover the feature wavelength ranger will be included.

       .. code-block:: shell

          $ classy features --shortbib "Morate+ 2016"

          $ classy features --shortbib "Morate+ 2016" --feature h

   .. tab-item:: python

       Use

       .. code-block:: python

          >>> import classy
          >>> spectra = classy.Spectra(shortbib="Morate+ 2016")
          >>> for spec in spectra:
          ...     if spec.h.is_candidate:
          ...         spec.h.inspect()

SCREENSHOT OF FITTING TOOL

.. _feature_index:
Feature Index
+++++++++++++

EXAMPLE

classy feature index


Share results with other people, promoting reproducibility. classy directory
can be shared between devices

Analysis
--------

Features are essentially mini-spectra


.. code-block:: python

    >>> ceres = classy.Spectra("Fortuna", source='SMASS')[0]  # returns classy.Spectrum
    >>> ceres.h.is_observed # is the 0.7mu hydration feature covered by the wavelength range?
    True
    >>> ceres.h.is_present  #  is the 0.7mu hydration feature present in the spectrum?
    True
    >>> ceres.h.center  #  what is the center wavelength of the feature?
    0.68


When a ``classy.Spectrum`` is created, ``classy`` automatically creates the feature attributes and sets
the ``is_observed`` values corresponding to the wavelength values. It will further perform a simple band fit
to determine whether it is present and band parameters like the center wavelength and the depth.
