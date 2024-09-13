import logging
import subprocess
from pathlib import Path
import pytest

from app.interfaces.logger import logger_init  # import first


def run_cli_command(command):
    """Helper function to run a CLI command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result


def test_cli_help():
    """Test the help command of the CLI."""
    result = run_cli_command('python -m app --help')
    logging.debug(f"CLI help output: {result.stdout}")
    assert result.returncode == 0
    assert 'usage: spqr [-h] [-v] {test,build,upload,init} ...' in result.stdout


def test_cli_version():
    """Test the version command of the CLI."""
    result = run_cli_command('python -m app --version')
    assert result.returncode == 0
    assert 'spqr 0.2.0' in result.stdout


def test_cli_functionality():
    """Test a specific functionality of the CLI."""
    # Arrange
    # TODO takes a unverified path
    path = Path(__file__).resolve().parents[1] / "testfiles"
    # Act
    result = run_cli_command(f'python -m app build -c {path} -r genepy')
    # Assert
    if result.returncode != 0:
        logging.error(f"CLI command failed with stderr: {result.stderr}")
    assert result.returncode == 0
    # assert '### CREATING RECIPE ### : test_env_genepy' in result.stdout


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
    command = f"python -m app upload -c {recipe_path}"
    result = run_cli_command(command)
    assert 'SPQR running upload mode' in result.stderr
    assert f'Recipe {recipe_path} should be on RCPD machine!' in result.stderr


def test_upload_command_layout():
    """Test the upload command of the CLI"""
    layout_path = Path("../")
    command = f"python -m app upload -g {layout_path}"
    result = run_cli_command(command)
    assert 'SPQR running upload mode' in result.stderr
    assert f'Layout {layout_path} should be on RCPD machine!' in result.stderr


if __name__ == "__main__":
    pytest.main()
