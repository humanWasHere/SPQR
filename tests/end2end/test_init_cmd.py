# import subprocess
import pytest
from pathlib import Path

from app.__main__ import manage_app_launch


@pytest.mark.parametrize("value, expected", [
    ('', 'default_config.json'),
    ('test_e2e_init_c.json', 'test_e2e_init_c.json'),
])
def test_cli_init_config(tmp_path, value, expected, caplog):
    """Test the initialization of a configuration file."""
    # Arrange
    source = Path(__file__).resolve().parents[2] / "assets" / "init" / "user_config_ex.json"
    target_path = tmp_path / value
    expected_path = tmp_path / expected
    # Act
    status = manage_app_launch(['init', '-c', str(target_path)])
    # Assert
    assert status == 0
    assert 'SPQR running init mode' in caplog.text
    assert f'Configuration file initialized at {expected_path}' in caplog.text
    assert source.read_text() == expected_path.read_text()


@pytest.mark.parametrize("value, expected", [
    ('', 'default_coord_file.txt'),
    ('test_e2e_init_x.txt', 'test_e2e_init_x.txt'),
])
def test_cli_init_coordfile(tmp_path, value, expected, caplog):
    """Test the initialization of a coordinate file."""
    # Arrange
    source = Path(__file__).resolve().parents[2] / "assets" / "init" / "coordinate_file_ex.txt"
    target_path = tmp_path / value
    expected_path = tmp_path / expected
    # Act
    status = manage_app_launch(['init', '-x', str(target_path)])
    # Assert
    assert status == 0
    assert 'SPQR running init mode' in caplog.text
    assert f'Coordinate file initialized at {expected_path}' in caplog.text
    assert source.read_text() == expected_path.read_text()
