import re
from pathlib import Path

from .hss_creator import HssCreator
from ..parsers.csv_parser import HSSParser
from ..parsers.json_parser import JSONParser, import_json

# TODO check if HssCreator instance is needed to modify the recipe
# -> get file recipe that already has been output
# uses json_parser.py -> import HssCreator heritage in RecipeModificator or in JsonParser


class RecipeModificator(HssCreator):
    '''this class is meant to modify current instance of a class or imported recipe'''
    # TODO should it take a class instance in entry as RecipeModificator(instance)
    # or RecipeModificator(HssCreator.__init__.attributes)
    def __init__(self, json_recipe: Path = None, csv_recipe: Path = None):
        # super().__init__  -> after for eps
        if csv_recipe is None:
            self.imported_csv_recipe = None
            self.imported_json_recipe = Path(json_recipe)
            self.working_recipe_path = Path(json_recipe)
            json_parser_instance = JSONParser(self.imported_json_recipe)
            self.constant_sections, self.table_sections = json_parser_instance.json_to_section_dicts()
            # print(f"here is constant_sections : {self.constant_sections}. Which is {type(self.constant_sections)}")
            # print(f"here is table_sections : {self.table_sections}. Which is {type(self.table_sections)}")
        elif json_recipe is None:
            self.imported_json_recipe = None
            self.imported_csv_recipe = Path(csv_recipe)
            self.working_recipe_path = Path(csv_recipe)
            hss_parser_instance = HSSParser(self.imported_csv_recipe)
            self.constant_sections, self.table_sections = hss_parser_instance.parse_data()
            # print(f"here is constant_sections : {self.constant_sections}. Which is {type(self.constant_sections)}")
            # print(f"here is table_sections : {self.table_sections}. Which is {type(self.table_sections)}")
        elif (json_recipe is None and csv_recipe is None):
            raise ImportError("no recipe was given")
        self.json_template = Path(__file__).resolve().parents[2] / "assets" / "template_SEM_recipe.json"

    def check_json_recipe_validity(self) -> bool:
        '''checks wether or not the imported recipe to modificate
        has the columns of the json template
        by json comparison'''
        # comparing json template at lowest conversion level (if json_to_dataframe is bad -> it doesn't impact here)
        keys_json_template = list(import_json(self.json_template).keys())
        keys_json_recipe = list(import_json(self.imported_json_recipe).keys())
        if keys_json_template != keys_json_recipe:
            print(f"imported recipe is not valid compared to template\n{keys_json_template}\n{keys_json_recipe}")
            return False
        else:
            return True

    def check_hss_recipe_validity(self) -> bool:
        '''checks wether or not the imported recipe to modificate
        has the columns of the json template
        by dataframe comparison'''
        json_template_parser_instance = JSONParser(str(self.json_template))
        constant_sections_json_template, table_sections_json_template = json_template_parser_instance.parse_data()
        csv_recipe_parser_instance = HSSParser(str(self.imported_csv_recipe))
        constant_sections_csv_recipe, table_sections_csv_recipe = csv_recipe_parser_instance.parse_data()
        # constant_sections
        # if constant_sections_json_template.keys() != constant_sections_csv_recipe.keys():
        #     print(f"here is constant_sections json_template : {constant_sections_json_template}\nhere is constant_sections csv_recipe : {constant_sections_csv_recipe}")
        assert constant_sections_json_template.keys() == constant_sections_csv_recipe.keys(), "imported recipe is not valid (at least at constant_sections level)"
        # table_sections
        assert [key for key in table_sections_json_template] == [key for key in table_sections_csv_recipe]
        # assert csv_section == template_section, "imported recipe is not valid (in table_sections level)"

    def section_modification(self):
        # TODO make an iterator -> while -> change different values -> englobe toute la fonction
        # TODO manage whole columns modification vs row modification
        section_to_modify = input("Which section do you want to modify?\n")
        subsection_to_modify = input("Which subsection do you want to modify? else press Enter\n")
        value_position = input("Do you want to modify only one specific value ? print number else press Enter")
        modified_value = input("Enter the value you want to set.\n")

        if section_to_modify in self.constant_sections:
            if value_position != "":
                self.constant_sections[section_to_modify].iloc[value_position] = modified_value
            else:
                self.constant_sections[section_to_modify] = modified_value
        elif section_to_modify in self.table_sections:
            if section_to_modify in self.table_sections.keys():
                if subsection_to_modify in self.table_sections[section_to_modify].columns:
                    if value_position != "":
                        self.table_sections[section_to_modify][subsection_to_modify].iloc[value_position] = modified_value
                    else:
                        self.table_sections[section_to_modify][subsection_to_modify] = modified_value
                else:
                    print(f"{subsection_to_modify} apparently not in df")
        else:
            print(f"section {section_to_modify} apparently not in any dict")

    def rename_recipe(self) -> str:
        '''renames the recipe in order to be recognized as modified'''
        # /!\ modify name without extension since HssCreator.will name the recipe -> insert it as a parameter of HssCreator
        is_previously_modified = re.search(r"_(\d+)\.(csv|json)$", self.working_recipe_path.name)
        if is_previously_modified:
            current_number = int(is_previously_modified.group(1))
            incremented_number = current_number + 1
            self.working_recipe_path = re.sub(r"_(\d+)\.(csv|json)$", f"_{incremented_number}.\\2", self.working_recipe_path.name)
        elif str(self.working_recipe_path.name).endswith((".json", ".csv")):
            new_recipe_name = str(self.working_recipe_path.stem) + "_1" + self.working_recipe_path.suffix
            return new_recipe_name
        else:
            print("recipe name is not formatted as expected")

    def run_recipe_modification(self):
        if self.imported_json_recipe:
            if self.check_json_recipe_validity():
                self.section_modification()
                super().dataframe_to_hss()
                super().rename_eps_data_header()
                super().set_commas_afterwards()
                # path +message for existing
                super().recipe_name = self.rename_recipe()
                super().output_dataframe_to_json()
        elif self.imported_csv_recipe:
            if self.check_hss_recipe_validity():
                self.section_modification()
                super().dataframe_to_hss()
                super().rename_eps_data_header()
                super().set_commas_afterwards()
                # path +message for existing
                super().recipe_name = self.rename_recipe()
                super().output_dataframe_to_json()
        # else:
        #     print("no recipe has been given")
