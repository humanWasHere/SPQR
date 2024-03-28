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
    def __init__(self, eps_dataframe: pd.DataFrame, layer=0, layout="", topcell="", template=None, output_path=None, recipe_name=None):
        if template is None:
            template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"
        if output_path is None:
            # TODO
            self.recipe_output_path = Path(__file__).resolve().parents[2] / "recipe_output"
        self.recipe_output_name = input("\tfile naming\n\tEnter a name for your recipe (without file extension/words must be separated by underscores) : \n\t") + ".csv"
        self.path_output_file = str(self.recipe_output_path) + "/" + self.recipe_output_name
        self.json_template = self.import_json(template)
        self.num_columns = 0
        self.eps_data = eps_dataframe
        self.layer = layer
        self.layout = layout
        self.topcell = topcell
        self.path_output_file = str(self.recipe_output_path) + "/" + self.recipe_output_name
        # TODO: validation?
        self.constant_sections = {}
        self.table_sections = {}

    def import_json(self, template_file) -> dict:
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
        # checking whether template's sections is first level (direct values) or second level (dict containing another value level) then making it a dataframe by one way or the other
        for key, value in self.json_template.items():
            if isinstance(value, dict):
                if isinstance(list(value.values())[0], list):
                    self.table_sections[key] = pd.DataFrame(value)
                else:
                    self.table_sections[key] = pd.json_normalize(value)
            else:
                self.constant_sections[key] = value

    def get_set_section(self) -> None:
        '''this method gets the logic of sectionMaker which fills the different sections of the recipe'''
        # note that if no logic is implemented in the sectionMaker class, the default template key/value will be directly returned
        # making an instance of sectionMaker which will set all the sections except <EPS_Data> since it has its own class to fill it
        instance_sectionMaker = SectionMaker(self.table_sections)
        self.table_sections["<CoordinateSystem>"] = instance_sectionMaker.make_coordinate_system_section()
        self.table_sections["<GPCoordinateSystem>"] = instance_sectionMaker.make_gp_coordinate_system_section()
        self.table_sections["<Unit>"] = instance_sectionMaker.make_unit_section()
        self.table_sections["<GP_Data>"] = instance_sectionMaker.make_gp_data_section()
        self.table_sections["<GPA_List>"] = instance_sectionMaker.make_gpa_list_section()
        self.table_sections["<GP_Offset>"] = instance_sectionMaker.make_gp_offset_section()
        self.table_sections["<EPA_List>"] = instance_sectionMaker.make_epa_list_section()
        instance_sectionMaker.make_idd_cond_section(self.layout, self.topcell)
        instance_sectionMaker.make_idd_layer_data_section(self.layer)

    def fill_with_eps_data(self) -> None:
        '''method that **should** drop all columns of the df_template when column title is not in the df_data else column data is added'''
        template_header = pd.DataFrame(self.table_sections["<EPS_Data>"])
        template_header = template_header.drop(template_header.index, axis=0)
        for column_name, value_name in self.eps_data.items():
            if column_name in template_header:
                # adding of eps_data dataframe values to the template dataframe header (stored in RAM)
                template_header[column_name] = value_name
        self.table_sections["<EPS_Data>"] = template_header

    def fill_type_in_eps_data(self) -> None:
        '''Defines if the Type column needs to be filled by 1s, 2s or empty values'''
        for col in self.table_sections["<EPS_Data>"]:
            if col == "Type1":
                self.table_sections["<EPS_Data>"][col] = 1
            # WARNING maintenabilité : 11 dépends du nommage et de la place de la colonne Type11 dans le template
            elif str(col).startswith("Type") and int(str(col)[4:6]) < 12:
                self.table_sections["<EPS_Data>"][col] = 2
        # if data empty in MPn section is empty, corresponding value type is set to "" else fill with 2s
        # WARNING maintenabilité ?
        # for mp_nb in range(1, 5):
        #     mp_n_is_empty = False
        #     for col, val in self.table_sections["<EPS_Data>"].items():
        #         if str(col).startswith(f"MP{mp_nb}"):
        #             if pd.isnull(val).all():
        #                 mp_n_is_empty = True
        #             else:
        #                 mp_n_is_empty = False
        #     # FIXME override -> based on last column only
        #     if mp_n_is_empty:
        #         # TODO handle NaN value or other type of empty values
        #         self.table_sections["<EPS_Data>"][f"Type{mp_nb + 10}"] = ""
        #     else:
        #         self.table_sections["<EPS_Data>"][f"Type{mp_nb + 10}"] = 2

    def dataframe_to_hss(self) -> str:
        '''method that converts a dataframe into a HSS format (writes it as a file)'''
        whole_recipe = ""
        # treatment of first level keys
        for section, value in self.constant_sections.items():
            whole_recipe += f"{section}\n"
            whole_recipe += f"{value}\n"
        # treatment of second level keys/values
        for section, dataframe in self.table_sections.items():
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

    def output_dataframe_to_json(self):
        '''method that writes a json of the recipe in a template to output and reuse (in opposition of json_to_dataframe method'''
        json_content = self.constant_sections
        for section_keys, section_series in self.table_sections.items():
            if not section_series.empty:
                section_dict = section_series.to_dict(orient='records')[0]
                json_content[section_keys] = section_dict
            else:
                raise ValueError("Series is empty")
        json_str = json.dumps(json_content, indent=4)
        json_str = re.sub(r'NaN', r'""', json_str)
        output_path = Path(__file__).resolve().parents[2] / "recipe_output" / "recipe.json"
        with open(output_path, 'w') as json_file:
            json_file.write(json_str)
        if output_path:  # TODO better check + log
            print('\tjson recipe created !')

    def write_in_file(self) -> None:
        '''this method executes the flow of writing the whole recipe'''
        # beware to not modify order
        self.json_to_dataframe()
        print('4. other sections creation')
        self.get_set_section()
        if not self.table_sections["<CoordinateSystem>"].empty:  # TODO better check + log
            print('\tother sections created')
        self.fill_with_eps_data()
        self.fill_type_in_eps_data()
        whole_recipe_template = self.dataframe_to_hss()
        whole_recipe_good_types = self.rename_eps_data_header(whole_recipe_template)
        whole_recipe_to_output = self.set_commas_afterwards(whole_recipe_good_types)
        self.output_dataframe_to_json()
        with open(self.path_output_file, 'w') as f:
            f.write(whole_recipe_to_output)
        if self.path_output_file:  # TODO better check + log
            print('\tcsv recipe created !')
