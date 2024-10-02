import argparse
from datetime import datetime
# from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import pytest
import os
from unittest.mock import patch, MagicMock

# from app.interfaces.tracker import check_env_is_prod, setup_tracker, launched_recipe_tracker, user_tracker, parser_tracker, cli_command_tracker
from app.interfaces.tracker import global_data_tracker


TEST_TRACKER_OUTPUT = Path(__file__).resolve().parents[2] / "testfiles" / "test_template.json"


# Arrange
@pytest.fixture
def mock_parser():
    return MagicMock()


@pytest.fixture
def mock_cli_arguments():
    return {'running_mode': 'init', 'recipe': 'test_recipe'}


@pytest.fixture
def mock_csv_path(tmp_path):
    return tmp_path / "tracker.csv"


@patch('app.interfaces.tracker.define_file_path_from_env')
@patch('app.interfaces.tracker.os.getlogin', return_value='test_user')
@patch('app.interfaces.tracker.datetime')
def test_global_data_tracker(mock_datetime, mock_getlogin, mock_define_file_path_from_env, mock_parser, mock_cli_arguments, mock_csv_path):
    # Arrange
    mock_datetime.now.return_value = datetime(2023, 1, 1)
    mock_define_file_path_from_env.return_value = mock_csv_path

    # Act
    result_df = global_data_tracker(mock_parser, mock_cli_arguments)

    # Assert
    # Vérifier que le résultat est un DataFrame
    assert isinstance(result_df, pd.DataFrame)

    # Vérifier que le fichier existe
    assert mock_csv_path.exists()

    # Vérifier que toutes les colonnes attendues sont présentes
    expected_columns = ['Username', 'Parser', 'Commands']
    assert all(column in result_df.columns for column in expected_columns)

    # Vérifier le contenu du DataFrame
    assert result_df['Username'].iloc[0] == 'test_user'
    assert result_df['Parser'].iloc[0] == 'Unused in this case'
    assert result_df['Commands'].iloc[0] == ['init', 'recipe-test_recipe']


# def test_check_env_is_prod():
#     # Arrange
#     tracker_name = "TestTracker"
#     # Act
#     with patch('app.interfaces.tracker.ENVIRONMENT', "production"):
#         # Act
#         result = check_env_is_prod(tracker_name)
#     # Assert
#     assert result is True


# def test_check_env_is_not_prod():
#     # Arrange
#     tracker_name = "TestTracker"
#     # Act
#     result = check_env_is_prod(tracker_name)
#     # Assert
#     assert result is False


# def test_setup_tracker_existing_file():
#     # Arrange
#     csv_filename = "test_file"
#     default_columns = ["column1", "column2"]

#     load_dotenv()
#     csv_path = Path(os.getenv("CSV_TRACKER_PATH"))
#     csv_file = csv_path / f"{csv_filename}_{datetime.now().year}.csv"

#     mock_df = pd.DataFrame({
#         'column1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
#         'column2': [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
#     }, index=["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"])

#     # Act
#     tracker_dataframe, csv_tracker_path, current_month, current_year = setup_tracker(csv_filename, default_columns)

#     # Assert
#     assert csv_tracker_path == csv_file
#     assert current_month == datetime.now().strftime("%B").lower()
#     assert current_year == datetime.now().year
#     pd.testing.assert_index_equal(tracker_dataframe.index, mock_df.index)
#     pd.testing.assert_index_equal(tracker_dataframe.columns, mock_df.columns)

# # ENVIRONMENT = "production"

# # csv_tracker_path = Path(__file__).resolve().parents[2] / "testfiles" / f"{csv_filename}_{current_year}.csv"

# # def test_launched_recipe_tracker():
# #     # Arrange
# #     test
# #     with patch('app.interfaces.tracker.launched_recipe_tracker().csv_tracker_path', csv_tracker_path):
# #         # Act
# #         result = launched_recipe_tracker()
# #     # Assert
# #     assert result ==
# #     Arrange

# @patch('app.interfaces.tracker.check_env_is_prod')
# @patch('app.interfaces.tracker.setup_tracker')
# @patch('app.interfaces.tracker.pd.DataFrame.to_csv')
# def test_launched_recipe_tracker(mock_to_csv, mock_setup_tracker, mock_check_env_is_prod):
#     # Mocking the check_env_is_prod to return True
#     mock_check_env_is_prod.return_value = True

