import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


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


class OPCfieldReverse(FileParser):

    unit = None

    def __init__(self, origin_x: float, origin_y: float, step_x: float, step_y: float,
                 num_steps_x: int, num_steps_y: int, origin_letter="A", origin_number=1) -> None:
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.step_x = step_x
        self.step_y = step_y
        self.num_steps_x = num_steps_x
        self.num_steps_y = num_steps_y
        self.origin_letter = origin_letter
        self.origin_number = origin_number
        self.data: pd.DataFrame

    def opcfield_reverse(self) -> pd.DataFrame:
        """Build an OPCField coordinate matrix in arbitrary unit"""
        x_coords = np.arange(
            self.origin_x, self.origin_x + self.step_x * self.num_steps_x, self.step_x)
        y_coords = np.arange(
            self.origin_y, self.origin_y + self.step_y * self.num_steps_y, self.step_y)
        xx, yy = np.meshgrid(x_coords, y_coords)
        coords = np.vstack([xx.ravel(), yy.ravel()]).T
        self.data = pd.DataFrame(coords.round(3), columns=['x', 'y'])

        rows = np.repeat(np.arange(self.num_steps_y), self.num_steps_x)
        cols = np.tile(np.arange(self.num_steps_x), self.num_steps_y)
        self.data['row'] = rows + self.origin_number

        # nested function that generates column names with following logic : A-Z, AA-ZZ, etc.
        def get_column_letter(col_num):
            col_letter_str = ''
            while col_num >= 0:
                col_num, remainder = divmod(col_num, 26)
                col_letter_str = chr(65 + remainder) + col_letter_str  # chr 65 = A
                col_num -= 1
            return col_letter_str

        self.data['col'] = [get_column_letter(col) for col in cols]
        # self.data['col'] = [chr(ord(self.origin_letter.upper()) + col) for col in cols]
        self.data.index = self.data['col'] + self.data['row'].astype(str)
        self.data['name'] = self.data.index
        # TODO dependency ?
        self.unit = 'um'
        # ask x_ap in __init__
        # if not x_ap:
        self.data['x_ap'] = np.nan
        self.data['y_ap'] = np.nan
        return self.data

    def parse_data(self) -> pd.DataFrame:
        self.opcfield_reverse()
        return self.data

# def run_parsing():
# '''this method holds the logic of parser selection'''
