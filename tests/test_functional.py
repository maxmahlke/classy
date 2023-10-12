"""Functional tests for classy."""
from click.testing import CliRunner

import classy
from classy import cli


def test_interaction_with_index():
    """Test common index interaction scenarios."""
    runner = CliRunner()

    # User Max wants to study K-type asteroids
    # He first checks that the classy data directory is populated
    # using the `classy status` command
    results = runner.invoke(cli.status)
    assert result.exit_code == 0
    assert "Contents of" in result.output

    # He starts by looking for spectra of Eos on the command line
    results = runner.invoke(cli.spectra, ["eos"])
    assert result.exit_code == 0
    assert "(221) Eos" in result.output

    # To confirm that (221) Eos is a K-type, he classifies the spectra
    # in the Mahlke scheme
    results = runner.invoke(cli.classify, ["eos -t mahlke"])
    assert result.exit_code == 0
    assert "(221) Eos" in result.output

    # He wonders what Tholen class the Gaia spectrum has
    results = runner.invoke(cli.classify, ["eos -s gaia -t tholen"])
    assert result.exit_code == 0
    assert "(221) Eos" in result.output

    # Max wonders how many spectra of K-type classifications there are
    # in his database
    results = runner.invoke(cli.spectra, ["--family eos"])
    assert result.exit_code == 0
    assert "(221) Eos" in result.output

    # He is most interested in spectra which cover the complete VisNIR range

    # As a first step, he wants to focus only on Eos family members
    results = runner.invoke(
        cli.spectra, ["--family eos --wave_min 0.45 --wave_max 2.45"]
    )
    assert result.exit_code == 0
    assert "(221) Eos" in result.output

    # ------
    # Satisfied with the exploration results, Max switches to the python
    # interface to start an analysis script

    # He first gets all asteroids of Eos
    spectra = classy.Spectra("eos")
    assert len(spectra) > 1  # TODO: Think of better test criterion here

    # He queries all VisNIR spectra of Eos family members using the classy.Spectra class
    spectra = classy.Spectra(wave_min=0.45, wave_max=2.45, family="Eos")
    assert len(spectra) > 1  # TODO: Think of better test criterion here

    # Then he is feeling fancy and repeats the same query with the query syntax
    spectra = classy.Spectra(
        query="wave_min <= 0.45 & wave_max >= 2.45 & family == Eos"
    )
    assert len(spectra) > 1  # TODO: Think of better test criterion here
