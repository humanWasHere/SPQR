import pandas as pd
import openpyxl


class ExcelParser:
    def __init__(self, file_to_parse):
        self.excel = file_to_parse

    def excel_to_dataframe(self):
        '''explain what this fonction does here'''
        workbook = openpyxl.load_workbook(self.excel)
        sheet_names = workbook.sheetnames
        if len(sheet_names) > 1:
            print('There is at least one sheet in the file.')
            sheet_name = input("Quel est le nom de la feuille que vous voulez processer ? ")
            # WARNING : must handle bad user input -> no sheet name after user_input
            excel_data = pd.read_excel(self.excel, sheet_name=sheet_name)
        else:
            excel_data = pd.read_excel(self.excel)

        df = pd.DataFrame(excel_data)
        return df.head()

    def unit(self):
        pass

    def unit_converter(self, unit):
        pass

    def parse_data(self) -> pd.DataFrame:
        pass
