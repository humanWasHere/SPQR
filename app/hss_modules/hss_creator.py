class CsvTemplate:
    def __init__(self, template_recette):
        self.template_hss_idp = template_recette

    def create_hss_template(self, column_number):
        # code that creates the hss template here
        # call apply_commas() et résultat des calculs
        pass

    def calculate_number_of_commas(self, column_number, row_id):
        # get max column in imported df
        # code that returns an int of how many commas is needed by rows
        # can be called in each lines IF NEEDED
        pass

    def apply_commas(self, column_number_to_match):
        # code that will apply the correct number of commas in the line
        # counts the number of word or number of commas
        pass


class CsvCalculator(CsvTemplate):
    def calculate1(self, values):
        # Calculation logic goes here
        pass
