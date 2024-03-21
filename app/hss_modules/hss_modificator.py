from .hss_creator import HssCreator
from ..parser_modules.csv_parser import CsvParser

# TODO check if HssCreator instance is needed to modify the recipe
# -> get file recipe that already has been output


class RecipeModificator(HssCreator):
    '''this class is meant to modify current instance of a class or imported recipe'''
    # TODO should it take a class instance in entry as RecipeModificator(instance) or RecipeModificator(HssCreator.__init__.attributes)
    def __init__(self, json_recipe=None, csv_recipe=None):
        if (json_recipe is not None):
            self.imported_json_recipe = self.parse_json_recipe(json_recipe)
        elif (csv_recipe is not None):
            self.imported_csv_recipe = self.parse_hss_recipe(csv_recipe)
        elif (json_recipe is None and csv_recipe is None):
            raise ImportError("no recipe was given")

    def parse_json_recipe(self, json_recipe):
        hss_creator_instance = HssCreator
        hss_creator_instance.import_json(json_recipe)
        # + json_to_dataframe

    def parse_hss_recipe(self, csv_recipe):
        csv_parser_instance = CsvParser
        csv_parser_instance.parse_csv(csv_recipe)
