import pandas as pd
# import numpy as np
import json
import re

# TODO
# faire un checker de nom (EPS_Name) -> match requirements de Hitachi -> informer l'utilisateur au moment où il nomme sa gauge si le format est valide ou non
# reporter les valeurs par défaut du sem_chef au template JSON ?
# pour le fichier d'output, créer le fichier si il n'existe pas -> faire une fonction ou à l'initialisation
# remove trailing comma eps_data if pb
# par rapport aux requirements de recette, voir pour ajouter ou supprimer des colonnes de EPS_Data par exemple (format firewall ou permis)
# nettoyer les appels de fonction pour qu'ils soient fait au bon endroit et si possible de manière unique
# implémenter une logique pour le type de parser -> if fichier genepy -> mapping genepy
# nommage des df etc à faire
# autofill pour recette fonctionnelle et exhaustive -> concertation des points à apporter -> faire en fonction de la doc et de l'xp de Romain
# dans le mapping -> faire correspondre les "TypeN" au template pour le merge des infos de eps_data au noms de colonne du template
# faire un checker pour csv ET hss -> intégrer le tool d'alex / voir si l'ordre des colonnes importe vraiment


class DataFrameToEPSData:
    # DEFAULTS = {
    #     'Mode': 1,
    #     'EPS_Template': "EPS_Default",
    #     'AP2_Template': "OPC_AP2_Off",
    #     'AP1_Mag': 45000,
    #     'AP1_AF_Mag': 45000,
    #     'AP1_Rot': 0,
    #     'MP1_X': 0,
    #     'MP1_Y': 0
    # }
    # MAP = {
    #     'Move_X': "x",
    #     'Move_Y': "y",
    #     'EPS_Name': "name",
    #     'AP1_X': "x_ap_rel",
    #     'AP1_Y': "y_ap_rel",
    #     'AP1_AF_X': "x_ap_rel",
    #     'AP1_AF_Y': "y_ap_rel",
    #     'EP_Mag_X': "mag",
    #     'EP_AF_X': "x_af_rel",
    #     'EP_AF_Y': "y_af_rel",
    #     'EP_AF_Mag': "mag",
    #     'MP1_Name': "name",
    #     'MP1_TargetCD': "target_cd",
    #     'MP1_Direction': "orient"
    # }
    MAPPING_Genepy = {
        'EPS_Name': "Gauge name",
        'Move_X': "X_coord_Pat",
        'Move_Y': "Y_coord_Pat",
        "MP_TargetCD": " min_dimension(nm)"
    }
    # correspondance entre min template (à ne pas toucher) et valeurs réalistes
    # inspired from banger-283UA-ZACT-PH-SRAM-FEM hss
    test_MAPPING_EPS_Data_from_template = {
        "Mode": 1,
        "AP1_X": -1000,
        "AP1_Y": 0,
        'AP1_Mag': 45000,
        'AP1_AF_Mag': 45000,
        'AP1_Rot': 0,
        "AP1_AF_X": -300000000,
        "AP1_AF_Y": -300000000,
        "AP1_AST_X": -300000000,
        "AP1_AST_Y": -300000000,
        "AP1_AST_Mag": 0,
        "AP2_X": -300000000,
        "AP2_Y": -300000000,
        "AP2_Mag": 1000,
        "AP2_Rot": 90,
        "AP2_AF_X": -300000000,
        "AP2_AF_Y": -300000000,
        "AP2_AF_Mag": 0,
        "AP2_AST_X": -300000000,
        "AP2_AST_Y": -300000000,
        "AP2_AST_Mag": 0,
        "EP_Mag_Scan_X": 1000,
        "EP_Mag_Scan_Y": 1000,
        "EP_Rot": "0,0",
        "EP_AF_X": -10000,
        "EP_AF_Y": -10000,
        "EP_AF_Mag": 0,
        "EP_AST_X": -10000,
        "EP_AST_Y": -10000,
        "EP_AST_Mag": 0,
        "EP_ABCC_X": -10000,
        "EP_ABCC_Y": -10000,
        "MP_X": -300000000,
        "MP_Y": -300000000,
        "MP_Template": "chaine",
        "MP_PNo": 1,
        "MP_DNo1": 0,
        "MP_DNo2": 0,
        "MP_Name": "chaine",
        "MP_TargetCD": -200000,
        "MP_PosOffset": -200000,
        "MP_SA_In": 0,
        "MP_Cursor_Size_X": 0,
        "MP_SA_Out": 0,
        "MP_Cursor_Size_Y": 0,
        "MP_MeaLeng": 1,
        "MP_Direction": 1
    }

    def __init__(self, gauges: pd.DataFrame, step: str = "PH"):
        # TODO:  validate data (columns, dtype, nan...)
        self.gauges = gauges  # .astype({'x': int, 'y': int})
        self.eps_data = pd.DataFrame()
        assert step in {"PH", "ET"}
        self.step = step

        self.global_eps_data_filling()
        # self.map_columns()
        # self.autofill_columns()

    # def set_rotation(self):
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90

    #     rot = np.where(self.eps_data['MP1_Direction'] == "X", 0, 90)
    #     # elif Y
    #     return rot

    # def test(self):
    #     TEST_MAPPING = {
    #         'Mode': 1,
    #         'EPS_Template': "EPS_Default",
    #         'AP2_Template': "OPC_AP2_Off",
    #         'AP1_Mag': 45000,
    #         'AP1_AF_Mag': 45000,
    #         'AP1_Rot': 0,
    #         'MP1_X': 0,
    #         'MP1_Y': 0,
    #         'Move_X': self.gauges["x"],
    #         'Move_Y': self.gauges["y"],
    #         'EP_Template': dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step],
    #         'EP_Rot': self.set_rotation()
    #     }

    def global_eps_data_filling(self):
        """Generate unique IDs and fill columns with default values"""
        # TODO placer ici (?) une logique sélectionnant le type de recette. Ici, depuis un ssfile genepy
        # applying mapping and so merged_df values to eps_data_df
        for csv_col, value in self.MAPPING_Genepy.items():
            self.eps_data[csv_col] = self.gauges[value]

        # applying test mapping to eps_data_df
        for csv_col, value in self.test_MAPPING_EPS_Data_from_template.items():
            self.eps_data[csv_col] = value

        # __________EPS_ID section__________
        self.eps_data['EPS_ID'] = range(1, min(self.gauges.shape[0] + 1, 9999))
        # preventing data to be out of range -> match doc
        if any(id > 9999 for id in self.eps_data['EPS_ID']):
            raise ValueError("EPS_ID values cannot exceed 9999")

        # __________Type section__________
        # self.eps_data['Type1'] = 1  # meaning absolute
        for col in self.eps_data.columns:
            if col == "Type1":
                self.eps_data[col] = 1
            # warning maintenabilité
            elif col.startswith("Type"):
                self.eps_data[col] = 2

        # __________Mode section__________
        # should be 1 normal or 2 differential

        # self.eps_data['MP1_PNo'] = self.eps_data['#EPS_ID']
        # for csv_col, value in self.DEFAULTS.items():
        #     self.eps_data[csv_col] = value

    # def map_columns(self):
    #     """Map gauge dataframe columns with corresponding recipe columns without further processing"""
    #     for csv_col, gauge_col in self.MAP.items():
    #         self.eps_data[csv_col] = self.gauges[gauge_col]

    # # TODO intégrer l'autofill à la création du df eps_data
    # def autofill_columns(self):
    #     """Fill more columns using logic"""
    #     self.eps_data['EP_Template'] = dict(
    #         PH="banger_EP_F16", ET="banger_EP_F32")[self.step]

    #     # Set rotation
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
    #     self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90
    #     # Compute measure point width/length (from SEM procedure)
    #     # TODO: MP_Cursor_Size_X/Y etc. for Ellipse. cf doc HSS p. 67
    #     search_area = self.eps_data.MP1_TargetCD * \
    #         self.eps_data.EP_Mag_X * 512 / 1000 / 135000 / 3
    #     # cursor_size = self.eps_data.MP1_TargetCD * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
    #     # Limit search area to 30 pixels / todo: handle NaN
    #     self.eps_data['MP1_SA_In'] = self.eps_data['MP1_SA_Out'] = search_area.fillna(
    #         500).astype(int).clip(upper=30)
    #     self.eps_data['MP1_MeaLeng'] = self.measleng  # TODO: compute
    #     # Fill Type columns. First one is 1, all others are 2 (?)
    #     # list of column indices  #TODO 65 for 1 MP, 66 for 2 MP...
    #     # type_cols = [i for i, label in enumerate(
    #     #     EPS_COLUMNS[:65]) if label == "Type"]
    #     # self.eps_data.iloc[:, type_cols] = 2
    #     self.eps_data.iloc[:, 1] = 1

    def get_eps_data(self):
        '''callable method (destination HssCreator) which returns the EPS_Data dataframe containing the values'''
        return self.eps_data


