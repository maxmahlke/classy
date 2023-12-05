"""Unit tests for cli module."""
import os

from click.testing import CliRunner

from classy import cli


def test_spectra():
    """Test listing of asteroid spectra based on metadata queries.

    These queries are examples given in the documentation.
    """
    os.environ["COLUMNS"] = "1000"  # ensure that rich prints full table

    runner = CliRunner()

    # List all spectra of Vesta
    result = runner.invoke(cli.spectra, args="vesta")
    assert result.exit_code == 0
    assert "Vesta" in result.output

    # List all spectra of 12 and 21
    result = runner.invoke(cli.spectra, args="12 21")
    assert result.exit_code == 0
    assert "Victoria" in result.output
    assert "Lutetia" in result.output

    # List all spectra of 87, 89, and 283
    result = runner.invoke(cli.spectra, args="julia sylvia 283")
    assert result.exit_code == 0
    assert "Julia" in result.output
    assert "Sylvia" in result.output
    assert "Emma" in result.output

    # Test spectra-specific queries
    result = runner.invoke(cli.spectra, args="eos --wave_min 0.4")
    assert result.exit_code == 0
    assert "Eos" in result.output

    result = runner.invoke(cli.spectra, args="eos --wave_max 1.2")
    assert result.exit_code == 0
    assert "Eos" in result.output

    result = runner.invoke(cli.spectra, args="--phase 0,10")
    assert result.exit_code == 0
    assert "phase" in result.output or "No spectra matching" in result.output

    result = runner.invoke(cli.spectra, args="ceres pallas --source MITHNEOS,Gaia")
    assert result.exit_code == 0
    assert "Ceres" in result.output
    assert "MITHNEOS" in result.output
    assert "Gaia" in result.output

    result = runner.invoke(cli.spectra, args=" --shortbib 'Marsset+ 2014'")
    assert result.exit_code == 0
    assert "Etna" in result.output

    result = runner.invoke(cli.spectra, args="bennu --date_obs 2005,")
    assert result.exit_code == 0
    assert "Bennu" in result.output

    result = runner.invoke(cli.spectra, args="vesta --N 500,")
    assert result.exit_code == 0
    assert "Vesta" in result.output

    result = runner.invoke(cli.spectra, args="--albedo 0.03,0.04")
    assert result.exit_code == 0
    assert "albedo" in result.output

    result = runner.invoke(cli.spectra, args="22 --wave_min 0.45 --wave_max 2.45")
    assert result.exit_code == 0
    assert "Kalliope" in result.output

    result = runner.invoke(cli.spectra, args="--albedo 0.1, --taxonomy B,C")
    assert result.exit_code == 0
    assert "albedo" in result.output
    assert "taxonomy" in result.output

    result = runner.invoke(cli.spectra, args="--wave_min 0.4 --taxonomy B,C")
    assert result.exit_code == 0
    assert "taxonomy" in result.output

    result = runner.invoke(
        cli.spectra,
        args="--query \"wave_min < 0.4 & (taxonomy == 'B' | taxonomy == 'C')\"",
    )
    assert result.exit_code == 0
    assert "taxonomy" in result.output

    result = runner.invoke(
        cli.spectra, args="--family Tirela,Watsonia --query \"taxonomy != 'L'\""
    )
    assert result.exit_code == 0
    assert "family" in result.output
    assert "taxonomy" in result.output

    # TODO: Reenable once feature index is available online
    # result = runner.invoke(cli.spectra, args="--feature h")
    # assert result.exit_code == 0

    result = runner.invoke(cli.spectra, args="--moid.EMB.value ,005 --H ,22")
    assert result.exit_code == 0
    assert "moid" in result.output

    os.environ["COLUMNS"] = "80"


def test_classify():
    """Test classification interface."""
    os.environ["COLUMNS"] = "1000"  # ensure that rich prints full table

    runner = CliRunner()

    result = runner.invoke(cli.classify, args="vesta --source MITHNEOS")
    assert "class_mahlke" in result.output
    assert "class_demeo" in result.output
    assert "class_tholen" in result.output
    assert result.exit_code == 0

    result = runner.invoke(cli.spectra, args="ceres --source ECAS --taxonomy tholen")
    assert result.exit_code == 0

    result = runner.invoke(cli.spectra, args="ceres --source ECAS -t THOLEN")
    assert result.exit_code == 0

    os.environ["COLUMNS"] = "80"


def test_invalid_argument_combinations():
    """Make sure that sensible warnings and errors are printed when invalid argument combinations
    are passed."""

    # Save without plotting -> could actually be used as "export"
