import pandas as pd
from abc import ABC, abstractmethod


class DataframeValidator:
    # TODO: implement or rework
    SCHEMA = {
        'name': "string",
        'x': int,
        'y': int,
        'x_ap': int,
        'y_ap': int,
        'orientation': "string",
        'target_cd': int,
        'magnification': int
    }

    @classmethod
    def validate(cls, func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            cls.validate_schema(data)
        return wrapper

    @classmethod
    def validate_schema(cls, dataframe) -> None:
        for col_name, series in dataframe.items():
            # TODO try conversion
            assert series.dtype == cls.SCHEMA[col_name], \
                f"Wrong dtype for {col_name}: expected {cls.SCHEMA[col_name]} got {series.dtype}"


class FileParser(ABC):
    """Main interface for parser modules."""
    @property
    @abstractmethod
    def unit(self) -> str:
        """Return coordinate units for conversion"""

    # @DataframeValidator.validate
    @abstractmethod
    def parse_data(self) -> pd.DataFrame:
        """Return a dataframe of gauge name and coordinates in original units
        Column labels MUST BE: name, x, y. Name must be alphanumeric or underscore."""

    def parse_data_dbu(self, precision):
        dbu_per_unit = {'dbu': 1, 'nm': precision/1000, 'micron': precision}
        data = self.parse_data()
        data[['x', 'y', 'x_ap', 'y_ap']] *= dbu_per_unit[self.unit]
        return data.astype(int, errors="ignore")

    # # @abstractmethod
    # def unit_converter(self, precision):  # precision is linked to a layout...
    #     """Converts coordinates from source unit to DBU"""
    #     return

    # # @abstractmethod
    # # def check_x_y_is_int(self) -> pd.DataFrame:
    # #     '''checks if x and y columns contains int values. If not converts it'''
    # #     pass

    # # def run_parsing(self):
    # #     try:
    # #         parser_instance = CalibreXMLParser(parser, block.precision)
    # #         data_parsed = parser_instance.parse_data()
    # #         # TODO calibre ruler checker -> verify file extension vs file content
    # #     except ParseError:
    # #         parser_instance = SsfileParser(parser, is_genepy=True)
    # #         data_parsed = parser_instance.parse_data().iloc[60:70]