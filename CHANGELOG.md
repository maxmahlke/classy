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

# 0.2 - 2022-05-3
- Initial release

# 0.1 - 2021
404
