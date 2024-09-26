# import logging
# import subprocess
from pathlib import Path
# import pytest

# from app.interfaces.logger import logger_init  # import first
from tests.end2end.test_e2e import run_cli_command


def test_cli_init_command_j_default():
    """Test the init command of the CLI."""
    # Arrange
    path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs"
    # Act
    command = f"python -m app init -j {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode (user configuration example in json)' in result.stderr
    assert f'Configuration file initialized at {path}/default_config.json' in result.stderr


def test_cli_init_command_t_default():
    """Test the init command of the CLI."""
    # Arrange
    path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs"
    # Act
    command = f"python -m app init -t {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode (coordinate file example in txt)' in result.stderr
    assert f'Configuration file initialized at {path}/default_coord_file.txt' in result.stderr


def test_cli_init_command_j():
    """Test the init command of the CLI."""
    # Arrange
    path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs" / "test_e2e_init_j.json"
    # Act
    command = f"python -m app init -j {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode (user configuration example in json)' in result.stderr
    assert f'Configuration file initialized at {path}' in result.stderr


def test_cli_init_command_t():
    """Test the init command of the CLI."""
    # Arrange
    path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs" / "test_e2e_init_t.txt"
    # Act
    command = f"python -m app init -t {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode (coordinate file example in txt)' in result.stderr
    assert f'Configuration file initialized at {path}' in result.stderr


def test_cli_init_command_j_bad_file_ext():
    """Test the init command of the CLI."""
    # Arrange
    path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs" / "test_e2e_init_t.txt"
    # Act
    command = f"python -m app init -j {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert f'ValueError: File should be in .json format: {path}' in result.stderr


def test_cli_init_command_t_bad_file_ext():
    """Test the init command of the CLI."""
    # Arrange
    path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs" / "test_e2e_init_j.json"
    # Act
    command = f"python -m app init -t {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert f'ValueError: File should be in .txt format: {path}' in result.stderr