import pandas as pd
from pathlib import Path
import json
import re
from .template_to_all_sections import SectionMaker

# TODO
# faire un checker de nom (EPS_Name) -> match requirements de Hitachi -> informer l'utilisateur au moment où il nomme sa gauge si le format est valide ou non
# implémenter une logique pour le type de parser -> if fichier genepy -> mapping genepy
# faire un checker pour csv ET hss -> intégrer le tool d'alex


class HssCreator:
    def __init__(self, eps_dataframe: pd.DataFrame, template=None, output_file=None):
        if template is None:
            template = Path(__file__).resolve(
            ).parents[2] / "assets" / "template_SEM_recipe.json"
        if output_file is None:
            # TODO this is temp, I don't want a recipe_output folder in my project
            # TODO ask user how he wants to name his recipe
            output_file = Path(__file__).resolve().parents[2] / "recipe_output" / "recipe.csv"
        self.json_template = self.import_json(template)
        self.num_columns = 0
        self.output_file = output_file
        self.eps_data = eps_dataframe
        self.first_level_df = pd.DataFrame()
        self.dict_of_second_level_df = {}

    # @abstractmethod
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

    # @abstractmethod
    def json_to_dataframe(self) -> None:
        '''method that parses a valid JSON file (no redondant data in same section) into a dataframe (writes it in instance - not return)'''
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
                instance_sectionMaker = SectionMaker(self.dict_of_second_level_df, "OM")
                self.dict_of_second_level_df["<CoordinateSystem>"] = instance_sectionMaker.make_coordinate_system_section()
                self.dict_of_second_level_df["<GPCoordinateSystem>"] = instance_sectionMaker.make_gp_coordinate_system_section()
                self.dict_of_second_level_df["<Unit>"] = instance_sectionMaker.make_unit_section()
                self.dict_of_second_level_df["<GP_Data>"] = instance_sectionMaker.make_gp_data_section()
                # in the template recipe there is <EPS_Data> in here
                self.dict_of_second_level_df["<GPA_List>"] = instance_sectionMaker.make_gpa_list_section()
                self.dict_of_second_level_df["<GP_Offset>"] = instance_sectionMaker.make_gp_offset_section()
                self.dict_of_second_level_df["<EPA_List>"] = instance_sectionMaker.make_epa_list_section()

    def add_MP(self, nb_of_mp_to_add) -> None:
        '''this method adds the number of MP in attribute of the method'''
        # if nb_of_mp_to_add = 1 -> add 1 MP -> so there is 2 MP
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
                    # TODO garder le code suivant ou faire un mapper ?
                    for col, val in template_header_df.items():
                        if str(col).startswith(f"MP{mp_count}"):
                            new_col_name = str(col).replace(
                                f"MP{mp_count}", f"MP{mp_count + 1}")
                            template_header_df[f"{new_col_name}"] = val
                    break
        template_header_df = template_header_df.drop(
            template_header_df.index, axis=0)
        self.dict_of_second_level_df["<EPS_Data>"] = template_header_df

    def fill_with_eps_data(self) -> None:
        '''method that **should** drop all columns of the df_template when column title is not in the df_data else column data is added'''
        # TODO drop les données du template si pas besoin -> permets d'avoir un template exhaustif
        # TODO voir s'il faut pas set NAN ou une value vide ''
        # if self.eps_data.empty:
        #     # self.eps_data = pd.DataFrame(self.dict_of_second_level_df["<EPS_Data>"])  # FIXME manage empty dataframe as entry
        #     raise ValueError("You must enter measure points ! Dataframe is empty...")
        template_header = pd.DataFrame(
            self.dict_of_second_level_df["<EPS_Data>"])
        template_header = template_header.drop(template_header.index, axis=0)
        for column_name, value_name in self.eps_data.items():
            if column_name in template_header:
                # adding of eps_data dataframe values to the template dataframe header (stored in RAM)
                template_header[column_name] = value_name
        self.dict_of_second_level_df["<EPS_Data>"] = template_header

    def fill_type_in_eps_data(self, number_of_existing_mp) -> None:
        '''Defines if the Type column needs to be filled by 1s, 2s or empty values'''
        if number_of_existing_mp < 1:
            number_of_existing_mp = 1
        for col in self.dict_of_second_level_df["<EPS_Data>"]:
            if col == "Type1":
                self.dict_of_second_level_df["<EPS_Data>"][col] = 1
            # WARNING maintenabilité : 11 dépends du nommage et de la place de la colonne Type11 dans le template
            elif str(col).startswith("Type") and int(str(col)[4:6]) < 11:
                self.dict_of_second_level_df["<EPS_Data>"][col] = 2
        # if data empty in MPn section is empty, corresponding value type is set to "" else fill with 2s
        # WARNING maintenabilité ?
        for mp_nb in range(1, number_of_existing_mp + 1):
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
        lines = [line.rstrip() for line in string_to_modify.split('\n')]
        # WARNING maintenabilité : number separated with commas (english notation) may false the calculation here. Maybe use .shape[0] pandas attribute
        self.num_columns = max(line.count(',') + 1 for line in lines)
        modified_string = ""
        for line in lines:
            num_commas = self.num_columns - (line.count(',') + 1)
            modified_string += line + "," * num_commas + "\n"
        return str(modified_string)

    # def output_dataframe_to_json(self):
    #     '''method that writes a json of the recipe in a template to output and reuse (in opposition of json_to_dataframe method'''
    #     # TODO rework / invert import json
    #     first_lines = self.first_level_df.to_json(orient='records', lines=True)
    #     json_content = first_lines
    #     for section_keys, section_df in self.dict_of_second_level_df.items():
    #         json_content += pd.DataFrame(section_df).to_json('temp.json', orient='records', lines=True)
    #     print(json_content)

        # Write the combined JSON content to a file
        # output_path = Path(__file__).resolve().parents[2] / "recipe_output" / "recipe.json"
        # with open(output_path, 'w') as json_file:
        #     json_file.write(json_content)

    def write_in_file(self, mp_to_add) -> None:
        '''this method executes the flow of writing the whole recipe'''
        # beware to not modify order
        self.json_to_dataframe()
        self.get_set_section()
        self.add_MP(mp_to_add)
        self.fill_with_eps_data()
        self.fill_type_in_eps_data(mp_to_add + 1)
        # output json here
        # self.output_dataframe_to_json()
        # __________
        whole_recipe_template = self.dataframe_to_hss()
        whole_recipe_good_types = self.rename_eps_data_header(
            whole_recipe_template)
        whole_recipe_to_output = self.set_commas_afterwards(
            whole_recipe_good_types)
        with open(self.output_file, 'w') as f:
            f.write(whole_recipe_to_output)
