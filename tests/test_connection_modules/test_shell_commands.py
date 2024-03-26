import pytest
from pathlib import Path
import subprocess
from unittest.mock import patch
from app.connection_modules.shell_commands import ShellCommands


# Test the run_scp_command_to_rcpd function with a valid CSV file
def test_run_scp_command_to_rcpd_with_csv():
    # Arrange
    shell_commands = ShellCommands()
    file_to_transfer = "test.csv"
    absolute_source_path = Path.cwd().parents[1] / "recipe_output"
    target_path = "upguest@c2x20007.cr2.st.com:/home/DG/DGTransferData/DGUpload"
    expected_command = f"scp {absolute_source_path}/{file_to_transfer} {target_path}"

    # Act & Assert
    with patch('subprocess.run') as mock_run:
        shell_commands.run_scp_command_to_rcpd(file_to_transfer, absolute_source_path, target_path)
        # Assert that subprocess.run was called with the expected command
        mock_run.assert_called_once_with(expected_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)


# Test the decorator to ensure it raises a ValueError for non-CSV files
def test_decorator_scp_rcpd_with_non_csv():
    # Arrange
    shell_commands = ShellCommands()
    file_to_transfer = "test.txt"  # Not a CSV file

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        shell_commands.run_scp_command_to_rcpd(file_to_transfer)
    assert "You did not import a correct CSV file. Check for extension." in str(excinfo.value)
