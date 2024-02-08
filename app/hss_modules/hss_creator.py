import pandas as pd
import numpy as np
import json
import re

# logique à implémenter dans le main à termes -> laisser les class et méthodes en appel dans ce fichier

# rappel du flow :
# - création de recette SEM : template JSON -> création de dataframe depuis template -> insérer le df mergé dans le df template -> formater output csv/hss
# - modification de recette SEM :
#   - instance en cours : (i)loc dans le dataframe (de la recette en cours)
#   - reprise d'une instance (valide/aka compatible parsing logiciel) : lecture du csv -> passer en dataframe pour manipulation -> formater output csv/hss
# est ce que HssModification est une classe fille ou une méthode de HssCreator ? -> pb par la récupération de l'instance en cours -> non
# csv to JSON ? -> modifictaion de recette / sauvegarde. Deux flows possibles : 1) avec le JSON on reprends le flow de création de recette 2) sinon faire un pandas.read_csv()

# TODO
# reporter les valeurs par défaut du sem_chef au template JSON ?
# dans le JSON . pour les milliers et , pour les décimales -> dans le code : faire l'inverse
# pour le fichier d'output, créer le fichier si il n'existe pas -> faire une fonction ou à l'initialisation
# remove trailing comma eps_data
# par rapport aux requirements de recette, voir pour ajouter ou supprimer des colonnes de EPS_Data par exemple (format firewall ou permis)


header = ''


class DataFrameToEPSData:
    DEFAULTS = {
        'Mode': 1,
        'EPS_Template': "EPS_Default",
        'AP2_Template': "OPC_AP2_Off",
        'AP1_Mag': 45000,
        'AP1_AF_Mag': 45000,
        'AP1_Rot': 0,
        'MP1_X': 0,
        'MP1_Y': 0
    }
    MAPPING_Genepy = {
        'EPS_Name': "Gauge name",
        'Move_X': "X_coord_Pat",
        'Move_Y': "Y_coord_Pat"
    }
    MAP = {
        'Move_X': "x",
        'Move_Y': "y",
        'EPS_Name': "name",
        'AP1_X': "x_ap_rel",
        'AP1_Y': "y_ap_rel",
        'AP1_AF_X': "x_ap_rel",
        'AP1_AF_Y': "y_ap_rel",
        'EP_Mag_X': "mag",
        'EP_AF_X': "x_af_rel",
        'EP_AF_Y': "y_af_rel",
        'EP_AF_Mag': "mag",
        'MP1_Name': "name",
        'MP1_TargetCD': "target_cd",
        'MP1_Direction': "orient"
    }

    def __init__(self, gauges: pd.DataFrame, step: str = "PH"):
        # TODO:  validate data (columns, dtype, nan...)
        self.gauges = gauges  # .astype({'x': int, 'y': int})
        self.eps_data = pd.DataFrame(columns=header)
        assert step in {"PH", "ET"}
        self.step = step

        self.init_columns()
        self.map_columns()
        self.autofill_columns()

    def set_rotation(self):
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90

        rot = np.where(self.eps_data['MP1_Direction'] == "X", 0, 90)
        # elif Y
        return rot

    def test(self):
        TEST_MAPPING = {
            'Mode': 1,
            'EPS_Template': "EPS_Default",
            'AP2_Template': "OPC_AP2_Off",
            'AP1_Mag': 45000,
            'AP1_AF_Mag': 45000,
            'AP1_Rot': 0,
            'MP1_X': 0,
            'MP1_Y': 0,
            'Move_X': self.gauges["x"],
            'Move_Y': self.gauges["y"],
            'EP_Template': dict(PH="banger_EP_F16", ET="banger_EP_F32")[self.step],
            'EP_Rot': self.set_rotation()
        }

    def init_columns(self):
        """Generate unique IDs and fill columns with default values"""
        self.eps_data['#EPS_ID'] = range(1, self.gauges.shape[0] + 1)
        self.eps_data['MP1_PNo'] = self.eps_data['#EPS_ID']
        for csv_col, value in self.DEFAULTS.items():
            self.eps_data[csv_col] = value

    def map_columns(self):
        """Map gauge dataframe columns with corresponding recipe columns without further processing"""
        for csv_col, gauge_col in self.MAP.items():
            self.eps_data[csv_col] = self.gauges[gauge_col]

    def autofill_columns(self):
        """Fill more columns using logic"""
        self.eps_data['EP_Template'] = dict(
            PH="banger_EP_F16", ET="banger_EP_F32")[self.step]

        # Set rotation
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "X", 'EP_Rot'] = 0
        self.eps_data.loc[self.eps_data['MP1_Direction'] == "Y", 'EP_Rot'] = 90
        # Compute measure point width/length (from SEM procedure)
        # TODO: MP_Cursor_Size_X/Y etc. for Ellipse. cf doc HSS p. 67
        search_area = self.eps_data.MP1_TargetCD * \
            self.eps_data.EP_Mag_X * 512 / 1000 / 135000 / 3
        # cursor_size = self.eps_data.MP1_TargetCD * self.eps_data.EP_Mag_X * 512 / 1000 / 135000
        # Limit search area to 30 pixels / todo: handle NaN
        self.eps_data['MP1_SA_In'] = self.eps_data['MP1_SA_Out'] = search_area.fillna(
            500).astype(int).clip(upper=30)
        self.eps_data['MP1_MeaLeng'] = self.measleng  # TODO: compute
        # Fill Type columns. First one is 1, all others are 2 (?)
        # list of column indices  #TODO 65 for 1 MP, 66 for 2 MP...
        type_cols = [i for i, label in enumerate(
            EPS_COLUMNS[:65]) if label == "Type"]
        self.eps_data.iloc[:, type_cols] = 2
        self.eps_data.iloc[:, 1] = 1


