import json
import logging
from pathlib import Path
import re

import pandas as pd

from ..data_structure import Block
from .eps_data import EPSData
from .section_maker import SectionMaker
from ..parsers.json_parser import JSONParser

# TODO
# export QCG 5k vs 6k
# faire un checker de nom (EPS_Name) -> match requirements de Hitachi -> validator
# -> informer l'utilisateur au moment où il nomme sa gauge si le format est valide ou non
# faire un checker pour csv ET hss -> intégrer le tool d'alex -> recipe checker

logger = logging.getLogger(__name__)


class HssCreator:
    """this class is meant to create the final version of the recipe (through section making)."""
    def __init__(self, core_data: pd.DataFrame, block: Block, json_conf: dict,
                 polarity: str = 'clear', template=None):
        self.layout = block.layout_path
        self.topcell = block.topcell
        self.precision = block.precision
        self.polarity = polarity
        self.main_layer = int(json_conf['layers'][0].split('.')[0])
        self.step = json_conf['step']
        if json_conf['output_dir'] == "":
            self.recipe_output_dir = Path(__file__).resolve().parents[2] / "recipe_output"
        else:
            self.recipe_output_dir = Path(json_conf['output_dir'])
        self.recipe_output_file: str
        if json_conf['recipe_name'] == "":
            self.recipe_output_file = self.recipe_output_dir / "recipe"
        else:
            self.recipe_output_file = self.recipe_output_dir / str(json_conf['recipe_name'])
        assert re.match(r'^[a-zA-Z0-9_-]{0,37}$', str(json_conf['recipe_name'])), "String does not meet the requirements"

        if template is None:
            self.json_template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"
        sections = JSONParser(self.json_template).json_to_section_dicts()
        self.constant_sections: dict[str, str] = sections.constant_sections
        self.table_sections: dict[str, pd.DataFrame] = sections.table_sections
        templates = {key: json_conf[key] for key in ['ap1_template', 'ep_template', 'eps_template', 'mp_template']}
        eps_data = EPSData(core_data, json_conf['step'], json_conf['magnification'],
                           json_conf['ap1_mag'], templates, sections.table_sections['<EPS_Data>'],
                           field_tone=polarity)
        self.eps_data = eps_data.get_eps_data()
        self.section_maker: SectionMaker

    def fill_with_eps_data(self) -> None:
        """Use template header and fill it with columns from the external EPSData dataframe."""
        # external_epsdata_columns.issubset(template_epsdata_columns)
        template_eps_data_header = pd.DataFrame(columns=self.table_sections['<EPS_Data>'].columns)
        for column_name, column_values in self.eps_data.items():
            if column_name in template_eps_data_header:
                # adding of eps_data dataframe values to the template dataframe header
                template_eps_data_header[column_name] = column_values
            else:
                raise ValueError(f"{column_name} is not in the template's EPS_Data header")
        self.table_sections["<EPS_Data>"] = template_eps_data_header

    def get_set_section(self) -> None:
        """Fills the different sections of the recipe except <EPS_Data> using SectionMaker."""
        # note that if no logic is implemented in the SectionMaker class,
        # the default template key/value will be used
        self.section_maker = SectionMaker(self.table_sections)
        sections = self.table_sections  # shorter
        # Implemented logic
        self.section_maker.make_gp_data_section()  # content validation
        self.section_maker.make_idd_cond_section(self.layout, self.topcell)  # design info
        self.section_maker.make_idd_layer_data_section(self.main_layer, self.polarity)  # layer mapping
        self.section_maker.make_recipe_section(self.step)  # set SEM condition

        # Placeholders
        sections['<CoordinateSystem>'] = self.section_maker.make_coordinate_system_section()
        sections['<GPCoordinateSystem>'] = self.section_maker.make_gp_coordinate_system_section()
        sections['<Unit>'] = self.section_maker.make_unit_section()
        sections['<GPA_List>'] = self.section_maker.make_gpa_list_section()
        sections['<GP_Offset>'] = self.section_maker.make_gp_offset_section()
        sections['<EPA_List>'] = self.section_maker.make_epa_list_section()
        sections['<ImageEnv>'] = self.section_maker.make_image_env_section()
        sections['<MeasEnv_Exec>'] = self.section_maker.make_measenv_exec_section()
        sections['<MeasEnv_MeasRes>'] = self.section_maker.make_measenv_measres_section()

    def dataframe_to_hss(self) -> str:
        """Converts internal dictionaries into a HSS format as raw text.
        Output CSV-like sections do not have a fixed number of separators."""
        whole_recipe = ""
        # whole_recipe = "#HSS IDP Spreadsheet\n\n"
        # Write single-value sections
        for section, value in self.constant_sections.items():
            whole_recipe += f"{section}\n"
            whole_recipe += f"{value}\n"
        # Write table-like sections
        for section, dataframe in self.table_sections.items():
            # TODO : implement this
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

    @staticmethod
    def rename_eps_data_header(string_to_edit: str) -> str:
        """Convert all 'TypeN' with N a number in 'Type'"""
        new_string = re.sub(r"Type(\d+)", r"Type", string_to_edit)
        return new_string

    @staticmethod
    def set_commas_afterwards(string_to_modify: str) -> str:
        """Get the max number of columns and write the same number of commas in the file """
        lines = [line.rstrip() for line in string_to_modify.splitlines()]
        # WARNING maintenabilité : number separated with commas -> manage sep
        num_columns = max(line.count(',') + 1 for line in lines)
        modified_string = ""
        for line in lines:
            num_commas = num_columns - (line.count(',') + 1)
            modified_string += line + "," * num_commas + "\n"
        return str(modified_string)

    def output_dataframe_to_json(self) -> None:
        """method that writes a json of the recipe in a template to output and reuse."""
        json_content = self.constant_sections
        for section_keys, section_series in self.table_sections.items():
            if not section_series.empty:
                # section_dict = section_series.to_dict(orient='records')[0]
                # json_content[section_keys] = section_dict
                json_content[section_keys] = {col: section_series[col].tolist() for col in section_series}
            else:
                logger.error(f"{section_keys} has its series empty")
        json_str = json.dumps(json_content, indent=4)
        json_str = re.sub(r'NaN', r'""', json_str)
        # json_output_file = self.recipe_output_file.with_suffix('').with_suffix('.json')
        self.recipe_output_file = self.recipe_output_file.with_suffix('').with_suffix('.json')
        self.recipe_output_file.write_text(json_str)
        if self.recipe_output_file.exists() and self.recipe_output_file.suffix == ".json":
            logger.info(f"json recipe created !  Find it at {self.recipe_output_file.resolve()}")

    def output_dataframe_to_csv(self) -> None:
        whole_recipe_template = self.dataframe_to_hss()
        whole_recipe_good_types = self.rename_eps_data_header(whole_recipe_template)
        whole_recipe_to_output = self.set_commas_afterwards(whole_recipe_good_types)
        self.recipe_output_file = self.recipe_output_file.with_suffix('').with_suffix('.csv')
        self.recipe_output_file.write_text(whole_recipe_to_output)
        if self.recipe_output_file.exists() and self.recipe_output_file.suffix == ".csv":
            logger.info(f"csv recipe created ! Find it at {Path(self.recipe_output_file).resolve()}")

    def write_in_file(self) -> str:
        """this method executes the flow of writing the whole recipe."""
        self.fill_with_eps_data()
        logger.info('4. Other sections creation')
        self.get_set_section()
        logger.info('Other sections created')
        self.output_dataframe_to_csv()
        self.output_dataframe_to_json()
        # if self.recipe_output_file.with_suffix(".csv").exists() and self.recipe_output_file.with_suffix(".json").exists():
        #     logger.info("VENI VEDI VICI")
        return f"{self.recipe_output_file}.csv"
