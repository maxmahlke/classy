import classy


def test_minimal():
    """Functional test of Spectrum with wave and refl"""

    # Define dummy data
    wave = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
    refl = [0.85, 0.94, 1.01, 1.05, 1.04, 1.02, 1.04, 1.07, 1.1]

    spec = classy.Spectrum(wave=wave, refl=refl)
    spec.plot(show=False)
