import logging
import subprocess
from pathlib import Path
import pytest
from unittest.mock import patch

from app import __version__


def run_cli_command(command):
    """Helper function to run a CLI command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result


def test_cli_help():
    """Test the help command of the CLI."""
    result = run_cli_command('python -m app --help')
    logging.debug(f"CLI help output: {result.stdout}")
    assert result.returncode == 0
    assert 'usage: spqr [-h] [-v] {init,edit,upload,test,build} ...' in result.stdout


def test_cli_version():
    """Test the version command of the CLI."""
    result = run_cli_command('python -m app --version')
    assert result.returncode == 0
    assert f'spqr {__version__}' in result.stdout


def test_cli_build_command():
    """Test the build command of the CLI."""
    path = Path(__file__).resolve().parents[2] / "assets" / "app_config.json"
    command = f"python -m app build -c {path} -r opcfield -l 22-50"
    result = run_cli_command(command)
    assert result.returncode == 0
    assert '### CREATING RECIPE ### : test_env_OPCField' in result.stderr
    assert 'SPQR running in production mode' in result.stderr
    assert '(1/29:3%): V1 | Polarite: CD | min_dimension: 0.018 | Pitch: 0.358 | pitch_x_y 0.358 0.018' in result.stdout
    assert 'Measurement done' in result.stderr
    assert 'json recipe created !' in result.stderr
    assert 'csv recipe created !' in result.stderr


def test_upload_command_recipe():
    """Test the upload command of the CLI"""
    recipe_path = Path("../")
    command = f"python -m app upload -r {recipe_path}"
    result = run_cli_command(command)
    assert 'SPQR running upload mode' in result.stderr
    assert f'Recipe {recipe_path} should be on RCPD machine!' in result.stderr


def test_upload_command_layout():
    """Test the upload command of the CLI"""
    layout_path = Path("../")
    command = f"python -m app upload -l {layout_path}"
    result = run_cli_command(command)
    assert 'SPQR running upload mode' in result.stderr
    assert f'Layout {layout_path} should be on RCPD machine!' in result.stderr


# @patch('pathlib.Path.is_file', return_value=True)
def test_edit_command_recipe():
    """Test the edit command of the CLI"""
    recipe_path = Path(__file__).resolve().parents[1] / "testfiles" / "test_env_genepy.csv"
    configuration_path = Path(__file__).resolve().parents[2] / "assets" / "app_config.json"
    recipe_name_from_config = "genepy"
    command = f"python -m app edit -r {recipe_path} -c {configuration_path} -n {recipe_name_from_config}"
    result = run_cli_command(command)
    assert 'SPQR running edit mode' in result.stderr
    assert 'Which section do you want to modify (from the following list)?' in result.stderr


if __name__ == "__main__":
    pytest.main()
