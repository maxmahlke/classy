# 0.5.1 -
- Add your private collection of spectra to the classy index using '$ classy add'.
- Add function to compute phase angle from observation date for identified asteroids
- Add interactive smoothing and fitting GUI. [undocumented]
- Fail gracefully with error if no spectra index is available

# 0.5 - 2023-05-12
- Add "classy status" command to manage cache directory
- Add PRIMASS-L, 52CAS, 24CAS, SCAS, and other repositories from PDS to sources
- Add Tholen 1984 class templates
- Add Bus and Binzel 2002 class templates
- Add Mahlke+ 2022 class templates
- tensforflow is not required unless classifying

# 0.4.3 - 2023-04-18
- Add 'save' argument to plotting functions
- Add S3OS2 archive to sources

# 0.4.2 - 2023-04-17
- Tholen taxonomy now respects the extrapolation limit
- Add DeMeo+ 2009 class templates
- Bugfix in slope computation
- Add progressbar to MITHNEOS download
- Add minimum y-limit delta in plot

# 0.4.1 - 2023-04-10
- Bugfixes in preprocessing module
- Bugfixes in DeMeo classification module
- Refinements in the plotting module

# 0.4 - 2023-04-07
- Add classification following DeMeo+ 09 taxonomy
- Add classification following Tholen 1984 taxonomy
- Add pre-defined preprocessing parameters for source/taxonomy pairs (eg Gaia and Tholen 1984)
- Mahlke taxonomy: Convert class probabilities from BCP to Ch if h feature is present

# 0.3.7 - 2023-03-08
- Add AKARI AcuA-spec catalogue
- Add label for each user spectrum

# 0.3.6 - 2023-03-07
- Fix smoothing of spectra in case of NaN reflectance values

# 0.3.5 - 2023-03-07
- The smooth_window and smooth_degree parameters can now be set in the preprocess() method call
- Add function to plot user-defined spectra

# 0.3.4 - 2023-02-22
- Set albedo to NaN if not provided and asteroid ID is unknown

# 0.3.3 - 2023-02-14
- Exit classy spectra if no spectra were found
- Add importlib_resources dependency for python 3.8
- Do not reset matplotlib rcParams when importing classy

# 0.3.2 - 2023-02-13
- Bump rocks version to match rich dependency requirement

# 0.3.1 - 2023-02-13
- Bugfix in $ classy spectra

# 0.3 - 2023-02-13
- Major revision of classy, adding Spectrum and Spectra classes

# 0.2.4 - 2022-05-11
- Fix the pre-settings of the smooth window size, it is now limited by the number of wavelength bins
- Don't show the undefined probability of being Ch in the Classifier plot

# 0.2.3 - 2022-05-11
- Always show the full VISNIR wavelength range in the Classifier plot
- Pretty-print tracebacks with rich
- Fix in the numeric column identification

# 0.2.2 - 2022-05-10
- Set default logging level back to INFO
- Bugfix in mixnorm module

# 0.2.1 - 2022-05-10
- Actually implement the 'classy' executable
- Fix implementation of data/ directory
- Simplify import scheme in package

  New recommended way to interact with classy is

    from classy import Preprocessor
    from classy import Classifier

# 0.2 - 2022-05-03
- Initial release

# 0.1 - 2021
404
