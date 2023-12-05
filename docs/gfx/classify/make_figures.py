import classy

spectra = classy.Spectra(21)
spectra.classify("tholen")
spectra.plot(taxonomy="tholen", save="docs/gfx/classify/21_tholen.png")
