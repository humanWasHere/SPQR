import pandas as pd
import numpy as np
from pathlib import Path
from .parse import FileParser


# TODO
# input and print should be at user's destination -> in GUI
# checker de présence des colonnes 'name', 'coord x', 'coord y' 'unit' ?
# interaction with user should be better -> GUI


class SSFileParser(FileParser):
    """Parse OPCField descriptor "ss" files in Genepy format or legacy (undefined) format"""

    unit = None

    def __init__(self, file_to_parse: str | Path, is_genepy=False):
        self.ssfile = Path(file_to_parse)
        self.is_genepy = is_genepy
        self.data: pd.DataFrame

    @staticmethod
    def rename_column_name(dataframe) -> pd.DataFrame:
        """this method allows user to rename the column imported if it is not already in valid format (NaN value)"""
        set_title_names = []  # TODO add all existing columns first
        for col in dataframe.columns:
            if pd.isna(dataframe.loc[0, col]):
                while True:
                    user_input = input(f"Enter a value to replace NaN in column {col}: ")
                    if user_input not in set_title_names:
                        set_title_names.append(user_input)
                        break
                    else:
                        print("Value already set !")
                dataframe.loc[0, col] = user_input  # bad indentation ? should be before break ?
        return dataframe

    def parse_data(self) -> pd.DataFrame:
        '''this method decides wether you need to parse a genepy ssfile or not'''
        if self.is_genepy:
            self.genepy_to_dataframe()
            self.post_parse()
            return self.data
        else:
            return self.ssfile_to_dataframe()

    def ssfile_to_dataframe(self) -> pd.DataFrame:
        '''converts a generic ssfile to a formatted parsing'''
        # print('1. ssfile parsing')  # TODO log
        with open(self.ssfile, 'r') as f:
            # counts the number of columns (separated by tabs) in the first line of the file (header / line with column names)
            header_column_number = len(f.readline().strip().split('\t'))
            max_column_number = max(len(line.split('\t')) for line in f)
        self.data = pd.read_csv(self.ssfile, sep='\t', names=range(max_column_number), on_bad_lines='warn', encoding='utf-8')
        # if NaN values in first line of the file (assumed title line)
        if self.data.iloc[0].isnull().values.any():
            print("There is undefined columns name in your dataframe. Have a look :")
            print(self.data.to_string())
            self.data = self.rename_column_name(self.data)
        if header_column_number != max_column_number:
            print("Reminder that the dataframe does not match expectations :( make it better !")
        # if not self.data.empty:  # TODO add more logic - log
            # print('\tssfile parsing done')
        return self.data

    def genepy_to_dataframe(self) -> pd.DataFrame:
        '''converts a genepy ssfile to a formatted parsing'''
        # print('1. genepy ssfile parsing')  # TODO log
        self.data = pd.read_csv(self.ssfile, sep='\t', header=0, on_bad_lines='warn', encoding='utf-8')
        self.data['UNIT_COORD'] = 'nm'
        self.data['Name'] = self.data['Name'].astype(str) + "_" + self.data['Pattern'].astype(str)
        print(self.data)
        # TODO add validation (column number / column name)
        self.unit = self.data.UNIT_COORD.unique()[0].lower()  # TODO normaliser l'unite d'entree par point -> if exists else get via layout ?
        # self.check_x_y_is_int()
        # if not self.data.empty:  # TODO add more logic - log
        #    print('\tgenepy ssfile parsing done')
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


class OPCfieldReverse(FileParser):

    unit = None

    def __init__(self, origin_x: float, origin_y: float, step_x: float, step_y: float, num_steps_x: int, num_steps_y: int, origin_letter="A", origin_number=1) -> None:
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.step_x = step_x
        self.step_y = step_y
        self.num_steps_x = num_steps_x
        self.num_steps_y = num_steps_y
        self.origin_letter = origin_letter
        self.origin_number = origin_number
        self.data = pd.DataFrame

    def opcfield_reverse(self) -> pd.DataFrame:
        """Build an OPCField coordinate matrix"""
        # FIXME works only in um ?
        x_coords = np.arange(self.origin_x, self.origin_x + self.step_x * self.num_steps_x, self.step_x)
        y_coords = np.arange(self.origin_y, self.origin_y + self.step_y * self.num_steps_y, self.step_y)
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
        self.unit = 'um'
        # ask x_ap in __init__
        # if not x_ap:
        self.data['x_ap'] = np.nan
        self.data['y_ap'] = np.nan
        return self.data

    def parse_data(self) -> pd.DataFrame:
        '''returns df'''
        self.opcfield_reverse()
        return self.data
