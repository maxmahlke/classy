# 0.8.3 -
- Add -v|--verbose option to `classy classify` and `classy spectra`
- Change extrapolation limit from 10% to 4.7%
- Do not overwrite `pV` attribute when classifying in Mahlke/Tholen
- Sort new wavelength grid prior to resampling
- Add matplotlib to required packages, fix import error regarding matplotlib

# 0.8.2 - 2023-12-14
- Use up-to-date Miriade server URL

# 0.8.1 - 2023-12-06
- Fix shadowing of download function and module name
- Add error handling for Miriade connection timeouts
- Move async semaphore inside async function scope
- Fix classification of spectra without specified targets in Mahlke scheme

# 0.8 - 2023-12-06
- Split functionality of `$ classy spectra` into two commands: `$ classy spectra` and `$ classy classify`
- Add query language: spectra can now be selected based on properties of the spectrum (e.g. wavelength coverage, bibliography) and those of the target (e.g. family, taxonomy)
- Add graphical user interface for smoothing and feature-detection
- Add `export` functionality to export raw and processed spectral data and metadata
- Complete rework of documentation
- Major code refactoring


# 0.7.1 - 2023-11-18
- Separate gui-dependencies into optional package install

# 0.7 - 2023-09-11
- Changes to make classy spectral database shareable between computers / users:
  - classy cache directory path can be set with CLASSY_CACHE_DIR environment variable
  - Spectra added with 'classy add' are copied to the cache
  - Use spectrum filename as unique identifier. Create one file per spectrum for all repositories.
  - Make paths in classy index Windows-compatible
- Add Popescu+ 2019

# 0.6.5 - 2023-08-18
- Add missing pyqt5 dependency

# 0.6.4 - 2023-08-17
- Add missing pyqtgraph dependency

# 0.6.3 - 2023-08-15
- Bugfix in MITHNEOS and SMASS source modules

# 0.6.2 - 2023-08-15
- Add M4AST to sources
- Add Gartrelle+ 2021 to sources
- Add Marsset+ 2021 to sources
- Add Hardersen+ 2004, 2011, 2014, 2015, 2018 to sources
- Fix references for Fornasier+ 2007 spectra
- Highlight public/private repositories differently in `classy status`

# 0.6.1 - 2023-08-08
- Catch error if AKARI download fails
- Add Tholen and DeMeo classes to output of `classy.Spectrum.to_csv()`

# 0.6 - 2023-07-22
- Add your private collection of spectra to the classy index using '$ classy add'.
- Add function to compute phase angle from observation date for identified asteroids
- Add interactive smoothing and fitting GUI.
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
