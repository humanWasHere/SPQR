from pathlib import Path
from unittest import mock  # create_autospec, patch, MagicMock

import pandas as pd
import pytest

from app.data_structure import Block
from app.interfaces import calibre_python
from app.measure.measure import Measure
from app.parsers.parse import FileParser


class FakeParser(FileParser):
    """Mock a FileParser implementation by wrapping an input dataframe."""
    unit: str = "um"
    def __init__(self, data: pd.DataFrame) -> None: self.data = data
    def parse_data(self) -> pd.DataFrame: return self.data


@pytest.fixture
def measure_instance(test_files):
    parser_input = FakeParser(
        pd.DataFrame({"name": ["gauge_name1", "gauge_name2", "gauge_name3", "gauge_name4"],
                      "x": [12, None, 13, 14],
                      "y": [22, 12, 42, None]}))
    mock_block = mock.create_autospec(Block, instance=True)
    mock_block.layout_path = test_files / "COMPLETED_TEMPLATE.gds"
    mock_block.topcell = "TOP"
    mock_block.precision = 1000
    return Measure(parser_input, mock_block, ["1.0"])


def test_creation_script_tmp(measure_instance):
    # Arrange
    output = "output_file.txt"
    search_area = 5
    # expected coords
    expected_path = Path.home() / "tmp" / "Script_tmp.tcl"

    # Act
    result = measure_instance.creation_script_tmp(output, search_area)

    # Assert
    assert isinstance(result, Path)
    assert result.exists()
    assert result.name == "Script_tmp.tcl"
    assert result.parent == Path.home() / "tmp"
    assert result == expected_path


def test_run_measure(measure_instance, monkeypatch):
    # Arrange
    # expected_columns = ['Gauge name', 'X_point', 'Y_point', 'Value']
    # expected_shape = (2, 4)
    result_path = ""  # TODO mock tmp file
    measure_instance.creation_script_tmp = lambda output, search_area=5, unit="nm": "script.tcl"
    # TODO finish the test

    # Act
    tmp_script = measure_instance.creation_script_tmp(result_path)
    monkeypatch.setattr('app.interfaces.calibre_python.lance_script', lambda x: "cr2sx04660")
    # result = measure_instance.run_measure()

    # Assert
    assert calibre_python.lance_script(tmp_script) == "cr2sx04660"
    # assert isinstance(result, pd.DataFrame)
    # assert result.columns.tolist() == expected_columns
    # assert result.shape == expected_shape


def test_output_measure(measure_instance, tmp_path):
    # Arrange
    test_df = pd.DataFrame({
        'name': ['test_name1', 'test_name2', 'test_name3'],
        'x': [1, 2, 3],
        'y': [11, 22, 33],
    })

    recipe_name = "test_output_recipe"
    expected_path = tmp_path / f"measure_{recipe_name}.csv"

    expected_csv = """name,x,y\ntest_name1,1,11\ntest_name2,2,22\ntest_name3,3,33\n"""

    # Act
    measure_instance.write_measurement(df=test_df, output_dir=tmp_path, recipe_name=recipe_name)

    # Assert
    assert expected_path.exists()
    assert expected_path.read_text() == expected_csv
