from hss_creator import HssCreator

# TODO check if HssCreator instance is needed to modify the recipe
# -> get file recipe that already has been output


class RecipeModificator(HssCreator):
    # header = [label + str(i) if label == "Type" else label for i, label in enumerate(EPS_COLUMNS)]  # uniquify Type cols
    # then -> df.to_json() -> pandas.to_json() -> pour récupération de sauvegardes et modifications

    # access data on 2 lever dict -> city = data["person2"]["address"]["city"]
    # ex
    # "person2": {
    #   "address": {
    #        "city": "Othertown",
    # print(city)  # Output: "Othertown"

    # format data : data.format(format_arguments)

    # df.at[2, 'age'] = 30
    def __init__(self):
        pass
