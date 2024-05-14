import re
from pathlib import Path

from .hss_creator import HssCreator
from ..parsers.csv_parser import HSSParser

# selon l'intégration dans le flow, voir si cette class est nécessaire

# TODO check if HssCreator instance is needed to modify the recipe
# -> get file recipe that already has been output
# uses json_parser.py -> import HssCreator heritage in RecipeModificator or in JsonParser


class RecipeModificator(HssCreator):
    '''this class is meant to modify current instance of a class or imported recipe'''
    # TODO should it take a class instance in entry as RecipeModificator(instance)
    # or RecipeModificator(HssCreator.__init__.attributes)
    def __init__(self, json_recipe: Path = None, csv_recipe: Path = None):
        # self.recipe_to_modify = dict
        # self.recipe_name = Path
        if (json_recipe is not None):
            self.imported_json_recipe = Path(json_recipe)
            self.recipe_name: Path = self.imported_json_recipe.name
            # FIXME
            self.recipe_to_modify_json = super().import_json(self.imported_json_recipe)
            # TODO return 2 dict (dict / pd.DataFrame)
            self.recipe_to_modify: dict = super().json_to_dataframe(self.recipe_to_modify_json)
        elif (csv_recipe is not None):
            self.imported_csv_recipe = Path(csv_recipe)
            self.recipe_name: Path = self.imported_csv_recipe.name
            super().constant_sections, super().table_sections = HSSParser.parse_data()
            # self.recipe_to_modify: dict = HSSParser.import_hss(self.imported_csv_recipe)
        elif (json_recipe is None and csv_recipe is None):
            raise ImportError("no recipe was given")

    def check_json_recipe_validity(self) -> bool:
        '''checks wether or not the imported recipe to modificate
        has the columns of the json template'''
        # /!\ self.recipe_to_modify should be --expected_format--
        if self.recipe_to_modify.columns == super().json_to_dataframe(self.json_template).columns:
            return True
        else:
            print("imported recipe is not valid")
            return False

    def section_modification(self):
        section_to_modify = input("print the exact name of the section you want to modify")
        value_to_modify = input("give the new value of the element you want to modify")
        place_value_to_modify = input("give the place of the new value of the element you want to modify (int)")

        if section_to_modify in super().constant_sections:
            if place_value_to_modify != "":
                super().constant_sections[section_to_modify].iloc[place_value_to_modify] = value_to_modify
            else:
                super().constant_sections[section_to_modify] = value_to_modify
        elif section_to_modify in super().table_sections:
            if place_value_to_modify != "":
                super().constant_sections[section_to_modify].iloc[place_value_to_modify] = value_to_modify
            else:
                super().table_sections[section_to_modify] = value_to_modify

    # def rename_recipe(self):
    #     '''renames the recipe in order to be recognized as modified'''
    #     if str(self.recipe_name).endswith(r"_(\d+).csv"):
    #         self.recipe_name = re.sub(r"_(\d+).csv", r"_(\d+ +1).csv", self.recipe_name)
    #     elif str(self.recipe_name).endswith(".csv"):
    #         self.recipe_name = str(self.recipe_name.suffix) + "_1.csv"
    #     else:
    #         print("recipe name is not formatted as expected")

    def rename_recipe(self):
        '''renames the recipe in order to be recognized as modified'''
        is_modified = re.search(r"_(\d+)\.csv$", self.recipe_name.name)
        if is_modified:
            current_number = int(is_modified.group(1))
            incremented_number = current_number + 1
            self.recipe_name.name = re.sub(r"_(\d+)\.csv$", f"_{incremented_number}.csv", self.recipe_name.name)
        elif self.recipe_name.name.endswith(".csv"):
            self.recipe_name.name = str(self.recipe_name.suffix) + "_1.csv"
        else:
            print("recipe name is not formatted as expected")

    def run_recipe_modification(self):
        if self.check_json_recipe_validity():
            self.section_modification()
            super().dataframe_to_hss
            super().rename_eps_data_header
            super().set_commas_afterwards
            self.rename_recipe()
            super().output_dataframe_to_json
