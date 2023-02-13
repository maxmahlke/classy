![PyPI](https://img.shields.io/pypi/v/space-classy) [![arXiv](https://img.shields.io/badge/arXiv-2203.11229-f9f107.svg)](https://arxiv.org/abs/2203.11229) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<p align="center">
  <img width="260" src="https://raw.githubusercontent.com/maxmahlke/classy/main/docs/gfx/logo_classy.png">
</p>

Note: The classification pipeline is implemented yet the user-interface is
minimal so far. I am currently writing my PhD thesis and intend to make `classy`
more user-friendly in July / August of this year. For questions or issues, please use the [Issues](https://github.com/maxmahlke/classy/issues) page of this repository
or contact me [via email](https://www.oca.eu/en/max-mahlke).

[Features](#features) - [Install](#install) - [Documentation](#documentation) - [Data](#data) - [Development](#development)

# Features

Classify asteroids in the taxonomic scheme by [Mahlke, Carry, Mattei 2022](https://arxiv.org/abs/2203.11229).

``` sh

$ classy classify path/to/observations.csv
INFO     Looks like we got 2 S, 1 Ee, 1 B, 1 X, 1 Q

```

# Install

`classy` is available on the [python package index](https://pypi.org) as *space-classy*:

``` sh
$ pip install space-classy
```

# Documentation

Check out the documentation at [classy.readthedocs.io](https://classy.readthedocs.io/en/latest/).
or run

     $ classy docs

# Data

The following data files are provided in this repository (format `csv` and `txt`) and at the CDS (format `txt`):

| File `csv` | File `txt` |  Content | Description|
|-----------|--------|----|------------|
| `class_templates.csv` | `template.txt` | Class templates |  Mean and standard deviation of the VisNIR spectra and visual albedos for each class. |
| `class_visnir.csv` | `classvni.txt` | Classifications of the VisNIR sample. |  Classes derived for the 2983 input observations used to derive the taxonomy. |
| `class_vis.csv` | `classvis.txt` | Classifications of the vis-only sample. |  Classes derived for the 2923 input observations containing only visible spectra and albedos. |
| `class_asteroid.csv` | `asteroid.txt` | Class per asteroid |  Aggregated classifications in VisNIR and vis-only samples with one class per asteroid. |
| `ref_spectra.csv` | `refspect.txt` | References of spectra | The key to the spectra references used in the classification tables. |
| `ref_albedo.csv` | `refalbed.txt` | References of albedos |  The key to the albedo references used in the classification tables. |

More information on each file can be found in the [data/ReadMe](https://github.com/maxmahlke/classy/blob/main/data/ReadMe).

<!-- # Development -->
<!---->
<!-- To be implemented: -->
<!---->
<!-- - [ ] Graphical User Interface -->
<!-- - [ ] Optional automatic addition of SMASS spectra to observations -->
<!-- - [ ] Automatic determination of best smoothing parameters -->

<!-- # Contribute -->

<!-- Computation of asteroid class by weighted average -->
