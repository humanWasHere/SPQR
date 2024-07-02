import pandas as pd
import pytest

from app.parsers.parse import OPCfieldReverse


@pytest.fixture
def opcfield():
    return OPCfieldReverse(0, 0, 15, 15, 2, 1, 0, 5, 'B', 2)


def test_opcfield_reverse_base_dataframe(opcfield):
    expected = pd.DataFrame.from_dict({
        'B2': {'x': 0, 'y': 0, 'row': 2, 'col': 'B', 'name': 'B2'},
        'C2': {'x': 15, 'y': 0, 'row': 2, 'col': 'C', 'name': 'C2'}
    }, orient='index')
    pd.testing.assert_frame_equal(opcfield.opcfield_reverse(), expected,
                                  check_like=True, obj='opcfield_reverse output')


def test_opcfield_reverse_with_ap(opcfield):
    expected = pd.DataFrame.from_dict({
        'B2': {'x': 0, 'y': 0, 'row': 2, 'col': 'B', 'name': 'B2', 'x_ap': 0, 'y_ap': 5},
        'C2': {'x': 15, 'y': 0, 'row': 2, 'col': 'C', 'name': 'C2', 'x_ap': 0, 'y_ap': 5}
    }, orient='index')
    pd.testing.assert_frame_equal(opcfield.parse_data(), expected,
                                  check_like=True, obj='parse_data output')
