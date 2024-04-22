import pytest
import subprocess
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.data_structure import Block
from app.measure.measure import Measure
from app.interfaces.calibre_python import lance_script
# FIXME layout and layers are not valid file paths


@pytest.fixture
def layout():
    return "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"

@pytest.fixture
def layers():
    return ["1.0"]

@pytest.fixture
def measure_instance(layout, layers):
    parser_input = pd.DataFrame({
        "Name": ["parser_gauge_name1", "parser_gauge_name2", "parser_gauge_name3", "parser_gauge_name4"],
        "X_point": [12, "unknown", 13, 14], "Y_point": [22, 12, 42, "unknown"]
    })
    return Measure(parser_input, layout, layers, 10000, unit='dbu')


def test_creation_script_tmp(measure_instance):
    # FIXME 'marche pas :(
    # TODO Black box kind of test -> is it good ?
    # Arrange
    # env setting
    output = "output_file.txt"
    search_area = 5
    unit = "nm"
    # expected coords
    expected_output = Path.home() / "tmp" / "Script_tmp.tcl"

    # Act
    result = measure_instance.creation_script_tmp(output, search_area, unit)

    # Assert
    assert isinstance(result, Path)
    assert result.exists()
    assert result.name == "Script_tmp.tcl"
    assert result.parent == Path.home() / "tmp"
    assert result == expected_output


def test_run_measure(measure_instance):
    # Arrange
    expected_columns = ['Gauge name', 'X_point', 'Y_point', 'Value']
    expected_shape = (2, 4)

    # Mock sequence_auto method to return expected dataframe
    # measure_instance.sequence_auto = lambda: test_parser_df
    measure_instance.creation_script_tmp = lambda output, search_area=5, unit="nm": "script.tcl"
    measure_instance.lance_script = lambda script, debug="/dev/null", verbose=True: "machine1"
    # measure_instance.creation_script_tmp()
    # measure_instance.lance_script()

    # Act
    result = measure_instance.run_measure()

    print(result)

    # Assert
    assert isinstance(result, pd.DataFrame)
    assert result.columns.tolist() == expected_columns
    assert result.shape == expected_shape
