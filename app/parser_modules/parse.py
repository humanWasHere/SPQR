import pandas as pd
from abc import ABC, abstractmethod


class FileParser(ABC):
    '''main class of parser modules'''
    @property
    @abstractmethod
    def unit(self) -> str:
        """Return coordinate units for conversion"""
        pass

    @abstractmethod
    def unit_converter(self, unit):
        '''method that converts different unit into dbu'''
        # if unit == "nm":
        #   convert nm to dbu
        #   return unit
        # elif unit == "dbu":
        #   return unit

    @abstractmethod
    def parse_data(self) -> pd.DataFrame:
        """Return a dataframe of gauge name and coordinates in original units
        Column labels MUST BE: name, x, y. Name must be alphanumeric or underscore."""
        pass
