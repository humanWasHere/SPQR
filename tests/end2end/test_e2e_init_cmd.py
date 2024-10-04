# import subprocess
import pytest

from tests.end2end.test_e2e import run_cli_command


@pytest.fixture()
def output_dir(tmp_path):
    return tmp_path / "init_outputs"


def test_cli_init_command_c_default(output_dir):
    """Test the init command of the CLI."""
    # Arrange
    path = output_dir
    # Act
    command = f"python -m app init -c {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode' in result.stderr
    assert f'Configuration file initialized at {path}/default_config.json' in result.stderr


def test_cli_init_command_x_default(output_dir):
    """Test the init command of the CLI."""
    # Arrange
    path = output_dir
    # Act
    command = f"python -m app init -x {path}"
    result = run_cli_command(command)

    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode' in result.stderr
    assert f'Coordinate file initialized at {path}/default_coord_file.txt' in result.stderr


def test_cli_init_command_c(output_dir):
    """Test the init command of the CLI."""
    # Arrange
    path = output_dir / "test_e2e_init_c.json"
    # Act
    command = f"python -m app init -c {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode' in result.stderr
    assert f'Configuration file initialized at {path}' in result.stderr


def test_cli_init_command_x(output_dir):
    """Test the init command of the CLI."""
    # Arrange
    path = output_dir / "test_e2e_init_x.txt"
    # Act
    command = f"python -m app init -x {path}"
    result = run_cli_command(command)
    # Assert
    assert result.returncode == 0
    assert 'SPQR running init mode' in result.stderr
    assert f'Coordinate file initialized at {path}' in result.stderr


# def test_cli_init_command_c_bad_file_ext():
#     """Test the init command of the CLI."""
#     # Arrange
#     path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs" / "test_e2e_init_c.txt"
#     # Act
#     command = f"python -m app init -c {path}"
#     result = run_cli_command(command)
#     # Assert
#     assert result.returncode == 0
#     assert f'ValueError: File should be in .json format: {path}' in result.stderr


# def test_cli_init_command_x_bad_file_ext():
#     """Test the init command of the CLI."""
#     # Arrange
#     path = Path(__file__).resolve().parents[1] / "testfiles" / "init_outputs" / "test_e2e_init_x.json"
#     # Act
#     command = f"python -m app init -x {path}"
#     result = run_cli_command(command)
#     # Assert
#     assert result.returncode == 0
#     assert f'ValueError: File should be in .txt format: {path}' in result.stderr
