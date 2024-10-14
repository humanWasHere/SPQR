import pandas as pd
from app.parsers.csv_parser import HSSParser


def test_parse_data(test_files):
    # Arrange
    testfile = test_files / "test_env_genepy.csv"
    hss_parser_instance = HSSParser(testfile)
    expected_data = pd.DataFrame({
        'name': ['A', 'B'],
        'x': [100, 200],
        'y': [300, 400],
        'x_ap': [500, 600],
        'y_ap': [700, 800]
    })

    # Act
    result = hss_parser_instance.parse_data()

    # Assert
    assert result.columns.to_list() == expected_data.columns.to_list()


def test_parse_hss(test_files):
    # Arrange
    # must cover 2 following cases : Type.1,Unnamed: 6
    short_testfile = test_files / "short_eps_data_csv.csv"
    hss_parser_instance = HSSParser(short_testfile)

    expected_tables = {
        '<EPS_Data>': pd.DataFrame({
            'EPS_ID': [1, 2],
            'Type': [1, 1],
            'Move_X': [11000, 16500],
            'Move_Y': [-133000, -133000],
            'Mode': [1, 1],
            'EPS_Name': ['CDvSP_CD100_SP70_V', 'CDvSP_CD100_SP90_V'],
            'AP1_X': [0, 0],
            'AP1_Y': [0, 0]
        })
    }
    expected_constant_sections = {
        "<FileID>": "LIDP00",
        "<Version>": '6',
        "<Revision>": '0'
    }

    # Act
    constant_sections, table_sections = hss_parser_instance.parse_hss()

    # Assert
    pd.testing.assert_frame_equal(table_sections['<EPS_Data>'], expected_tables['<EPS_Data>'])
    assert constant_sections == expected_constant_sections
