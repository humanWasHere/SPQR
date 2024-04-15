import pandas as pd
from abc import ABC, abstractmethod


class DataframeValidator:
    # TODO: implement or rework
    SCHEMA = {
        'name': str,
        'x': int,
        'y': int,
        'x_ap': int,
        'y_ap': int,
        'orient': str,
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
            assert series.dtype == cls.SCHEMA[col_name], f"wrong dtype for {col_name}: expected {cls.SCHEMA[col_name]} got {series.dtype}"


class FileParser(ABC):
    """Main interface for parser modules."""
    @property
    @abstractmethod
    def unit(self) -> str:
        """Return coordinate units for conversion"""
        pass

    # @DataframeValidator.validate
    @abstractmethod
    def parse_data(self) -> pd.DataFrame:
        """Return a dataframe of gauge name and coordinates in original units
        Column labels MUST BE: name, x, y. Name must be alphanumeric or underscore."""
        pass

    def parse_data_dbu(self, precision):
        dbu_per_unit = {'dbu': 1, 'nm': precision/1000, 'micron': precision}
        data = self.parse_data()
        data[['x', 'y', 'x_ap', 'y_ap']] *= dbu_per_unit[self.unit]
        return data
