<p align="center">
  <img width="260" src="https://raw.githubusercontent.com/maxmahlke/classy/master/docs/_static/logo_classy.svg">
</p>

<p align="center">
  <a href="https://github.com/maxmahlke/classy#features"> Features </a> - <a href="https://github.com/maxmahlke/classy#install"> Install </a> - <a href="https://github.com/maxmahlke/classy#documentation"> Documentation </a>
</p>

<br>

<div align="center">
  <a href="https://img.shields.io/pypi/pyversions/space-classy">
    <img src="https://img.shields.io/pypi/pyversions/space-classy"/>
  </a>
  <a href="https://img.shields.io/pypi/v/space-classy">
    <img src="https://img.shields.io/pypi/v/space-classy"/>
  </a>
  <a href="https://readthedocs.org/projects/classy/badge/?version=latest">
    <img src="https://readthedocs.org/projects/classy/badge/?version=latest"/>
  </a>
  <a href="https://arxiv.org/abs/2203.11229">
    <img src="https://img.shields.io/badge/arXiv-2203.11229-f9f107.svg"/>
  </a>
</div>

<br>

![Classification of (1) Ceres using data from Gaia/SMASS/MITHNEOS](https://classy.readthedocs.io/en/latest/_images/ceres_classification_dark.png)

# Features

- Classify asteroid reflectance spectra in the taxonomic scheme by [Mahlke, Carry, and Mattei 2022](https://arxiv.org/abs/2203.11229).

- Add spectra from public repositories for comparison

- Explore data via the command line, build an analysis with the ``python`` interface

- Simple syntax: specify the asteroid to analyse, ``classy`` takes care of the rest

``` sh

$ classy spectra juno --classify

```

or

``` python
>>> import classy
>>> spectra = classy.Spectra(3)
... [classy] Found 1 spectrum in Gaia
... [classy] Found 5 spectra in SMASS
>>> spectra.classify()
... [classy] [(3) Juno] - [Gaia]: S
... [classy] [(3) Juno] - [spex/sp96]: S
... [classy] [(3) Juno] - [smass/smassir]: S
... [classy] [(3) Juno] - [smass/smass1]: S
... [classy] [(3) Juno] - [smass/smass2]: S
... [classy] [(3) Juno] - [smass/smass2]: S
>>> spectra.to_csv('class_juno.csv')
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

More information on each file can be found in the [data/mahlke2022/ReadMe](https://github.com/maxmahlke/classy/blob/main/data/ReadMe).

<!-- # Development -->
<!---->
<!-- To be implemented: -->
<!---->
<!-- - [ ] Graphical User Interface -->
<!-- - [ ] Optional automatic addition of SMASS spectra to observations -->
<!-- - [ ] Automatic determination of best smoothing parameters -->

<!-- # Contribute -->

<!-- Computation of asteroid class by weighted average -->
