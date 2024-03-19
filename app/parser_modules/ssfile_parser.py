import pandas as pd

# TODO
# input and print should be at user's destination -> in GUI
# traitement des NaN value
# est ce que genepy set ses unités pour la colonnes/ligne entière à chaque fois ?
# checker de présence des colonnes 'name', 'coord x' et 'coord y' ?
# interaction with user should be better -> GUI


class SsfileParser:
    '''this class is used to parse ssfiles which can be genepy ssfile or other (formatted to convention ?) ssfiles'''
    def __init__(self, file_to_parse, is_genepy=False):
        self.ssfile = file_to_parse
        self.is_genepy = is_genepy

    def ssfile_to_dataframe(self) -> pd.DataFrame:  # Union[pd.DataFrame, str] with from typing import Union
        '''this method converts the informations of a ssfile into a dataframe for genepy ssfile and other'''
        if self.is_genepy:
            # if not 7 columns for genepy file : file not genepy or pb with genepy file. warning returned anyways (on_bad_lines)
            df = pd.read_csv(self.ssfile, sep='\t', header=0,
                             on_bad_lines='warn', encoding='utf-8')
            df = self.drop_empty_column(df)
            return pd.DataFrame(df)
        else:
            with open(self.ssfile, 'r') as f:
                # counts the number of columns (separated by tabs) in the first line of the file (header / line with column names)
                header_column_number = len(f.readline().strip().split('\t'))
                max_column_number = max(len(line.split('\t')) for line in f)
            df = pd.read_csv(self.ssfile, sep='\t', names=range(
                max_column_number), on_bad_lines='warn', encoding='utf-8')
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

    def rename_title(dataframe) -> pd.DataFrame:
        '''this method allows user to rename the column imported if it is not already in valid format (NaN value)'''
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

    def drop_empty_column(self, dataframe) -> pd.DataFrame:
        '''this method checks all columns for empty values (NaN values in whole column). If empty, drops it (means bad dataframe interpretation - while parsing ssfile ?)'''
        for col in dataframe.columns:
            if dataframe[col].isnull().all():
                dataframe.drop(columns=[col], inplace=True)
        return dataframe

    def change_coord_to_relative(self, dataframe) -> any:
        '''this method changes the coordinates to relative (since it is not in the correct format in the ssfile)'''
        # FIXME should we call this function only if ssfile is genepy dataframe ?
        # if dataframe["UNIT_COORD"] == "DBU": -> indent
        # dataframe["X_coord_Pat"]
        # if function is x_measure - x_addressing = relative_val is correct
        relative_coord_x = dataframe["X_coord_Pat"] - dataframe["X_coord_Addr"]
        relative_coord_y = dataframe["Y_coord_Pat"] - dataframe["Y_coord_Addr"]
        # TODO add relative_coord_x/y columns in dataframe ? replace data ? del columns ?
        return relative_coord_x, relative_coord_y
