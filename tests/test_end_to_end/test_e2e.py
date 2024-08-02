import subprocess
import pytest

def run_cli_command(command):
    """Helper function to run a CLI command and return the output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result

def test_cli_help():
    """Test the help command of the CLI."""
    result = run_cli_command('python -m app --help')
    assert result.returncode == 0
    assert 'usage: spqr [-h] {start,build} ...' in result.stdout

# def test_cli_version():
#     """Test the version command of the CLI."""
#     result = run_cli_command('python -m app --version')
#     assert result.returncode == 0
#     assert '1.0.0' in result.stdout  # Replace with your actual version

def test_cli_functionality():
    """Test a specific functionality of the CLI."""
    result = run_cli_command('python -m app start -r genepy')
    assert result.returncode == 0
    # assert 'app running in dev mode' in result.stdout
    # FIXME why stderr ???
    assert 'app running in dev mode' in result.stderr
    # assert '### CREATING RECIPE ### : test_env_genepy' in result.stdout

def test_cli_build_command():
    """Test the build command of the CLI."""
    command = 'python -m app build -c assets/app_config.json -r opcfield -l 22-50'
    result = run_cli_command(command)
    assert result.returncode == 0
    # FIXME why stderr ?
    assert '### CREATING RECIPE ### : test_env_OPCField' in result.stderr
    # assert '### CREATING RECIPE ### : test_env_OPCField' in result.stdout
    assert 'app running in prod mode' in result.stderr
    assert '(1/29:3%): V1 | Polarite: CD | min_dimension: 0.018 | Pitch: 0.358 | pitch_x_y 0.358 0.018' in result.stdout
    assert 'Measurement done' in result.stderr
    assert 'json recipe created !' in result.stderr
    assert 'csv recipe created !' in result.stderr
    
if __name__ == "__main__":
    pytest.main()