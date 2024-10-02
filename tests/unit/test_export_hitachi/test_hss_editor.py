# import json
from pathlib import Path

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

# from app.data_structure import Block
from app.export_hitachi.hss_editor import RecipeEditor
# from app.parsers.json_parser import import_json
# from app.parsers.json_parser import JSONParser


# TODO make relative file path for "test_template.json"

# LAYOUT_TESTCASE = Path(__file__).resolve().parents[1] / "testfiles" / "COMPLETED_TEMPLATE.gds"
TEST_TEMPLATE = Path(__file__).resolve().parents[2] / "testfiles" / "test_template.json"
RECIPE_NAME_CONF = "recipe_to_modify"
JSON_RECIPE = Path(__file__).resolve().parents[4] / "spqr-assets" / "spqr_test_ressources" / "test_env_genepy.json"
CSV_RECIPE = Path(__file__).resolve().parents[4] / "spqr-assets" / "spqr_test_ressources" / "test_env_genepy.csv"


class TestRecipeEditor:

    @pytest.fixture
    def test_json_user_config(self):
        return {
            "recipe_to_modify": {
                "recipe_name": "test_edit_temp_output",
                "output_dir": Path(__file__).resolve().parent,
                "coord_file": "/work/opc/all/users/chanelir/spqr-assets/spqr_test_ressources/ssfile_proto.txt",
                "layout": "/work/opc/all/users/chanelir/spqr-assets/spqr_test_ressources/COMPLETED_TEMPLATE.gds",
                "layers": ["1.0"],
                "ap1_template": "",
                "ap1_mag": 50000,
                "ep_template": "",
                "eps_template": "OPC_EPS_Template",
                "magnification": 200000,
                "mp_template": "X90M_GATE_PH",
                "step": "PH",
                "opcfield_x": "",
                "opcfield_y": "",
                "step_x": "",
                "step_y": "",
                "num_step_x": "",
                "num_step_y": ""
            }
        }

    # should match config recipe name
    # @pytest.fixture
    # def global_recipe_name(self):
    #     return "recipe_to_modify"

    # @pytest.fixture
    # def csv_recipe_path(self):
    #     return Path(__file__).resolve().parents[4] / "spqr-assets" / "spqr_test_ressources" / "test_env_genepy.csv"

    # @pytest.fixture
    # def json_recipe_path(self):
    #     return Path(__file__).resolve().parents[4] / "spqr-assets" / "spqr_test_ressources" / "test_env_genepy.json"

    # @pytest.fixture
    # def block_instance(self):
    #     """Mock the execution of layout peek"""
    #     mock_block = mock.create_autospec(Block, instance=True)
    #     mock_block.layout_path = "fake.oas"
    #     mock_block.topcell = "TOP"
    #     mock_block.precision = 1000
    #     return mock_block

    # @pytest.fixture
    # def core_data(self):
    #     return pd.DataFrame({
    #         'name': ['Name1', 'Name2', 'Name3'],
    #         'x': [5500, 5500, 5500],
    #         'y': [-94500, -94500, -94500],
    #         'x_ap': [0, 0, 0],
    #         'y_ap': [0, 0, 0],
    #         'x_dim': [0, 0, 0],
    #         'y_dim': [0, 0, 0]
    #     })

    # @pytest.fixture
    # def hss_editor_instance_json(self, test_json_user_config, global_recipe_name, json_recipe_path):
    #     return RecipeEditor(json_conf=test_json_user_config, recipe_name_conf=global_recipe_name, recipe=json_recipe_path)

    @pytest.fixture
    def hss_editor_instance_json(self, test_json_user_config):
        return RecipeEditor(json_conf=test_json_user_config, recipe_name_conf=RECIPE_NAME_CONF, recipe=JSON_RECIPE)

    # @pytest.fixture
    # def hss_editor_instance_csv(self, test_json_user_config, global_recipe_name, csv_recipe_path):
    #     return RecipeEditor(json_conf=test_json_user_config, recipe_name_conf=global_recipe_name, recipe=csv_recipe_path)

    @pytest.fixture
    def hss_editor_instance_csv(self, test_json_user_config):
        return RecipeEditor(json_conf=test_json_user_config, recipe_name_conf=RECIPE_NAME_CONF, recipe=CSV_RECIPE)

    def test_get_columns_for_edition_json(self, hss_editor_instance_json):
        """Test get_columns_for_edition method with CSV recipe."""
        # Arrange
        table_sections = {
            '<EPS_Data>': pd.DataFrame({
                'EPS_Name': ['CDvSP_CD100_SP70_V', 'CDvSP_CD100_SP90_V'],
                'Move_X': [11000, 16500],
                'Move_Y': [-133000, -133000],
                'AP1_X': [0, 0],
                'AP1_Y': [0, 0],
                'MP1_TargetCD': [100, 100],
                'MP1_TargetCD': [100, 100]
            })
        }
        # hss_editor_instance_json.table_sections = table_sections

        # Act
        result = hss_editor_instance_json.get_columns_for_edition(table_sections)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ['name', 'x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']
        # pd.testing()

    def test_get_columns_for_edition_csv(self, hss_editor_instance_csv):
        """Test get_columns_for_edition method with CSV recipe."""
        # Arrange
        table_sections = {
            '<EPS_Data>': pd.DataFrame({
                'EPS_Name': ['CDvSP_CD100_SP70_V', 'CDvSP_CD100_SP90_V'],
                'Move_X': [11000, 16500],
                'Move_Y': [-133000, -133000],
                'AP1_X': [0, 0],
                'AP1_Y': [0, 0],
                'MP1_TargetCD': [100, 100],
                'MP1_TargetCD': [100, 100]
            })
        }
        hss_editor_instance_csv.table_sections = table_sections

        # Act
        result = hss_editor_instance_csv.get_columns_for_edition(table_sections)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ['name', 'x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']
        # assert pd.testing()

    def test_check_recipe_validity_json(self, hss_editor_instance_json):
        """Test check_recipe_validity method with JSON recipe."""
        # Arrange
        print(hss_editor_instance_json.table_sections)
        # hss_editor_instance_json.json_template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"
        # hss_editor_instance_json.recipe = hss_editor_instance_json.json_template  # Mocking the recipe to be the same as the template for simplicity
        # hss_editor_instance_json.recipe = hss_editor_instance_json.json_template  # Mocking the recipe to be the same as the template for simplicity

        # Act
        is_valid = hss_editor_instance_json.check_recipe_validity()

        # Assert
        assert isinstance(is_valid, bool)
        assert is_valid

    def test_check_recipe_validity_csv(self, hss_editor_instance_csv):
        """Test check_recipe_validity method with CSV recipe."""
        # Arrange
        # hss_editor_instance_csv.json_template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"
        # hss_editor_instance_csv.constant_sections = import_json(hss_editor_instance_csv.json_template)
        # hss_editor_instance_csv.table_sections = import_json(hss_editor_instance_csv.json_template)

        # Act
        is_valid = hss_editor_instance_csv.check_recipe_validity()

        # Assert
        assert isinstance(is_valid, bool)
        assert is_valid

    @patch('builtins.input', side_effect=['<Unit>', 'Coordinate', '', '2000', ''])
    def test_section_edit_single_value(self, mock_input, hss_editor_instance_csv):
        """Test section_edit method for single value modification."""
        # Arrange
        expected_value = '2000'

        # Act
        result = hss_editor_instance_csv.section_edit()
        print(result)

        # Assert
        assert result is None
        assert hss_editor_instance_csv.table_sections['<Unit>'].loc[0, 'Coordinate'] == expected_value

    @patch('builtins.input', side_effect=['<EPS_Data>', 'Move_X', '', '250', ''])
    def test_section_edit_full_column(self, mock_input, hss_editor_instance_csv):
        """Test section_edit method for full column modification."""
        # Arrange
        expected_value = '250'

        # Act
        result = hss_editor_instance_csv.section_edit()

        # Assert
        assert result is None
        assert (hss_editor_instance_csv.table_sections['<EPS_Data>']['Move_X'] == expected_value).all()

    @patch('builtins.input', side_effect=['', ''])
    def test_section_edit_no_modification(self, mock_input, hss_editor_instance_csv):
        """Test section_edit method with no modification."""
        # Arrange

        # Act
        result = hss_editor_instance_csv.section_edit()

        # Assert
        assert result is False

    @patch('pathlib.Path.glob')
    def test_rename_recipe_existing_files(self, mock_glob, hss_editor_instance_csv):
        """Test rename_recipe method when there are existing files with similar names."""
        # Arrange
        mock_file_1 = MagicMock(spec=Path)
        mock_file_1.name = 'test_env_genepy_1.csv'
        mock_file_2 = MagicMock(spec=Path)
        mock_file_2.name = 'test_env_genepy_2.csv'
        mock_glob.return_value = [mock_file_1, mock_file_2]
        expected_new_name = hss_editor_instance_csv.recipe.parent / "test_env_genepy_3.csv"

        # Act
        new_recipe_name = hss_editor_instance_csv.rename_recipe()

        # Assert
        assert new_recipe_name == expected_new_name.resolve()

    @patch.object(RecipeEditor, 'check_recipe_validity', return_value=True)
    @patch.object(RecipeEditor, 'section_edit', return_value=True)
    @patch.object(RecipeEditor, 'rename_recipe', return_value=Path('/fake/path/short_eps_data_json_1.json'))
    @patch.object(RecipeEditor, 'output_dataframe_to_csv')
    @patch.object(RecipeEditor, 'output_dataframe_to_json')
    def test_run_recipe_edit_success(self, mock_check_validity, mock_section_edit, mock_rename, mock_output_csv, mock_output_json, hss_editor_instance_csv):
        """Test run_recipe_edit method for successful recipe modification."""
        # Arrange

        # Act
        hss_editor_instance_csv.run_recipe_edit()

        # Assert
        mock_check_validity.assert_called_once()
        mock_section_edit.assert_called_once()
        mock_rename.assert_called_once()
        mock_output_csv.assert_called_once()
        mock_output_json.assert_called_once()
        assert hss_editor_instance_csv.recipe_output_file == Path('/fake/path/short_eps_data_json_1.json').resolve()
