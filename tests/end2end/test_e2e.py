import logging
import subprocess
from pathlib import Path

import pytest

from app import __version__
from app.__main__ import manage_app_launch


TEST_CONFIG = Path(__file__).resolve().parents[2] / "assets" / "app_config.json"

def run_cli_command(command):
    """Helper function to run a CLI command and return the output."""
    return subprocess.run(command, shell=True, capture_output=True, text=True)


def test_cli_help(capsys):
    """Test the help command of the CLI."""
    with pytest.raises(SystemExit) as exc_info:
        manage_app_launch(['-h'])
        assert exc_info.value.code == 0
        assert 'usage: spqr [-h] [-v] {init,build,upload,test,edit} ...' in capsys.readouterr()


def test_cli_version(capsys):
    """Test the version command of the CLI."""
    with pytest.raises(SystemExit) as exc_info:
        manage_app_launch(['-v'])
    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert f'spqr {__version__}' in captured.out


def test_cli_build_command():
    """Test the build command of the CLI."""
    command = f"python -m app build -c {TEST_CONFIG} -r opcfield -l 22-50"
    result = run_cli_command(command)
    assert result.returncode == 0
    assert '### CREATING RECIPE ### : test_env_OPCField' in result.stderr
    assert 'SPQR running in production mode' in result.stderr
    assert '(1/29:3%): V1 | Polarite: CD | min_dimension: 0.018 | Pitch: 0.358 | pitch_x_y 0.358 0.018' in result.stdout
    assert 'Measurement done' in result.stderr
    assert 'json recipe created !' in result.stderr
    assert 'csv recipe created !' in result.stderr


def test_upload_command_recipe(test_files):
    """Test the upload command of the CLI"""
    # recipe_path = test_files / "test_env_genepy.csv"
    # command = f"python -m app upload -r {recipe_path}"
    with pytest.raises(ChildProcessError) as exc_info:
        status = manage_app_launch(['upload', '-r', 'eqwerqeqweqwe'])
    # assert exc_info.value.code == 0
    assert status == 0
    assert False
    # result = run_cli_command(command)
    # assert 'SPQR running upload mode' in capsys.readouterr()
    # assert f'Recipe {recipe_path} should be on RCPD machine!' in capsys.readouterr()


# @patch('pathlib.Path.is_file', return_value=True)
def test_edit_command_recipe(test_files):
    """Test the edit command of the CLI"""
    recipe_path = test_files / "test_env_genepy.csv"
    configuration_path = Path(__file__).resolve().parents[2] / "assets" / "app_config.json"
    recipe_name = "genepy"
    command = f"python -m app edit -r {recipe_path} -c {configuration_path} -n {recipe_name}"
    result = run_cli_command(command)
    assert 'SPQR running edit mode' in result.stderr
    assert 'Which section do you want to modify (from the following list)?' in result.stderr


if __name__ == "__main__":
    pytest.main()
