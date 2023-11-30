"""Functional tests for classy."""
from click.testing import CliRunner

import classy
from classy import cli


def test_interaction_with_index():
    pass
    # """Test common index interaction scenarios."""
    # runner = CliRunner()
    #
    # # User Max wants to study K-type asteroids
    # # He first checks that the classy data directory is populated
    # # using the `classy status` command. It is, so he enters 0 to exit.
    # result = runner.invoke(cli.status, input="0\n")
    # assert result.exit_code == 0
    # assert "Contents of" in result.output
    #
    # # He starts by looking for spectra of Eos on the command line
    # result = runner.invoke(cli.spectra, ["eos"])
    # assert result.exit_code == 0
    # assert "Eos" in result.output
    #
    # # To confirm that (221) Eos is a K-type, he classifies the spectra
    # # in the Mahlke scheme
    # result = runner.invoke(cli.classify, ["eos -t mahlke"])
    # assert result.exit_code == 0
    # assert "Eos" in result.output
    #
    # # He wonders what Tholen class the Gaia spectrum has
    # result = runner.invoke(cli.classify, ["eos -s gaia -t tholen"])
    # assert result.exit_code == 0
    # assert "Eos" in result.output
    #
    # # Max wonders how many spectra of K-type classifications there are
    # # in his database
    # result = runner.invoke(cli.spectra, ["--family eos"])
    # assert result.exit_code == 0
    # assert "Eos" in result.output
    #
    # # He is most interested in spectra which cover the complete VisNIR range
    #
    # # As a first step, he wants to focus only on Eos family members
    # result = runner.invoke(
    #     cli.spectra, ["--family eos --wave_min 0.45 --wave_max 2.45"]
    # )
    # assert result.exit_code == 0
    # assert "Eos" in result.output
    #
    # # ------
    # # Satisfied with the exploration results, Max switches to the python
    # # interface to start an analysis script
    #
    # # He first gets all asteroids of Eos
    # spectra = classy.Spectra("eos")
    # assert len(spectra) > 1  # TODO: Think of better test criterion here
    #
    # # He queries all VisNIR spectra of Eos family members using the classy.Spectra class
    # spectra = classy.Spectra(wave_min=0.45, wave_max=2.45, family="Eos")
    # assert len(spectra) > 1  # TODO: Think of better test criterion here
    #
    # # Then he is feeling fancy and repeats the same query with the query syntax
    # spectra = classy.Spectra(
    #     query="wave_min <= 0.45 & wave_max >= 2.45 & family == Eos"
    # )
    # assert len(spectra) > 1  # TODO: Think of better test criterion here
