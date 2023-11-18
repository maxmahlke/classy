.. _features:

Features
========

Only spectra that cover the feature wavelength ranger will be included.

``classy`` recognises three spectral absorption features as ``special``: the ``e``, ``h``, and ``k``
features. They are defined in `Mahlke, Carry, and Mattei 2022 <https://arxiv.org/abs/2203.11229>`_ and plotted below.

.. image:: gfx/feature_flags.png
    :align: center
    :class: only-light
    :width: 600

.. image:: gfx/feature_flags_dark.png
    :align: center
    :class: only-dark
    :width: 600

The presence or absence of these features can change the taxonomic classification of the spectrum.
Each ``classy.Spectrum`` has the attributes ``e``, ``h``, and ``k``, which represent these features.

.. code-block:: python

    >>> ceres = classy.Spectra("Fortuna", source='SMASS')[0]  # returns classy.Spectrum
    >>> ceres.h.is_observed # is the 0.7mu hydration feature covered by the wavelength range?
    True
    >>> ceres.h.is_present  #  is the 0.7mu hydration feature present in the spectrum?
    True
    >>> ceres.h.center  #  what is the center wavelength of the feature?
    0.68

Note the difference between ``is_observed`` (does the spectrum cover the feature wavelength range?) and ``is_present``
(is the band visible in this spectrum?).

When a ``classy.Spectrum`` is created, ``classy`` automatically creates the feature attributes and sets
the ``is_observed`` values corresponding to the wavelength values. It will further perform a simple band fit
to determine whether it is present and band parameters like the center wavelength and the depth.

.. warning::

    The band parametrisation that ``classy`` does automatically is rudimentary. It is recommended to use the
    interactive feature-fitting routine instead, see :ref:`Advanced Usage <advanced>`.
