import pandas as pd
from pathlib import Path
from .parse import FileParser


# TODO
# input and print should be at user's destination -> in GUI
# traitement des NaN value
# est ce que genepy set ses unités pour la colonnes/ligne entière à chaque fois ?
# checker de présence des colonnes 'name', 'coord x' et 'coord y' ?
# interaction with user should be better -> GUI


class SsfileParser(FileParser):
    unit = None

    '''this class is used to parse ssfiles which can be genepy ssfile or other (formatted to convention ?) ssfiles'''
    def __init__(self, file_to_parse: str | Path, is_genepy=False):
        self.ssfile = file_to_parse
        self.is_genepy = is_genepy
        self.data: pd.DataFrame

    def ssfile_to_dataframe(self) -> pd.DataFrame:
        with open(self.ssfile, 'r') as f:
            # counts the number of columns (separated by tabs) in the first line of the file (header / line with column names)
            header_column_number = len(f.readline().strip().split('\t'))
            max_column_number = max(len(line.split('\t')) for line in f)
        df = pd.read_csv(self.ssfile, sep='\t', names=range(max_column_number), on_bad_lines='warn', encoding='utf-8')
        # if NaN values in first line of the file (assumed title line)
        if df.iloc[0].isnull().values.any():
            print("There is undefined columns name in your dataframe. Have a look :")
            print(df.to_string())
            df = self.drop_empty_column(
                self.rename_title(df))
        if header_column_number != max_column_number:
            print(
                "Reminder that the dataframe does not match expectations :( make it better !")
        return df

    def genepy_to_dataframe(self) -> pd.DataFrame:
        self.data = pd.read_csv(self.ssfile, sep='\t', header=0, on_bad_lines='warn', encoding='utf-8')
        # TODO input validation
        self.unit = self.data.UNIT_COORD.unique()[0]  # TODO normaliser l' unite d'entree par point
        self.post_parse()
        return self.data

    def parse_data(self) -> pd.DataFrame:
        '''this method converts the informations of a ssfile into a dataframe for genepy ssfile and other'''
        if self.is_genepy:
            return self.genepy_to_dataframe()
        else:
            return self.ssfile_to_dataframe()

    def rename_title(dataframe) -> pd.DataFrame:
        """this method allows user to rename the column imported if it is not already in valid format (NaN value)"""
        set_title_names = []
        for col in dataframe.columns:
            if pd.isna(dataframe.loc[0, col]):
                while True:
                    user_input = input(
                        f"Enter a value to replace NaN in column {col}: ")
                    if user_input not in set_title_names:
                        set_title_names.append(user_input)
                        break
                    # TODO unable to loop for several columns ?
                    else:
                        print("Value already set !")
                dataframe.loc[0, col] = user_input
        return dataframe

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

    def change_coord_to_relative(self, dataframe: pd.DataFrame) -> pd.DataFrame :
        '''this method changes the coordinates to relative (since it is not in the correct format in the ssfile)'''
        # FIXME to rework
        # if function is x_measure - x_addressing = relative_val is correct
        dataframe.x_ap = dataframe.x_ap - dataframe.x
        dataframe.y_ap = dataframe.y_ap - dataframe.y
        # TODO add relative_coord_x/y columns in dataframe ? replace data ? return columns ?
        return dataframe