#     # Creating a mock DataFrame
#     mock_df = pd.DataFrame({"launched_recipes": [0]}, index=["current_month"])

#     # Mocking the setup_tracker to return the necessary values
#     mock_setup_tracker.return_value = (mock_df, "mock_csv_path", "current_month")

#     # Act
#     result = launched_recipe_tracker()

#     # Assert
#     assert result is not None
#     assert result.at["current_month", "launched_recipes"] == 1
#     mock_to_csv.assert_called_once_with("mock_csv_path")


# # Arrange
# @patch('app.interfaces.tracker.check_env_is_prod')
# @patch('app.interfaces.tracker.setup_tracker')
# @patch('app.interfaces.tracker.pd.DataFrame.to_csv')
# @patch('app.interfaces.tracker.os.getlogin')
# def test_user_tracker(mock_getlogin, mock_to_csv, mock_setup_tracker, mock_check_env_is_prod):
#     # Mocking the check_env_is_prod to return True
#     mock_check_env_is_prod.return_value = True

#     # Creating a mock DataFrame
#     mock_df = pd.DataFrame({"current_user": [0]}, index=["current_month"])

#     # Mocking the setup_tracker to return the necessary values
#     mock_setup_tracker.return_value = (mock_df, "mock_csv_path", "current_month")

#     # Mocking os.getlogin to return a specific user
#     mock_getlogin.return_value = "current_user"
#     # Act
#     result = user_tracker()
#     # Assert
#     assert result is not None
#     assert result.at["current_month", "current_user"] == 1
#     mock_to_csv.assert_called_once_with("mock_csv_path")


# # Arrange
# @patch('app.interfaces.tracker.check_env_is_prod')
# @patch('app.interfaces.tracker.setup_tracker')
# @patch('app.interfaces.tracker.pd.DataFrame.to_csv')
# @patch('app.interfaces.tracker.logging.error')
# def test_parser_tracker(mock_logging_error, mock_to_csv, mock_setup_tracker, mock_check_env_is_prod):
#     mock_check_env_is_prod.return_value = True
#     mock_df = pd.DataFrame({
#         "HSSParser": [0],
#         "TACRulerParser": [0],
#         "JSONParser": [0],
#         "OPCFieldReverse": [0],
#         "SSFileParser": [0],
#         "CalibreXMLParser": [0]
#     }, index=["current_month"])
#     mock_setup_tracker.return_value = (mock_df, "mock_csv_path", "current_month")
#     # Act
#     result = parser_tracker("HSSParser")
#     # Assert
#     assert result is not None
#     assert result.at["current_month", "HSSParser"] == 1
#     mock_to_csv.assert_called_once_with("mock_csv_path")
#     mock_logging_error.assert_not_called()
#     # Test for an undefined parser
#     # result = parser_tracker("UndefinedParser")
#     # mock_logging_error.assert_called_once_with("Parser UndefinedParser n'est pas défini dans les colonnes du DataFrame.")


# # Arrange
# @patch('app.interfaces.tracker.check_env_is_prod')
# @patch('app.interfaces.tracker.setup_tracker')
# @patch('app.interfaces.tracker.pd.DataFrame.to_csv')
# def test_cli_command_tracker(mock_to_csv, mock_setup_tracker, mock_check_env_is_prod):
#     mock_check_env_is_prod.return_value = True
#     valid_command_list = ["-v", "build", "test", "init", "-c", "-r", "-u", "-l", "-m", "-a", "-j", "-t"]
#     mock_df = pd.DataFrame({command: [0] for command in valid_command_list}, index=["current_month"])
#     mock_setup_tracker.return_value = (mock_df, "mock_csv_path", "current_month")
#     # Act
#     result = cli_command_tracker(["-v", "build", "test"])
#     # Assert
#     assert result is not None
#     assert result.at["current_month", "-v"] == 1
#     assert result.at["current_month", "build"] == 1
#     assert result.at["current_month", "test"] == 1
#     mock_to_csv.assert_called_once_with("mock_csv_path")
#     # Test for an invalid command
#     result = cli_command_tracker(["invalid_command"])
#     assert result.at["current_month", "-v"] == 1  # Ensure previous values are unchanged
#     assert result.at["current_month", "build"] == 1
#     assert result.at["current_month", "test"] == 1
#     mock_to_csv.assert_called_with("mock_csv_path")
