![PyPI](https://img.shields.io/pypi/v/space-classy) [![arXiv](https://img.shields.io/badge/arXiv-2203.11229-f9f107.svg)](https://arxiv.org/abs/2203.11229) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<p align="center">
  <img width="260" src="https://raw.githubusercontent.com/maxmahlke/classy/main/docs/gfx/logo_classy.png">
</p>

[Features](#features) - [Install](#install) - [Documentation](#documentation)

Classify asteroids in the taxonomic scheme by [Mahlke, Carry, Mattei 2020](https://arxiv.org/abs/2203.11229).
based on reflectance spectra and visual albedos using the command line.

``` sh

$ classy classify path/to/observations.csv

```

or do it step-by-step

``` sh

$ classy preprocess path/to/observations.csv

```

Tip: Check out [rocks](https://github.com/maxmahlke/rocks) to easily add IAU
names, numbers, designations, and literature parameters to the observations.

<!-- # Install -->

<!-- `classy` is available on the [python package index](https://pypi.org) as *space-classy*: -->

<!-- ``` sh -->
<!-- $ pip install space-classy -->
<!-- ``` -->

<!-- # Documentation -->

<!-- Check out the documentation at [classy.readthedocs.io](https://classy.readthedocs.io/en/latest/). -->
or run

     $ classy docs

<!-- # Contribute -->

<!-- Automatic determination of best smoothing parameters -->
<!-- Computation of asteroid class by weighted average -->
