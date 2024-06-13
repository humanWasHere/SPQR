from abc import ABC, abstractmethod
import pandas as pd


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
