from pathlib import Path
from unittest import mock  # create_autospec, patch, MagicMock

import pandas as pd
import pytest

from app.data_structure import Block
from app.interfaces import calibre_python
from app.measure.measure import Measure
from app.parsers.parse import FileParser


class FakeParser(FileParser):
    unit: str = "um"
    def __init__(self, df: pd.DataFrame) -> None: self.data = df
    def parse_data(self) -> pd.DataFrame: return self.data


LAYOUT = Path(__file__).resolve().parents[1] / "testfiles" / "COMPLETED_TEMPLATE.gds"
LAYERS = ["1.0"]


@pytest.fixture
def measure_instance():
    parser_input = FakeParser(
        pd.DataFrame({"name": ["gauge_name1", "gauge_name2", "gauge_name3", "gauge_name4"],
                      "x": [12, None, 13, 14],
                      "y": [22, 12, 42, None]}))
    mock_block = mock.create_autospec(Block, instance=True)
    mock_block.layout_path = LAYOUT
    mock_block.topcell = "TOP"
    mock_block.precision = 1000
    return Measure(parser_input, mock_block, LAYERS)


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


def test_output_measurement_file(measure_instance):
    # Arrange
    test_df = pd.DataFrame({
        'name': ['test_name1', 'test_name2', 'test_name3'],
        'x': [1, 2, 3],
        'y': [11, 22, 33],
    })

    test_output_dir = (Path(__file__).parents[1] / "tests" / "testfiles")
    test_recipe_name = "test_output_recipe_name"
    expected_path = test_output_dir / f"measure_{test_recipe_name}.csv"

    expected_csv = """name,x,y\ntest_name1,1,11\ntest_name2,2,22\ntest_name3,3,33\n"""

    # Act
    measure_instance.output_measurement_file(df=test_df, output_dir=test_output_dir, recipe_name=test_recipe_name)

    # Assert
    print(expected_csv)
    print(expected_path.read_text())
    try:
        assert expected_path.exists()
        assert expected_path.read_text() == expected_csv
    finally:
        if expected_path.exists():
            expected_path.unlink()
        else:
            print('file did not even create')
