Appendix
========

.. _sanity_checks:

Validity Verifications
----------------------

When instantiating a ``Spectrum``, ``classy`` verifies the validity of the passed
data in the following way.

+----------+----------+-----------------------------------------+
| Argument | Value    | Action                                  |
+----------+----------+-----------------------------------------+
| ``wave`` | Positive | Keep value.                             |
+----------+----------+-----------------------------------------+
| ``wave`` | Negative | Discard value and matching reflectance. |
+----------+----------+-----------------------------------------+
| ``wave`` | NaN      | Discard value and matching reflectance. |
+----------+----------+-----------------------------------------+
| ``refl`` | Positive | Keep value.                             |
+----------+----------+-----------------------------------------+
| ``refl`` | Negative | Keep value.                             |
+----------+----------+-----------------------------------------+
| ``refl`` | NaN      | Discard value and matching wavelength.  |
+----------+----------+-----------------------------------------+

The examples below show how the ``wave`` and ``refl`` arrays are adapted.

.. code-block:: python

    >>> # Negative wavelength -> remove value
    >>> wave = [-1, 2, 3, 4]
    >>> refl = [1, 2, 3, 4]
    >>> spec = classy.Spectrum(wave, refl)
    >>> print(spec.wave)
    >>> print(spec.refl)

    >>> # NaN wavelength -> remove value
    >>> wave = [np.nan, 2, 3, 4]
    >>> refl = [1, 2, 3, 4]
    >>> spec = classy.Spectrum(wave, refl)
    >>> print(spec.wave)
    >>> print(spec.refl)

    >>> # Negative reflectance -> keep value
    >>> wave = [1, 2, 3, 4]
    >>> refl = [-1, 2, 3, 4]
    >>> spec = classy.Spectrum(wave, refl)
    >>> print(spec.wave)
    >>> print(spec.refl)

    >>> # NaN reflectance -> remove value
    >>> wave = [1, 2, 3, 4]
    >>> refl = [np.nan, 2, 3, 4]
    >>> spec = classy.Spectrum(wave, refl)
    >>> print(spec.wave)
    >>> print(spec.refl)

These validity verifications can thus affect the shape of the ``wave`` and
``refl`` values. Attributes which are applied on a per-point bases (like
quality flags) are not handled by ``classy``, their adaptation is up to you. To
facilitate this, ``classy`` adds the ``mask_valid`` attribute, which has the
same shape as the original data and is ``True`` if a value is kept and
``False`` otherwise.`

.. code-block:: python

    >>> # NaN reflectance -> remove value
    >>> wave = [1, 2, 3, 4]
    >>> refl = [np.nan, 2, 3, 4]
    >>> flag = [0, 1, 1, 2]
    >>> spec = classy.Spectrum(wave, refl, flag=flag)
    >>> print(spec.wave)
    >>> print(spec.refl)
    >>> print(spec.flag)
    >>> spec.flag = flag[spec.mask_valid]
    >>> print(spec.flag)

.. TODO: This does not work yet, both flag and mask_values have to be np.array

Finally, ``classy`` ensures that the passed wavelength values are sorted
in increasing order. If they are not sorted yet, ``wave`` will be sorted
and ``refl`` and ``refl_err`` will be sorted accordingly. To ensure that your
metadata has the correct order, you can run

.. code-block:: python

  >>> flag = sorted(flag, key=wave)

prior to instantiation.

.. TODO: This does not work yet, both flag and mask_values have to be np.array

.. _share_features:

Sharing feature index entires
-----------------------------

Locate the ``features.csv`` file in your ``CLASSY_DATA_DIR`` (default locations are given :ref:`here <cache_directory>`).
Each line represents one feature (column ``feature``) in a given spectrum (identified by the ``filename`` column).
All the necessary data to parametrize the feature using ``classy`` is contained in these single lines. To share
the parametrization of certain features, select the corresponding lines from the ``features.csv`` index file and share
them with your collaborators.

.. TODO: Insert link to SsODNet BFT column names