class adaptativeRecipeFilling:
    def __init__(self) -> None:
        pass

    def set_type(self, section_name) -> None:
        if section_name == "<EPS_Data>":
            for col in self.eps_data.columns:
                if col == "Type1":
                    self.eps_data[col] = 1
                # warning maintenabilité
                elif col.startswith("Type"):
                    self.eps_data[col] = 2
        elif section_name == "something else to implement":
            # TODO implement other stuff
            print("implement it")

    def set_id(self, dataframe, key_name=None) -> None:
        if dataframe == "<EPS_Data>":
            self.eps_data['EPS_ID'] = range(
                1, min(self.gauges.shape[0] + 1, 9999))
            # preventing data to be out of range -> match doc
            if any(id > 9999 for id in self.eps_data['EPS_ID']):
                raise ValueError("EPS_ID values cannot exceed 9999")
        # else:
        #     HssCreator. ['EPS_ID'] = range(1, min(self.gauges.shape[0] + 1, 9999))
        #     # preventing data to be out of range -> match doc
        #     if any(id > 9999 for id in self.eps_data['EPS_ID']):
        #         raise ValueError("EPS_ID values cannot exceed 9999")


class HssCreator:
    # TODO add eps_dataframe: pd.DataFrame
    def __init__(self, eps_dataframe: pd.DataFrame, template=None, output_file=None):
        # "imports"
        if template is None:
            template = "/work/opc/all/users/chanelir/semrc/assets/template_SEM_recipe.json"
        if output_file is None:
            output_file = "/work/opc/all/users/chanelir/semrc-outputs/recette.hss"
        self.json_template = self.import_json(template)
        # initialization
        self.num_columns = 0
        self.output_file = output_file
        self.eps_data = eps_dataframe
        self.first_level_df = pd.DataFrame()
        # dict which contains all the second level sections of the second level JSON template
        self.dict_of_second_level_df = {}

    def import_json(self, template_file) -> any:
        '''fonction that opens a JSON file in reading mode qui ouvre en lecture un fichier JSON et le retourne si il est clean sinon une erreur est relevée'''
        try:
            with open(template_file, 'r') as f:
                template_file = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON file: {e}")
        return template_file

    def json_to_dataframe(self) -> None:
        '''method that parses a valid JSON file (no redondant data in same section) into a dataframe (writes it in instance - not return)'''
        # initialization of first
        first_lines_first_level = {}
        # checking which treatment the template's sections will have
        for key, value in self.json_template.items():
            if isinstance(value, dict):
                if isinstance(list(value.values())[0], list):
                    self.dict_of_second_level_df[key] = pd.DataFrame(value)
                else:
                    self.dict_of_second_level_df[key] = pd.json_normalize(
                        value)
            else:
                first_lines_first_level[key] = value
        # here we assume there is only one value per section with one name of section per row
        # conversion of the 3 first lines of the template into a one level dataframe (normalize)
        self.first_level_df = pd.json_normalize(first_lines_first_level)

    def drop_unused_columns(self) -> pd.DataFrame:
        '''method that **should** drop all columns of the df_template that the title is not in the df_data ONLY IF the columns title is already matching'''
        # import may be temp
        self.json_to_dataframe()
        # get EPS_Data section from template
        # check de correspondance -> ajout des donnée finales ou drop des données du template -> création de EPS_Data final
        # itération dans les noms de colonnes du template pour ajouter les colonnes manquantes à EPS_Data
        # for column_name in pd.DataFrame(self.dict_of_second_level_df["<EPS_Data>"]):
        #     if column_name not in self.eps_data.columns:
        #         # ajout de la colonne au dataframe eps_data (par comparaison au template)
        #         self.eps_data[column_name] = ''  # TODO voir s'il faut pas set NAN ou une value vide ''
        template_header = pd.DataFrame(
            self.dict_of_second_level_df["<EPS_Data>"])
        template_header = template_header.drop(template_header.index, axis=0)
        for column_name, value_name in self.eps_data.items():
            if column_name in template_header:
                # ajout des valeurs du dataframe eps_data aux header du dataframe de template
                template_header[column_name] = value_name
        self.dict_of_second_level_df["<EPS_Data>"] = template_header

    def dataframe_to_hss(self) -> str:
        '''method that converts a dataframe into a HSS format (writes it as a file)'''
        whole_recipe = ""
        # we assume there is only one fixed value
        # treatment of first level keys
        for titre_premier_niveau in self.first_level_df.columns:
            whole_recipe += f"{titre_premier_niveau}\n"
            # treatment of first level values
            for value_premier_niveau in self.first_level_df[titre_premier_niveau]:
                whole_recipe += f"{value_premier_niveau}\n"
        # treatment of keys (first level (section) and second level (dataframe.columns)) and second level values (dataframe.to_csv)
        for section, dataframe in self.dict_of_second_level_df.items():
            # writing of first level keys (in dataframe)
            whole_recipe += f"{section}\n"
            header_str = ','.join(dataframe.columns)
            # writing of second level keys
            whole_recipe += f"#{header_str}\n"
            csv_str = dataframe.to_csv(index=False, header=False)
            # writing of second level values
            for line in csv_str.splitlines():
                whole_recipe += f"{line}\n"
        # removes the last backspace '\n' added by iteration at the data's end
        whole_recipe = whole_recipe.rstrip('\n')
        return whole_recipe

    def rename_eps_data_header(self, string_to_edit) -> str:
        '''method that converts all "TypeN" with N a number in "Type"'''
        # TODO modifier seulement la section <EPS_Data> / d'un autre côté RCPD attends des "Type" et pas autre chose
        new_string = re.sub(r"Type(\d+)", r"Type", string_to_edit)
        return new_string

    def set_commas_afterwards(self, string_to_modify) -> str:
        '''this method gets the max value number in the output file in order to set the self.num_columns and know the number of commas to write in the file'''
        # cleans the string - removes trailing eventual whitespace
        lines = [line.rstrip() for line in string_to_modify.split('\n')]
        # counts the max number of elements in each rows
        # warning : number separated with commas (english notation) may false the calculation here. Maybe use .shape[0] pandas attribute
        self.num_columns = max(line.count(',') + 1 for line in lines)
        # defines and writes the number of commas needed for each lines
        modified_string = ""
        for line in lines:
            num_commas = self.num_columns - (line.count(',') + 1)
            modified_string += line + "," * num_commas + "\n"
        return str(modified_string)

    def write_in_file(self) -> None:
        # gets data from otherClass.eps_data_df
        self.drop_unused_columns()
        whole_recipe_template = self.dataframe_to_hss()
        # whole_recipe_EPS_Data
        # renaming of "TypeN" into "Type"
        whole_recipe_good_types = self.rename_eps_data_header(
            whole_recipe_template)
        # cleans, calculates and writes the correct number of commas in the output file
        whole_recipe_to_output = self.set_commas_afterwards(
            whole_recipe_good_types)
        with open(self.output_file, 'w') as f:
            f.write(whole_recipe_to_output)
