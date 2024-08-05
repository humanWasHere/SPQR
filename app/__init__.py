import importlib.metadata
from pathlib import Path

__version__ = ''

try:
    # If it is running from a distribution
    __version__ = importlib.metadata.version("spqr")
except importlib.metadata.PackageNotFoundError:
    # Works in development environment where package is not installed
    import toml
    pyproject_toml_file = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
        __version__ = toml.load(pyproject_toml_file)["tool"]["poetry"]["version"]
