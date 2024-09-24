import logging
import re
# import pandas as pd
from pathlib import Path

from .hss_creator import HssCreator
from ..parsers.csv_parser import HSSParser
from ..parsers.json_parser import JSONParser, import_json
from ..data_structure import Block

# TODO check if HssCreator instance is needed to modify the recipe
# -> get file recipe that already has been output
# uses json_parser.py -> import HssCreator heritage in RecipeModificator or in JsonParser

logger = logging.getLogger(__name__)


class RecipeModificator(HssCreator):
    """this class is meant to modify current instance of a class or imported recipe."""
    # TODO should it take a class instance in entry as RecipeModificator(instance)
    # TODO faire une condition qui overlap le nom de recette donné ou garder la fonction qui s'en charge et changer les modèles pydantic
    # or RecipeModificator(HssCreator.__init__.attributes)
    def __init__(self, json_conf: dict, recipe_name: str, recipe: Path = None):
        core_data = None
        self.is_csv = False
        self.recipe = None
        self.constant_sections = None
        self.table_sections = None
        self.json_conf = json_conf
        if Path(recipe).suffix == ".csv":
            self.is_csv = True
            self.recipe = Path(recipe)
            csv_recipe_parser_instance = HSSParser(str(self.recipe))
            self.constant_sections, self.table_sections = csv_recipe_parser_instance.parse_hss()
            core_data = self.get_columns_for_edition()
            print(f"post core data init : {self.table_sections['<EPS_Data>']}")
        elif Path(recipe).suffix == ".json":
            self.recipe = Path(recipe)
            json_recipe_parser_instance = JSONParser(self.recipe)
            self.constant_sections, self.table_sections = json_recipe_parser_instance.json_to_section_dicts()
            core_data = self.get_columns_for_edition()
        else:
            logging.error("Recipe given for modification is not a valid recipe. Try with a .csv or .json.")
        self.json_template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"
        # super().__init__  -> after for eps
        super().__init__(core_data=core_data, block=Block(self.json_conf[recipe_name]['layout']),
                         json_conf=self.json_conf[recipe_name], polarity='clear', template=None)
        print(f"post init : {self.table_sections['<EPS_Data>']}")

    def get_columns_for_edition(self):
        # core_data = hss_parser_instance.parse_data()
        desired_info_for_edition = self.table_sections['<EPS_Data>'][['EPS_Name', 'Move_X', 'Move_Y', 'AP1_X', 'AP1_Y', 'MP1_TargetCD', 'MP1_TargetCD']]
        desired_info_for_edition.columns = ['name', 'x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']
        desired_info_for_edition.loc[:, ['x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']] = desired_info_for_edition.loc[:, ['x', 'y', 'x_ap', 'y_ap', 'x_dim', 'y_dim']].astype(int)
        desired_info_for_edition.loc[:, 'name'] = desired_info_for_edition.loc[:, 'name'].astype(str)
        return desired_info_for_edition

    # def check_json_recipe_validity(self) -> bool:
    #     """checks wether or not the imported recipe to modificate
    #     has the columns of the json template
    #     by json comparison."""
    #     # comparing json template at lowest conversion level (if json_to_dataframe is bad -> it doesn't impact here)
    #     keys_json_template = list(import_json(self.json_template).keys())
    #     keys_json_recipe = list(import_json(self.json_recipe).keys())
    #     if keys_json_template != keys_json_recipe:
    #         logger.error(f"imported recipe is not valid compared to template\n{keys_json_template}\n{keys_json_recipe}")
    #         return False
    #     else:
    #         return True

    # def check_hss_recipe_validity(self) -> bool:
    #     """checks wether or not the imported recipe to modificate
    #     has the columns of the json template
    #     by dataframe comparison."""
    #     # constant sections
    #     assert all(element in list(import_json(self.json_template).keys()) for element in self.constant_sections.keys()), "imported recipe is not valid (at least at constant_sections level)"
    #     # table_sections
    #     assert all(key in list(import_json(self.json_template).keys()) for key in self.table_sections), "imported recipe is not valid (at least at table_sections level)"
    #     # TODO assert all values are present in each (no modulo)
    #     # assert csv_section == template_section, "imported recipe is not valid (in table_sections level)"
    #     return True

    def check_recipe_validity(self) -> bool:
        """checks wether or not the imported recipe to modificate
        has the columns of the json template
        by dataframe comparison."""
        if self.is_csv:
            # constant sections
            assert all(element in list(import_json(self.json_template).keys()) for element in self.constant_sections.keys()), "imported recipe is not valid (at least at constant_sections level)"
            # table_sections
            assert all(key in list(import_json(self.json_template).keys()) for key in self.table_sections), "imported recipe is not valid (at least at table_sections level)"
            # TODO assert all values are present in each (no modulo)
            # assert csv_section == template_section, "imported recipe is not valid (in table_sections level)"
            return True
        else:
            # comparing json template at lowest conversion level (if json_to_dataframe is bad -> it doesn't impact here)
            keys_json_template = list(import_json(self.json_template).keys())
            keys_json_recipe = list(import_json(self.json_recipe).keys())
            if keys_json_template != keys_json_recipe:
                logger.error(f"imported recipe is not valid compared to template\n{keys_json_template}\n{keys_json_recipe}")
                return False
            else:
                return True

    def section_modification(self):
        """this method should be used to modificate a section."""
        # TODO check si l'utilisateur a fait une modification. Si il n'en a pas fait, break RecipeModification (pas de modification effectuée) --> cas utilisateur : enter dès le début de la modification
        # TODO faire de la documentation répertoriant toutes les sections (pour que ça soit explicite pour l'utilisateur)
        # TODO sanitize type user inputs
        first_modification = True
        while True:
            print("Editing another parameter") if first_modification is False else print("First editing")
            section_to_modify = input("Which section do you want to modify (from the following list)?\n<CoordinateSystem>, <GPCoordinateSystem>, <Unit>, <GP_Data>, <EPS_Data>, <GPA_List>, <GP_Offset>, <EPA_List>, <IDD_Cond>, <IDD_Layer_Data>, <ImageEnv>, <Recipe>, <MeasEnv_Exec>, <MeasEnv_MeasRes>\nIf none press Enter\n")
            if section_to_modify != "" and section_to_modify in self.table_sections.keys():
                while True:
                    # print(self.json_conf[section_to_modify].columns)
                    subsections_list = self.table_sections[section_to_modify].columns.tolist()
                    subsections_list = ', '.join(subsections_list)
                    subsection_to_modify = input(f"Which subsection do you want to modify (from the following list)?\n{subsections_list}\nElse press Enter\n")
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
            elif section_to_modify == "":
                break
            else:
                logger.error(f"section {section_to_modify} apparently not in any dict")

    def rename_recipe(self) -> Path:
        """renames the recipe in order to be recognized as modified."""
        # /!\ modify name without extension since HssCreator.will name the recipe -> insert it as a parameter of HssCreator
        is_previously_modified = re.search(r"_(\d+)\.(csv|json)$", self.recipe.name)
        if is_previously_modified:
            current_number = int(is_previously_modified.group(1))
            incremented_number = current_number + 1
            new_recipe_name = Path(re.sub(r"_(\d+)\.(csv|json)$", f"_{incremented_number}.\\2", self.recipe.name)).resolve()
            return new_recipe_name
        elif str(self.recipe.name).endswith((".json", ".csv")):
            # new_recipe_name = str(self.recipe.stem) + "_1" + self.recipe.suffix
            new_recipe_name = self.recipe.parent / (str(self.recipe.stem) + "_1" + self.recipe.suffix)
            return new_recipe_name.resolve()
        else:
            logger.warning("recipe name is not formatted as expected")

    def run_recipe_modification(self) -> None:
        """run_recipe_modification is a method that should run the whole recipe modification process.
        Not implemented yet."""
        # if self.is_csv is False:
        # if self.check_json_recipe_validity():
        # self.section_modification()
        # hss_recipe = super().dataframe_to_hss()
        # hss_recipe_good_types = super().rename_eps_data_header(hss_recipe)
        # hss_recipe_to_output = super().set_commas_afterwards(hss_recipe_good_types)
        # recipe_output_file = Path(self.rename_recipe())
        # recipe_output_file.with_suffix(".json").write_text(hss_recipe_to_output)
        # if super().recipe_output_file.with_suffix(".json").exists():
        #     logger.info(f"JSON recipe created! Find it at {super().recipe_output_file}.json")
        # return f"{super().recipe_output_file}.json"
        if self.is_csv is True:
            # if self.check_hss_recipe_validity() is True:
            if self.check_recipe_validity() is True:
                print(f"post check hss recipe validity : {self.table_sections['<EPS_Data>']}")
                self.section_modification()
                hss_recipe = super().dataframe_to_hss()
                hss_recipe_good_types = super().rename_eps_data_header(hss_recipe)
                hss_recipe_to_output = super().set_commas_afterwards(hss_recipe_good_types)
                super().output_dataframe_to_json()
                recipe_output_file = Path(self.rename_recipe()).resolve()
                recipe_output_file.with_suffix(".csv").write_text(hss_recipe_to_output)
                if recipe_output_file.with_suffix(".csv").exists():
                    logger.info(f"csv recipe created ! Find it at {recipe_output_file}")
                # return f"{recipe_output_file}.csv"
        # else:
        #     logger.warning("no recipe has been given")
