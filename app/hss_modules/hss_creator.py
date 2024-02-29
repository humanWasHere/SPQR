import pandas as pd
import json
import re
from .template_to_all_sections import sectionMaker

# This is main hss_modules' file

# TODO
# faire un checker de nom (EPS_Name) -> match requirements de Hitachi -> informer l'utilisateur au moment où il nomme sa gauge si le format est valide ou non
# implémenter une logique pour le type de parser -> if fichier genepy -> mapping genepy
# faire un checker pour csv ET hss -> intégrer le tool d'alex


class HssCreator:
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
        '''method that opens a JSON file in reading mode which opens in reading mode the JSON file. Returns it if file is clean else raises an error'''
        try:
            with open(template_file, 'r') as f:
                template_file = json.load(f)
        except FileNotFoundError as e:
            raise ValueError(f"JSON file not found: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error loading JSON file {template_file}: {e}")
        return template_file

    def json_to_dataframe(self) -> None:
        '''method that parses a valid JSON file (no redondant data in same section) into a dataframe (writes it in instance - not return)'''
        # initialization of first level/lines
        first_lines_first_level = {}
        # checking whether template's sections is first level (direct values) or second level (dict containing another value level) then making it a dataframe by one way or the other
        for key, value in self.json_template.items():
            if isinstance(value, dict):
                if isinstance(list(value.values())[0], list):
                    self.dict_of_second_level_df[key] = pd.DataFrame(value)
                else:
                    self.dict_of_second_level_df[key] = pd.json_normalize(
                        value)
            else:
                first_lines_first_level[key] = value
        # conversion of the 3 first lines of the template into a one level dataframe (normalize)
        self.first_level_df = pd.json_normalize(first_lines_first_level)

    def get_set_section(self) -> None:
        '''this method gets the logic of sectionMaker which fills the different sections of the recipe'''
        # note that if no logic is implemented in the sectionMaker class, the default template key/value will be directly returned
        for df in self.dict_of_second_level_df:
            if df != "<EPS_Data>":
                # making an instance of sectionMaker which will set all the sections except <EPS_Data> since it has its own class to fill it
                instance_sectionMaker = sectionMaker(
                    self.dict_of_second_level_df)
                self.dict_of_second_level_df["<CoordinateSystem>"] = instance_sectionMaker.make_coordinate_system_section(
                )
                self.dict_of_second_level_df["<GPCoordinateSystem>"] = instance_sectionMaker.make_gp_coordinate_system_section(
                )
                self.dict_of_second_level_df["<Unit>"] = instance_sectionMaker.make_unit_section(
                )
                self.dict_of_second_level_df["<GP_Data>"] = instance_sectionMaker.make_gp_data_section(
                )
                # in the template recipe there is <EPS_Data> in here
                self.dict_of_second_level_df["<GPA_List>"] = instance_sectionMaker.make_gpa_list_section(
                )
                self.dict_of_second_level_df["<GP_Offset>"] = instance_sectionMaker.make_gp_offset_section(
                )
                self.dict_of_second_level_df["<EPA_List>"] = instance_sectionMaker.make_epa_list_section(
                )

    # TODO avoir template['<EPS_Data>'] pour get columns in class eps creator
    # then hssCreator.template['<EPS_Data>'] = EPSCreator.template['<EPS_Data>'] in HssCreator
    # pour l'instant, modify the columns before eps assignation in template header
    def add_MP(self, nb_of_mp_to_add) -> None:
        '''this method adds the number of MP in attribute of the method'''
        # if 1 -> add 1 MP -> so there is 2 MP
        if nb_of_mp_to_add < 1:
            return None
        template_header_df = pd.DataFrame(
            self.dict_of_second_level_df["<EPS_Data>"])
        for mp in range(nb_of_mp_to_add):
            # executing type counting in order to add Type column before all the MPn columns (convention)
            i = 1
            while True:
                if f"Type{i}" in template_header_df.keys():
                    i += 1
                    pass
                else:
                    # TODO or change to empty (?)
                    template_header_df[f"Type{i}"] = ''
                    break
            # count MP number by "MPn_X" key access
            mp_count = 1
            i = 1
            while i:
                if f"MP{i}_X" in template_header_df.keys():
                    mp_count = i
                    i += 1
                else:
                    # TODO écrire en dur avec un mapping ou faire le code suivant ?
                    for col, val in template_header_df.items():
                        if str(col).startswith(f"MP{mp_count}"):
                            new_col_name = str(col).replace(
                                f"MP{mp_count}", f"MP{mp_count + 1}")
                            template_header_df[f"{new_col_name}"] = val
                    break
        # clean columns a bit and rewrite in df dict
        template_header_df = template_header_df.drop(
            template_header_df.index, axis=0)
        self.dict_of_second_level_df["<EPS_Data>"] = template_header_df

    def fill_with_eps_data(self) -> None:
        '''method that **should** drop all columns of the df_template when column title is not in the df_data else column data is added'''
        # check de correspondance -> ajout des donnée finales ou drop des données du template -> création de EPS_Data final (par itération et correspondance en nom de colonne au template)
        # TODO drop les données du template si pas besoin -> permets d'avoir un template exhaustif
        # TODO voir s'il faut pas set NAN ou une value vide ''
        # safety check to add default data if there is no data in self.eps_data (helps for unit tests)
        # FIXME manage empty dataframe as entry
        if self.eps_data.empty:
            self.eps_data = pd.DataFrame(self.dict_of_second_level_df["<EPS_Data>"])
        # actual logic of the method
        template_header = pd.DataFrame(
            self.dict_of_second_level_df["<EPS_Data>"])
        template_header = template_header.drop(template_header.index, axis=0)
        for column_name, value_name in self.eps_data.items():
            if column_name in template_header:
                # adding of eps_data dataframe values to the template dataframe header (stored in RAM)
                template_header[column_name] = value_name
        self.dict_of_second_level_df["<EPS_Data>"] = template_header

    def fill_type_in_eps_data(self, number_of_mp) -> None:
        '''Defines if the Type column needs to be filled by 1s, 2s or empty values'''
        # sanitize value
        if number_of_mp < 1:
            number_of_mp = 1
        # logic for columns before MP columns
        for col in self.dict_of_second_level_df["<EPS_Data>"]:
            if col == "Type1":
                self.dict_of_second_level_df["<EPS_Data>"][col] = 1
            # WARNING maintenabilité : 11 dépends du nommage et de la place de la colonne Type11 dans le template
            elif str(col).startswith("Type") and int(str(col)[4:6]) < 11:
                self.dict_of_second_level_df["<EPS_Data>"][col] = 2
        # defines if writing data is necessary or not - for MP section
        # if data empty in MPn section is empty, corresponding value type is set to "" else fill with 2s
        # WARNING maintenabilité ?
        for mp_nb in range(1, number_of_mp + 1):
            mp_n_is_empty = False
            for col, val in self.dict_of_second_level_df["<EPS_Data>"].items():
                if str(col).startswith(f"MP{mp_nb}"):
                    if pd.isnull(val).all():
                        mp_n_is_empty = True
                    else:
                        mp_n_is_empty = False
            if mp_n_is_empty is True:
                # TODO handle NaN value or other type of empty values
                self.dict_of_second_level_df["<EPS_Data>"][f"Type{mp_nb + 10}"] = ""
            else:
                self.dict_of_second_level_df["<EPS_Data>"][f"Type{mp_nb + 10}"] = 2

    def dataframe_to_hss(self) -> str:
        '''method that converts a dataframe into a HSS format (writes it as a file)'''
        whole_recipe = ""
        # treatment of first level keys
        for titre_premier_niveau in self.first_level_df.columns:
            whole_recipe += f"{titre_premier_niveau}\n"
            # treatment of first level values
            for value_premier_niveau in self.first_level_df[titre_premier_niveau]:
                whole_recipe += f"{value_premier_niveau}\n"
        # treatment of second level keys/values
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
        # TODO ? modifier seulement la section <EPS_Data> / d'un autre côté RCPD attends des "Type" et pas autre chose
        new_string = re.sub(r"Type(\d+)", r"Type", string_to_edit)
        return new_string

    def set_commas_afterwards(self, string_to_modify) -> str:
        '''this method gets the max value number in the output file in order to set the self.num_columns and know the number of commas to write in the file'''
        # cleans the string - removes eventual trailing whitespace
        lines = [line.rstrip() for line in string_to_modify.split('\n')]
        # counts the max number of elements in each rows
        # WARNING maintenabilité : number separated with commas (english notation) may false the calculation here. Maybe use .shape[0] pandas attribute
        self.num_columns = max(line.count(',') + 1 for line in lines)
        # defines and writes the number of commas needed for each lines
        modified_string = ""
        for line in lines:
            num_commas = self.num_columns - (line.count(',') + 1)
            modified_string += line + "," * num_commas + "\n"
        return str(modified_string)

    def write_in_file(self, mp_to_add) -> None:
        '''this method executes the flow of writing the whole recipe'''
        # beware to not modify order
        # get template
        self.json_to_dataframe()
        # create sections except <EPS_Data>
        self.get_set_section()
        # add mp if told to (0 does nothing)
        self.add_MP(mp_to_add)
        # gets data from dataframe_to_eps_data.eps_data_df (EPS_Data filling class)
        self.fill_with_eps_data()
        # fill recipe with <EPS_Data> values
        self.fill_type_in_eps_data(mp_to_add + 1)
        # convert to recipe/hss/csv format (str)
        whole_recipe_template = self.dataframe_to_hss()
        # renaming of "TypeN" into "Type" - doesn't apply on df so we do to recipe output string
        whole_recipe_good_types = self.rename_eps_data_header(
            whole_recipe_template)
        # cleans, calculates and writes the correct number of commas in the output file
        whole_recipe_to_output = self.set_commas_afterwards(
            whole_recipe_good_types)
        with open(self.output_file, 'w') as f:
            f.write(whole_recipe_to_output)
