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
    def __init__(self, eps_dataframe: pd.DataFrame, layers: int, block: Block,
                 template=None, output_dir=None, recipe_name="recipe"):
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
        self.constant_sections: dict[str, pd.DataFrame] = {}
        self.table_sections: dict[str, pd.DataFrame] = {}

    def import_json(self, template_file) -> dict:
        """Parse JSON file. Do not handle exceptions yet"""
        return json.loads(template_file.read_text())

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
        """Fills the different sections of the recipe except <EPS_Data> using SectionMaker"""
        # note that if no logic is implemented in the SectionMaker class,
        # the default template key/value will be used
        section_maker = SectionMaker(self.table_sections)
        sections = self.table_sections  # shorter
        # Implemented logic
        section_maker.make_gp_data_section()  # content validation
        section_maker.make_idd_cond_section(self.layout, self.topcell)  # design info
        section_maker.make_idd_layer_data_section(self.layers)  # layer mapping
        # Placeholders
        sections['<CoordinateSystem>'] = section_maker.make_coordinate_system_section()
        sections['<GPCoordinateSystem>'] = section_maker.make_gp_coordinate_system_section()
        sections['<Unit>'] = section_maker.make_unit_section()
        sections['<GPA_List>'] = section_maker.make_gpa_list_section()
        sections['<GP_Offset>'] = section_maker.make_gp_offset_section()
        sections['<EPA_List>'] = section_maker.make_epa_list_section()
        sections['<ImageEnv>'] = section_maker.make_image_env_section()

    def fill_with_eps_data(self) -> None:
        """Use template header and fill it with columns from the external EPSData dataframe"""
        # external_epsdata_columns.issubset(template_epsdata_columns)
        template_eps_data_header = pd.DataFrame(columns=self.table_sections["<EPS_Data>"].columns)
        for column_name, column_values in self.eps_data_df.items():
            if column_name in template_eps_data_header:
                # adding of eps_data dataframe values to the template dataframe header
                template_eps_data_header[column_name] = column_values
            else:
                raise ValueError(f"{column_name} is not in the template's EPS_Data header")
        self.table_sections["<EPS_Data>"] = template_eps_data_header

    def fill_type_in_eps_data(self) -> None:
        '''Defines if the Type column needs to be filled by 1s, 2s or empty values'''
        for col in self.table_sections["<EPS_Data>"]:
            if col == "Type1":
                self.table_sections["<EPS_Data>"][col] = 1
            # FIXME maintenabilité : 11 dépends du nommage et de la place de la colonne Type11 dans le template  # noqa E501
            elif str(col).startswith("Type") and int(str(col)[4:6]) < 12:
                self.table_sections["<EPS_Data>"][col] = 2

    # def convert_coord_to_nm(self):
    #     # FIXME should keep data as float ??? -> change test to float checking (not int)
    #     # FIXME not here
    #     self.table_sections["<EPS_Data>"]["Move_X"] = (
    #         self.table_sections["<EPS_Data>"]["Move_X"] * 1000 / self.precision).astype('int64')
    #     self.table_sections["<EPS_Data>"]["Move_Y"] = (
    #         self.table_sections["<EPS_Data>"]["Move_Y"] * 1000 / self.precision).astype('int64')

    def dataframe_to_hss(self) -> str:
        """Converts internal dictionaries into a HSS format as raw text.
        Output CSV-like sections do not have a fixed number of separators"""
        whole_recipe = ""
        # Write single-value sections
        for section, value in self.constant_sections.items():
            whole_recipe += f"{section}\n"
            whole_recipe += f"{value}\n"
        # Write table-like sections
        for section, dataframe in self.table_sections.items():
            # whole_recipe += f"""{section}
            #                     #{','.join(dataframe.columns)}
            #                     {dataframe.to_csv(index=False, header=False)}
            # """

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

    def rename_eps_data_header(self, string_to_edit: str) -> str:
        """Convert all 'TypeN' with N a number in 'Type'"""
        new_string = re.sub(r"Type(\d+)", r"Type", string_to_edit)
        return new_string

    def set_commas_afterwards(self, string_to_modify: str) -> str:
        """Get the max number of columns and write the same number of commas in the file """
        lines = [line.rstrip() for line in string_to_modify.splitlines()]
        # WARNING maintenabilité : number separated with commas -> manage sep
        num_columns = max(line.count(',') + 1 for line in lines)
        modified_string = ""
        for line in lines:
            num_commas = num_columns - (line.count(',') + 1)
            modified_string += line + "," * num_commas + "\n"
        return str(modified_string)

    def output_dataframe_to_json(self):
        '''method that writes a json of the recipe in a template to output and reuse'''
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
        self.recipe_output_file.with_suffix(".json").write_text(json_str)
        if self.recipe_output_file.with_suffix(".json").exists():  # TODO better check + log
            print(f"\tjson recipe created !  Find it at {str(self.recipe_output_file)}.json")

    def write_in_file(self) -> None:
        '''this method executes the flow of writing the whole recipe'''
        # beware to not modify order
        self.json_to_dataframe()
        print('4. other sections creation')
        self.get_set_section()
        print('\tother sections created')
        self.fill_with_eps_data()
        self.fill_type_in_eps_data()
        # self.convert_coord_to_nm()
        whole_recipe_template = self.dataframe_to_hss()
        whole_recipe_good_types = self.rename_eps_data_header(whole_recipe_template)
        whole_recipe_to_output = self.set_commas_afterwards(whole_recipe_good_types)
        self.output_dataframe_to_json()
        self.recipe_output_file.with_suffix(".csv").write_text(whole_recipe_to_output)
        if self.recipe_output_file.with_suffix(".csv").exists():  # TODO better check + log
            print(f"\tcsv recipe created ! Find it at {self.recipe_output_file}.csv")
