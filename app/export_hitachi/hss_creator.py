import re
import json
import pandas as pd
from pathlib import Path
from ..data_structure import Block
from .section_maker import SectionMaker

# TODO
# faire un checker de nom (EPS_Name) -> match requirements de Hitachi -> validator
# -> informer l'utilisateur au moment où il nomme sa gauge si le format est valide ou non
# faire un checker pour csv ET hss -> intégrer le tool d'alex -> recipe checker


class HssCreator:
    def __init__(self, eps_dataframe: pd.DataFrame, layers: int, block: Block, template=None, output_dir=None, recipe_name="recipe"):
        if template is None:
            template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"
        if output_dir is None:
            output_dir = Path(__file__).resolve().parents[2] / "recipe_output"  # TODO
        self.recipe_output_dir = Path(output_dir)
        self.recipe_output_file = self.recipe_output_dir / recipe_name  # to create here?
        self.eps_data_df = eps_dataframe
        self.layout = block.layout_path
        self.topcell = block.topcell
        self.precision = int(float(block.precision))
        self.layers = layers
        self.json_template = self.import_json(template)
        # TODO: validation?
        self.constant_sections = {}
        self.table_sections = {}

    def import_json(self, template_file) -> dict:
        """Parse JSON file and handle exceptions"""
        try:
            with open(template_file, 'r') as f:
                template_file = json.load(f)
        except FileNotFoundError as e:
            print(f"JSON file not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error loading JSON file {template_file}: {e}")
        return template_file

    def json_to_dataframe(self) -> None:
        """Parse a valid HSS JSON template into two dictionaries of unique sections:
        - a dict of strings for unique values -> {'section_name': "value"},
        - a dict of dataframes for table content -> {'section_name': pd.DataFrame}."""
        for section_name, content in self.json_template.items():
            if isinstance(content, dict):
                if isinstance(list(content.values())[0], list):
                    self.table_sections[section_name] = pd.DataFrame(content)
                else:
                    self.table_sections[section_name] = pd.json_normalize(content)
            else:
                self.constant_sections[section_name] = content

    def get_set_section(self) -> None:
        '''this method gets the logic of sectionMaker which fills the different sections of the recipe except <EPS_Data>'''
        # note that if no logic is implemented in the sectionMaker class, the default template key/value will be directly returned
        instance_sectionMaker = SectionMaker(self.table_sections)
        self.table_sections["<CoordinateSystem>"] = instance_sectionMaker.make_coordinate_system_section()
        self.table_sections["<GPCoordinateSystem>"] = instance_sectionMaker.make_gp_coordinate_system_section()
        self.table_sections["<Unit>"] = instance_sectionMaker.make_unit_section()
        self.table_sections["<GP_Data>"] = instance_sectionMaker.make_gp_data_section()
        self.table_sections["<GPA_List>"] = instance_sectionMaker.make_gpa_list_section()
        self.table_sections["<GP_Offset>"] = instance_sectionMaker.make_gp_offset_section()
        self.table_sections["<EPA_List>"] = instance_sectionMaker.make_epa_list_section()
        self.table_sections["<IDD_Cond>"] = instance_sectionMaker.make_idd_cond_section(self.layout, self.topcell)
        self.table_sections["<IDD_Layer_Data>"] = instance_sectionMaker.make_idd_layer_data_section(self.layers)
        self.table_sections["<ImageEnv>"] = instance_sectionMaker.make_image_env_section()

    def fill_with_eps_data(self) -> None:
        '''method that **should** drop all columns of the df_template when column title is not in the df_data else column data is added'''
        template_header_eps_data = pd.DataFrame(self.table_sections["<EPS_Data>"])
        template_header_eps_data = template_header_eps_data.drop(template_header_eps_data.index, axis=0)
        for column_name, value_name in self.eps_data_df.items():
            if column_name in template_header_eps_data:
                # adding of eps_data dataframe values to the template dataframe header (stored in RAM)
                template_header_eps_data[column_name] = value_name
            else:
                raise ValueError(f"{column_name} is not in the template's dataframe header")
        self.table_sections["<EPS_Data>"] = template_header_eps_data

    def fill_type_in_eps_data(self) -> None:
        '''Defines if the Type column needs to be filled by 1s, 2s or empty values'''
        for col in self.table_sections["<EPS_Data>"]:
            if col == "Type1":
                self.table_sections["<EPS_Data>"][col] = 1
            # WARNING maintenabilité : 11 dépends du nommage et de la place de la colonne Type11 dans le template
            elif str(col).startswith("Type") and int(str(col)[4:6]) < 12:
                self.table_sections["<EPS_Data>"][col] = 2
        # TODO add_mp
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
        #         self.table_sections["<EPS_Data>"][f"Type{mp_nb + 10}"] = np.nan
        #     else:
        #         self.table_sections["<EPS_Data>"][f"Type{mp_nb + 10}"] = 2

    def convert_coord_to_nm(self):
        # FIXME should keep data as float ??? -> change test to float checking (not int)
        self.table_sections["<EPS_Data>"]["Move_X"] = (self.table_sections["<EPS_Data>"]["Move_X"] * 1000 / self.precision).astype('int64')
        self.table_sections["<EPS_Data>"]["Move_Y"] = (self.table_sections["<EPS_Data>"]["Move_Y"] * 1000 / self.precision).astype('int64')

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
        new_string = re.sub(r"Type(\d+)", r"Type", string_to_edit)
        return new_string

    def set_commas_afterwards(self, string_to_modify) -> str:
        '''this method gets the max value number in the output file in order to set the num_columns and know the number of commas to write in the file'''
        lines = [line.rstrip() for line in string_to_modify.split('\n')]
        # WARNING maintenabilité : number separated with commas (english notation) may false the calculation here. Maybe use .shape[0] pandas attribute
        num_columns = max(line.count(',') + 1 for line in lines)
        modified_string = ""
        for line in lines:
            num_commas = num_columns - (line.count(',') + 1)
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
                # TODO raise an error ?
                print(f"\t{section_keys} has its series empty")
        json_str = json.dumps(json_content, indent=4)
        json_str = re.sub(r'NaN', r'""', json_str)
        with open(str(self.recipe_output_file) + ".json", 'w') as json_file:
            json_file.write(json_str)
        if json_file:  # TODO better check + log
            print(f"\tjson recipe created !  Find it at {str(self.recipe_output_file)}.json")

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
        # self.convert_coord_to_nm()
        whole_recipe_template = self.dataframe_to_hss()
        whole_recipe_good_types = self.rename_eps_data_header(whole_recipe_template)
        whole_recipe_to_output = self.set_commas_afterwards(whole_recipe_good_types)
        self.output_dataframe_to_json()
        with open(self.recipe_output_file.with_suffix(".csv"), 'w') as f:
            f.write(whole_recipe_to_output)
        if Path(f).exists():  # TODO better check + log
            print(f"\tcsv recipe created ! Find it at {self.recipe_output_file}.csv")