class HssCreator:
    def __init__(self, template=None, output_file=None, eps_dataframe=None):  # TODO add eps_dataframe: pd.DataFrame
        # "imports"
        if template is None:
            template = "/work/opc/all/users/chanelir/semrc/app/hss_modules/template_SEM_recipe.json"
        if output_file is None:
            output_file = "/work/opc/all/users/chanelir/semrc/app/hss_modules/recette.hss"
        if eps_dataframe is None:
            eps_dataframe = "/work/opc/all/users/chanelir/semrc/app/merged_df.temp"
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

    def json_to_dataframe(self):
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

    def modify_eps_data(self):
        # import may be temp
        self.json_to_dataframe()
        # get EPS_Data from template
        eps_data_template = pd.DataFrame(self.dict_of_second_level_df["<EPS_Data>"])
        print(eps_data_template)
        self.eps_data

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
        self.num_columns = max(line.count(',') + 1 for line in lines)
        # defines and writes the number of commas needed for each lines
        modified_string = ""
        for line in lines:
            num_commas = self.num_columns - (line.count(',') + 1)
            modified_string += line + "," * num_commas + "\n"
        return str(modified_string)

    def write_in_file(self):
        # template import
        self.json_to_dataframe()
        # make the template
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


class HssModification(HssCreator):
    # header = [label + str(i) if label == "Type" else label for i, label in enumerate(EPS_COLUMNS)]  # uniquify Type cols
    # then -> df.to_json() -> pandas.to_json() -> pour récupération de sauvegardes et modifications

    # access data on 2 lever dict -> city = data["person2"]["address"]["city"]
    # ex
    # "person2": {
    #   "address": {
    #        "city": "Othertown",
    # print(city)  # Output: "Othertown"

    # format data : data.format(format_arguments)

    # df.at[2, 'age'] = 30
    def __init__(self):
        pass


runCSVCreator = HssCreator()
runCSVCreator.modify_eps_data()
