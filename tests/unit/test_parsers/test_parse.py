from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.parsers.parse import OPCFieldReverse, get_parser
from app.parsers import (CalibreXMLParser, HSSParser, JSONParser, SSFileParser, TACRulerParser)


@pytest.fixture
def opcfield():
    return OPCFieldReverse(0, 0, 15, 15, 2, 1, 'B', 2)


def test_get_parser(test_files):
    other_testfiles = Path('/work/opc/all/users/banger/dev/semchef/examples/')
    assert get_parser('') is OPCFieldReverse
    assert get_parser(other_testfiles / 'banger_MP03K_ACTI_scanmat_PH.csv') is HSSParser
    assert get_parser(other_testfiles / 'tacx_rulers.txt') is TACRulerParser
    assert get_parser(other_testfiles / 'calibre_rulers.xml') is CalibreXMLParser
    assert get_parser(test_files / 'test_template.json') is JSONParser
    assert get_parser(test_files / 'ssfile_proto.txt') is SSFileParser


def test_opcfield_reverse_base_dataframe(opcfield):
    expected = pd.DataFrame.from_dict({
        'B2': {'x': 0, 'y': 0, 'row': 2, 'col': 'B', 'name': 'B2'},
        'C2': {'x': 15, 'y': 0, 'row': 2, 'col': 'C', 'name': 'C2'}
    }, orient='index')
    pd.testing.assert_frame_equal(opcfield.opcfield_reverse(), expected,
                                  check_like=True, obj='opcfield_reverse output')


def test_opcfield_reverse_with_ap(opcfield):
    expected = pd.DataFrame.from_dict({
        'B2': {'x': 0, 'y': 0, 'row': 2, 'col': 'B', 'name': 'B2', 'x_ap': np.nan, 'y_ap': np.nan},
        'C2': {'x': 15, 'y': 0, 'row': 2, 'col': 'C', 'name': 'C2', 'x_ap': np.nan, 'y_ap': np.nan}
    }, orient='index')
    pd.testing.assert_frame_equal(opcfield.parse_data(), expected,
                                  check_like=True, obj='parse_data output')


def test_parse_data(opcfield):
    # FIXME doublon, supprimer
    # Arrange
    expected_data = pd.DataFrame({
        'x': [0, 15],
        'y': [0, 0],
        'row': [2, 2],
        'col': ['B', 'C'],
        'name': ['B2', 'C2'],
        'x_ap': [np.nan, np.nan],
        'y_ap': [np.nan, np.nan]
    })
    expected_data.index = expected_data['name']
    expected_data.index.name = None
    data = opcfield.parse_data()

    # Vérification que les colonnes 'x_ap' et 'y_ap' sont présentes dans le DataFrame
    print(data.index)
    print(expected_data.index)
    assert 'x_ap' in data.columns
    assert 'y_ap' in data.columns
    pd.testing.assert_frame_equal(data, expected_data)
    # pd.testing.assert_frame_equal(opcfield.parse_data(), expected_data)
