import logging
import re
import pandas as pd
from pathlib import Path

from .hss_creator import HssCreator
from ..parsers.csv_parser import HSSParser
from ..parsers.json_parser import JSONParser, import_json
from ..data_structure import Block


logger = logging.getLogger(__name__)


class RecipeEditor(HssCreator):
    """this class is meant to modify current instance of a class or imported recipe."""
    # or RecipeModificator(HssCreator.__init__.attributes)
    def __init__(self, json_conf: dict, recipe_name_conf: str, recipe: Path = None):
        # some init
        pseudo_core_data = None
        self.is_csv = False
        self.recipe = None
        constant_sections = None
        table_sections = None
        # parsing condition --> get real col/val and get val for HssCreator mother instance init
        if Path(recipe).suffix == ".csv":
            self.is_csv = True
            self.recipe = Path(recipe)
            # prepare for HssCreator init / parse sections
            csv_recipe_parser_instance = HSSParser(str(self.recipe))
            constant_sections, table_sections = csv_recipe_parser_instance.parse_hss()
            pseudo_core_data = self.get_columns_for_edition(table_sections)
        elif Path(recipe).suffix == ".json":
            self.recipe = Path(recipe)
            # prepare for HssCreator init / parse sections
            json_recipe_parser_instance = JSONParser(str(self.recipe))
            # constant_sections, table_sections = json_recipe_parser_instance.json_to_section_dicts()
            json_recipe_parser_instance.json_to_section_dicts()
            constant_sections, table_sections = json_recipe_parser_instance.constant_sections, json_recipe_parser_instance.table_sections
            pseudo_core_data = self.get_columns_for_edition(table_sections)
        else:
            logging.error("Recipe given for modification is not a valid recipe. Try with a .csv or .json.")
        # initializing HssCreator instance to get parent method (functionnal needs)
        super().__init__(core_data=pseudo_core_data, block=Block(json_conf[recipe_name_conf]['layout']),
                         json_conf=json_conf[recipe_name_conf], polarity='clear', template=None)
        # get template info
        self.json_template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"
        # HssCreator recreates sections --> we get the correct one from parsing
        self.constant_sections = constant_sections
        self.table_sections = table_sections

    def get_columns_for_edition(self, pseudo_table_sections) -> pd.DataFrame:
        """filter needed columns of a core dataframe in order to input it in HssCreator"""
        desired_info_for_edition = pseudo_table_sections['<EPS_Data>'][['EPS_Name', 'Move_X', 'Move_Y', 'AP1_X', 'AP1_Y', 'MP1_TargetCD', 'MP1_TargetCD']]
        desired_info_for_edition.columns = ['name', 'x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']
        desired_info_for_edition.loc[:, ['x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']] = desired_info_for_edition.loc[:, ['x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']].astype(int)
        desired_info_for_edition.loc[:, 'name'] = desired_info_for_edition.loc[:, 'name'].astype(str)
        return desired_info_for_edition

    def check_recipe_validity(self) -> bool:
        """checks wether or not the imported recipe to modificate
        has the columns of the json template
        by dataframe comparison."""
        if self.is_csv:
            # constant sections
            assert all(element in list(import_json(self.json_template).keys()) for element in self.constant_sections.keys()), "imported recipe is not valid (at least at constant_sections level)"
            # table_sections
            assert all(key in list(import_json(self.json_template).keys()) for key in self.table_sections), "imported recipe is not valid (at least at table_sections level)"
            # assert csv_section == template_section, "imported recipe is not valid (in table_sections level)"
            return True
        else:
            # comparing json template at lowest conversion level (if json_to_dataframe is bad -> it doesn't impact here)
            keys_json_template = list(import_json(self.json_template).keys())
            keys_json_recipe = list(import_json(self.recipe).keys())
            if keys_json_template != keys_json_recipe:
                logger.error(f"imported recipe is not valid compared to template\n{keys_json_template}\n{keys_json_recipe}")
                return False
            else:
                return True

    def section_edit(self) -> bool | None:
        """this method should be used to modificate a section."""
        # TODO sanitize type user inputs
        first_modification = True
        while True:
            print("Editing another parameter") if first_modification is False else print("First editing")
            section_list = ", ".join(list(self.table_sections.keys()))
            section_to_modify = input(f"Which section do you want to modify (from the following list)?\n{section_list}\nIf none press Enter\n")
            if section_to_modify != "" and section_to_modify in self.table_sections.keys():
                while True:
                    subsections_list = self.table_sections[section_to_modify].columns.tolist()
                    subsections_list_str = ', '.join(subsections_list)
                    print(f"list : {subsections_list} and len list : {len(subsections_list)}")
                    if len(subsections_list) > 1:
                        subsection_to_modify = input(f"Which subsection do you want to modify (from the following list)?\n{subsections_list_str}\nElse press Enter\n")
                    else:
                        subsection_to_modify = subsections_list_str
                    if subsection_to_modify in self.table_sections[section_to_modify].columns.tolist():
                        while True:
                            value_position = input("Do you want to modify only one specific value ? For single modification insert index row number else press enter for full column modification\n")
                            if value_position != "":
                                if int(value_position) <= len(self.table_sections[section_to_modify]):
                                    modified_value = input("Enter the value you want to set. Else press Enter\n")
                                    self.table_sections[section_to_modify].loc[int(value_position), subsection_to_modify] = modified_value
                                    first_modification = False
                                else:
                                    logging.error(f"given value is out of range ({len(self.table_sections[section_to_modify])}). Try to match with existing index rows")
                            else:
                                modified_value = input("Enter the value you want to set. Else press Enter\n")
                                self.table_sections[section_to_modify][subsection_to_modify] = modified_value
                                first_modification = False
                                break
                        break
                    else:
                        logger.error(f"{subsection_to_modify} apparently not in df")
                        break
            elif section_to_modify == "":
                # covers the case a recipe is not modified
                if first_modification:
                    return False
                else:
                    break
            else:
                logger.error(f"section {section_to_modify} apparently not in any dict")

    def rename_recipe(self) -> Path:
        """renames the recipe in order to be recognized as modified."""
        # searches in folder recipe with similar name and get last digit --> creating recipes that don't overlap previously existing recipes
        base_name = re.sub(r"_(\d+)\.(csv|json)$", "", self.recipe.stem)
        suffix = self.recipe.suffix
        parent_dir = self.recipe.parent
        matching_files = list(parent_dir.glob(f"{base_name}_*.{suffix.lstrip('.')}"))
        if matching_files:
            max_number = 0
            for file in matching_files:
                match = re.search(rf"{base_name}_(\d+)\.{suffix.lstrip('.')}$", file.name)
                if match:
                    number = int(match.group(1))
                    if number > max_number:
                        max_number = number

            new_number = max_number + 1
            new_recipe_name = parent_dir / f"{base_name}_{new_number}{suffix}"
            return new_recipe_name.resolve()
        # if recipe has never been edited, we add the digit logic
        elif str(self.recipe.name).endswith((".json", ".csv")) and self.recipe.suffix in [".json", ".csv"]:
            new_recipe_name = self.recipe.parent / (str(self.recipe.stem) + "_1" + self.recipe.suffix)
            return new_recipe_name.resolve()
        else:
            logger.warning("Recipe name to modify is not formatted as expected")

    def run_recipe_edit(self) -> None:
        """run_recipe_modification is a method that should run the whole recipe modification process."""
        if self.check_recipe_validity():
            if self.section_edit() is False:
                logging.warning("No modification has been made. Exiting recipe creation.")
                return
            recipe_output_file = Path(self.rename_recipe()).resolve()
            self.recipe_output_file = recipe_output_file
            self.output_dataframe_to_csv()
            self.output_dataframe_to_json()
            # recipe_output_file.with_suffix(".csv").write_text(hss_recipe_to_output)
            # if recipe_output_file.with_suffix(".csv").exists():
            #     logger.info(f"csv recipe created ! Find it at {recipe_output_file}")
            # return f"{recipe_output_file}.csv"
        # else:
        #     logger.warning("no recipe has been given")
