import pytest
from unittest.mock import patch, MagicMock
import subprocess
import pandas as pd
from pathlib import Path
import tempfile
from app.measure_modules.measure import Measure

# FIXME layout and layers are not valid file paths


class TestMeasure:

    @pytest.fixture
    def layout(self):
        return "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/COMPLETED_TEMPLATE.gds"

    @pytest.fixture
    def layers(self):
        return ["1.0"]

    @pytest.fixture
    def measure_instance(self, layout, layers):
        parser_input = pd.DataFrame({"Name": ["parser_gauge_name1", "parser_gauge_name2", "parser_gauge_name3", "parser_gauge_name4"], "X_point": [12, "unknown", 13, 14], "Y_point": [22, 12, 42, "unknown"]})  # , index=[0])
        coords = pd.DataFrame({"Gauge ": ['A', 'B', 'C', 'D'], "Value": [1, 2, 3, 4]})
        return Measure(parser_input, coords, layout, layers)

    # exemple de test - non pertinent ici
    def test_find_host(self, measure_instance):
        # Arrange
        expected_host = "machine1"
        subprocess_result = subprocess.CompletedProcess(args=["echo", expected_host], returncode=0, stdout=expected_host.encode())
        subprocess.run = lambda *args, **kwargs: subprocess_result

        # Act
        result = measure_instance.find_host()

        # Assert
        assert isinstance(result, str)
        assert result == expected_host

    def test_layout_peek(self, measure_instance):
        # Arrange
        expected_output = b'layout_peek_output'
        expected_options = ["-precision", "-topcell", "-layers", "-bbox"]
        measure_instance.layout = self.layout
        subprocess_result = subprocess.CompletedProcess(args=["echo", expected_output], returncode=0, stdout=expected_output)
        subprocess.run = lambda *args, **kwargs: subprocess_result
        measure_instance.find_host = lambda: "machine1"

        # Act
        result = measure_instance.layout_peek(*expected_options)

        # Assert
        print(f"Actual output: {result}")
        assert isinstance(result, bytes)
        assert result == expected_output

    def test_creation_script_tmp(self, measure_instance):
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

    @patch('subprocess.Popen')
    def test_lance_script(self, measure_instance):
        # Arrange
        tmp_script_input = Path.home() / "tmp" / "Script_tmp.tcl"
        expected_host = "machine1"
        subprocess_result = subprocess.CompletedProcess(args=["echo", expected_host], returncode=0, stdout=expected_host.encode())
        subprocess.Popen = lambda *args, **kwargs: subprocess_result
        measure_instance.find_host = lambda: expected_host

        # Configure mock find_host method
        measure_instance.find_host = MagicMock(return_value=expected_host)
        measure_instance.creation_script_tmp(Path.home() / "tmp" / "Script_tmp.tcl")

        # Act
        # result = measure_instance.lance_script(script, debug)
        result = measure_instance.lance_script(tmp_script_input)

        # Assert
        assert result is not None
        assert isinstance(result, str)
        assert result == expected_host

    def test_sequence_auto(self, measure_instance):
        # This tests is meant to be as white box as possible, using mock objects
        # Arrange
        expected_df = pd.DataFrame({'name': ['A', 'B', 'C'], 'value': [1, 2, 3]})
        # init function dependencies
        measure_instance.creation_script_tmp = lambda output, search_area=5, unit="nm": "script.tcl"
        measure_instance.lance_script = lambda script, debug="/dev/null", verbose=True: "machine1"
        # init temp file
        tempfile_result = tempfile.NamedTemporaryFile()
        tempfile_result.write(expected_df.to_csv(index=False).encode())
        tempfile_result.seek(0)
        tempfile.NamedTemporaryFile = lambda *args, **kwargs: tempfile_result

        # Act
        result = measure_instance.sequence_auto()

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert result.equals(expected_df)

    def test_clean_unknown(self, measure_instance):
        # Arrange
        expected_df = pd.DataFrame({'col1': [1], 'col2': [4], 'col3': [7], 'col4': ['chaine1']})
        dirty_df = pd.DataFrame({'col1': [1, 2, 'unknown'], 'col2': [4, 'unknown', 6], 'col3': [7, 8, 9], 'col4': ['chaine1', 'chaine2', 'chaine3']})

        # Act
        result = measure_instance.clean_unknown(dirty_df)

        # .astype('int64')
        # Assert
        assert isinstance(result, pd.DataFrame)
        # assert pd.testing.assert_frame_equal(result, expected_df)
        assert result.dtypes.all() == expected_df.dtypes.all()

    def test_run_measure(self, measure_instance):
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
