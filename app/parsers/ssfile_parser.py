from pathlib import Path

import pandas as pd

from .parse import FileParser

# TODO checker de présence des colonnes 'name', 'coord x', 'coord y' 'unit' ?


class SSFileParser(FileParser):
    """Parse OPCField descriptor "ss" files in Genepy format or legacy (undefined) format"""

    unit = None

    def __init__(self, file_to_parse: str | Path, is_genepy: bool = True):
        self.ssfile = Path(file_to_parse)
        self.is_genepy = is_genepy
        self.data: pd.DataFrame

    def parse_data(self) -> pd.DataFrame:
        """Call the dedicated parsing logic depending on OPCField type"""
        if self.is_genepy:
            self.genepy_to_dataframe()
            self.post_parse()
            return self.data
        # if not self.data.empty:  # TODO add more logic - log
            # print('\tssfile parsing done')

    def genepy_to_dataframe(self) -> pd.DataFrame:
        '''converts a genepy ssfile to a formatted parsing'''
        # print('1. genepy ssfile parsing')  # TODO log
        self.data = pd.read_csv(self.ssfile, sep='\t', on_bad_lines='warn')
        if 'UNIT_COORD' not in self.data and 'Name' in self.data:
            # genepat testcase workaround
            self.data['UNIT_COORD'] = 'nm'
            self.data['Name'] = (self.data['Name'].astype(str) + "_"
                                 + self.data['Pattern'].astype(str))
        # TODO add validation (column number / column name)
        self.unit = self.data.UNIT_COORD.unique()[0].lower()
        # TODO normaliser l'unite d'entree par point -> if exists else get via layout ?
        return self.data

    def post_parse(self) -> None:
        '''checks all columns for empty values and format names'''
        self.data.dropna(axis=1, how='all', inplace=True)
        self.data.rename(
            columns={'Name': "name",
                     'X_coord_Pat': "x",
                     'Y_coord_Pat': "y",
                     'X_coord_Addr': "x_ap",
                     'Y_coord_Addr': "y_ap"},
            inplace=True
        )
        self.data = self.change_coord_to_relative(self.data)
        # TODO renaming logic?

    @staticmethod
    def change_coord_to_relative(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Modify the AP coordinates in-place from absolute to relative."""
        # FIXME is good ?
        dataframe.x_ap -= dataframe.x
        dataframe.y_ap -= dataframe.y
        # TODO add relative_coord_x/y columns in dataframe ? replace data ? return columns ?
        return dataframe
