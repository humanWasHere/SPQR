from hss_creator import HssCreator
from ..parser_modules.csv_parser import CsvParser

# TODO check if HssCreator instance is needed to modify the recipe
# -> get file recipe that already has been output


class RecipeModificator(HssCreator):
    '''this class is meant to modify current instance of a class or imported recipe'''
    # TODO import recipe parser -> / csv parser
    # should it take a class instance in entry as RecipeModificator(instance) or RecipeModificator(HssCreator.__init__.attributes)

    # TODO penser à sortir des json
    # parser les json de sortie de recette ET les csv de sortie de recette
    # then -> df.to_json() -> pandas.to_json() -> pour récupération de sauvegardes et modifications

    # df.at[2, 'age'] = 30
    def __init__(self, json_recipe=None, csv_recipe=None):
        hss_creator_instance = HssCreator
        # this or HssCreator.import_json(json_recipe) ?
        self.imported_json_recipe = hss_creator_instance.import_json(json_recipe)  # This can be none
        # TODO make a logic that asks at least one recipe format to modify
        self.imported_csv_recipe = CsvParser.parse_csv(csv_recipe)
        self.imported_recipe = ""

        if (self.imported_json_recipe is not None and self.imported_csv_recipe is None):
            self.imported_recipe = "json_recipe"
        elif (self.imported_json_recipe is None and self.imported_csv_recipe is not None):
            self.imported_recipe = "csv_recipe"
