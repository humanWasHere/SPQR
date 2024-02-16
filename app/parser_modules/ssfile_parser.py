import pandas as pd

# assuming that the first line of the ssfile represents
# user must separate the columns with tabs

# assuming there is 7 columns in a genepy ssfile output

# TODO detect encoding -> helps with parsing ?
# import chardet
# with open(file_path, 'rb') as f:
#     result = chardet.detect(f.read())
# encoding = result['encoding']
# TODO
# check encoding of the ssfile to better treatment
# détecter combien de colonne à le header -> si différent du max retourner une erreur
# ask user to change the NaN title or ask user to set the column names
# est ce que les colonnes du fichier ssfile_romain ne sont pas des paires de valeur pour une colonne ?
# est ce qu'on fill les NaN values avec des 0 ? -> génant pour RCPD ? Post treatment for us in recipe creation ? -> for me
# -> if NaN value: pass
# est ce que genepy set ses unités pour la ligne entière à chaque fois ?
# checker de présence des colonnes 'name', 'coord x' et 'coord y' ?


class ssfileParser:

    def __init__(self, file_to_parse, is_genepy=False):
        self.ssfile = file_to_parse
        self.in_genepy = is_genepy

    def rename_title(dataframe):
        # TODO
        '''explain what this fonction does here'''
        set_title_names = []  # store column name temp
        for col in dataframe.columns:  # for each dataframe's columns
            # if value is NaN for column title
            if pd.isna(dataframe.loc[0, col]):
                while True:  # we loop for security user_input -> if user enters a column title unused, we break the loop else we ask again
                    user_input = input(
                        f"Enter a value to replace NaN in column {col}: ")
                    if user_input not in set_title_names:
                        set_title_names.append(user_input)
                        break
                    else:
                        print("Value already set !")
                # we modify the value of the columns for user entries
                dataframe.loc[0, col] = user_input
        return dataframe

    def drop_empty_column(dataframe):
        '''explain what this fonction does here'''
        # check for all columns if whole column has empty values (NaN values). If so, drops itv (means bad dataframe interpretation)
        for col in dataframe.columns:
            if dataframe[col].isnull().all():
                dataframe.drop(columns=[col], inplace=True)
        return dataframe

    def ssfile_to_dataframe(self):
        '''explain what this fonction does here'''
        # first check : is ssfile from genepy ?
        if self.in_genepy:  # à check autrement -> data in ssfile or external -> True/False is genepy file
            # if not 7 columns for genepy file : not genepy or pb with genepy. warning returned anyways (on_bad_lines)
            df = pd.read_csv(self.ssfile, sep='\t', header=0,
                             on_bad_lines='warn', encoding='utf-8')
            df = ssfileParser.drop_empty_column(df)  # dataframe cleaning
            return pd.DataFrame(df)
        else:
            with open(self.ssfile, 'r') as f:
                # counts the number of columns (separated by tabs) in the first line of the file (header / line with column names)
                header_column_number = len(f.readline().strip().split('\t'))
                # WARNING : first line of the ssfile should be column name - WARNING 2 : words must be space separated
                # -> tabulations makes a new column
                # number of max column detected with
                max_column_number = max(len(line.split('\t')) for line in f)
                # longest line of the file (by iteration)
                # warning : we can't do it by dataframe -> error tokenizing data
            df = pd.read_csv(self.ssfile, sep='\t', names=range(
                max_column_number), on_bad_lines='warn', encoding='utf-8')
            # Lire le fichier CSV avec les noms de colonnes spécifiés et la gestion des lignes incorrectes
            # if NaN values in first line of the file (assumed title line)
            if df.iloc[0].isnull().values.any():
                print("There is undefined columns name in your dataframe. Have a look :")
                print(df.to_string())
                # rename NaN columns and do some cleaning
                df = ssfileParser.drop_empty_column(
                    ssfileParser.rename_title(df))
            if header_column_number != max_column_number:  # random check
                print(
                    "Reminder that the dataframe does not match expectations :( make it better !")
                print("Le nombre de colonne dans le header est {} et le nombre de colonne max est {}."
                      .format(header_column_number, max_column_number))  # if this line displays the same number it's a win !
            print(df.to_string())
            # FIXME return if parser is other than genepy
            # return df

    def change_coord_to_relative(self, dataframe):
        # if dataframe["UNIT_COORD"] == "DBU": -> indent
        # dataframe["X_coord_Pat"]
        # if function is x_measure - x_addressing = relative_val is correct
        relative_coord_x = dataframe["X_coord_Pat"] - dataframe["X_coord_Addr"]
        relative_coord_y = dataframe["Y_coord_Pat"] - dataframe["Y_coord_Addr"]
        # TODO add relative_coord_x/y columns in dataframe ?
        return relative_coord_x, relative_coord_y


# genepy_ssfile = "/work/opc/all/users/chanelir/semrc-assets/ssfile-genepy/out/ssfile_proto.txt"  # genepy files
# parser_instance = ssfileParser(genepy_ssfile, is_genepy=True)
# ssfile_genepy_df = parser_instance.ssfile_to_dataframe()
# parser_instance.change_coord_to_relative(ssfile_genepy_df)
