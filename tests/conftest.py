from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def test_files():
    """Fixture to provide path to test inputs"""
    base_path = Path(__file__).parent / "testfiles"
    return base_path


# @pytest.fixture()
# def get_test_case(test_resources):
#     def _get_test_case(name: str):
#         return test_resources / name
#     return _get_test_case
