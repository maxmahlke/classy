import classy

def test_minimal():
    """Functional test of Spectrum with wave and refl"""

    # Define dummy data
    wave = [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85]
    refl = [0.85, 0.94, 1.01, 1.05, 1.04, 1.02, 1.04, 1.07, 1.1]

    spec = classy.Spectrum(wave=wave, refl=refl)
    spec.remove_continuum()
    spec.plot(show=False)


def test_spectra_print():
    spec = classy.Spectra(16)
    print(spec) # it should be the same as cli: classy spectra 16
    spec.classify(taxonomy="mahlke")
    print(spec) # it should be the same as cli: classy classify 16 --taxonomy mahlke
    spec.classify(taxonomy="demeo")
    print(spec) # results should contain mahlke and demeo classifications
    spec.classify(taxonomy="tholen")
    print(spec) # it should be the same as cli: classy classify 16

# if __name__ == "__main__":
#     test_minimal()
#     test_spectra_print()