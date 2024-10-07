import argparse
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
from unittest.mock import patch, MagicMock

from app.interfaces.tracker import global_data_tracker


# TEST_TRACKER_OUTPUT = Path(__file__).resolve().parents[2] / "testfiles" / "test_template.json"
TEST_TRACKER_OUTPUT = Path(__file__).resolve().parents[3] / "assets" / "template_SEM_recipe.json"


# Arrange
@pytest.fixture
def mock_parser():
    return MagicMock()


@pytest.fixture
def mock_cli_arguments():
    return argparse.Namespace(running_mode='init', recipe='test_recipe')


@pytest.fixture
def mock_csv_path(tmp_path):
    return tmp_path / "tracker.csv"


@patch('app.interfaces.tracker.define_file_path_from_env')
@patch('app.interfaces.tracker.os.getlogin', return_value='test_user')
@patch('app.interfaces.tracker.datetime')
def test_global_data_tracker(mock_datetime, mock_getlogin, mock_define_file_path_from_env,
                             mock_parser, mock_cli_arguments, mock_csv_path):
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
    assert result_df['Parser'].iloc[0] == 'NA'
    assert result_df['Commands'].iloc[0] == ['init', 'recipe']

# def test_rename_recipe() # TODO
#     assert result_df['Parser'].iloc[0] == 'SSFileParser'
#     assert result_df['Commands'].iloc[0] == ['test', 'recipe-genepy']
