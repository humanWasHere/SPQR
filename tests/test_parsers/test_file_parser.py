import pandas as pd

from app.parsers.file_parser import FileParser


class TestConcreteFileParser(FileParser):
    def __init__(self, unit):
        self._unit = unit

    @property
    def unit(self) -> str:
        return self._unit

    def parse_data(self) -> pd.DataFrame:
        # Example implementation, replace with actual data parsing logic
        return pd.DataFrame({
            'x': [1, 2],
            'y': [3, 4],
            'x_ap': [5, 6],
            'y_ap': [7, 8]
        })


def test_parse_data_dbu():
    # Arrange
    precision = 1000
    file_parser_instance = TestConcreteFileParser(unit='micron')
    expected_data = pd.DataFrame({
        'x': [1000, 2000],
        'y': [3000, 4000],
        'x_ap': [5000, 6000],
        'y_ap': [7000, 8000]
    })

    # Act
    result = file_parser_instance.parse_data_dbu(precision)

    print(result)
    print(expected_data)
    # Assert
    pd.testing.assert_frame_equal(result, expected_data)
