import pandas as pd

excel_file = "/work/opc/all/users/chanelir/semrc-test/assets/ssfile-genepy-proto_data.xlsx"

class excelParser:

    def __init__(self, file_to_parse):
        self.excel = file_to_parse

    def excel_to_dataframe(self):
        # Chemin du fichier Excel

        # Nom de la feuille à parser
        sheet_name = input("Quel est le nom de la feuille que vous voulez processer ? ")
        # handle bad user input -> no sheet name after user_input

        # Lecture du fichier Excel
        excel_data = pd.read_excel(self.excel, sheet_name=sheet_name)

        # Conversion en dataframe pandas
        df = pd.DataFrame(excel_data)

        # check if user has all necessary columns
        print(df.head())

    # def __repr__():
    #     print(excelParser.excel_to_dataframe())


parser_instance = excelParser(excel_file)
parser_instance.excel_to_dataframe()
