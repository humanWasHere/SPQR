import pandas as pd
import openpyxl

# excel_file = "/work/opc/all/users/chanelir/semrc-test/assets/ssfile-genepy-proto_data.xlsx"


class excelParser:
    def __init__(self, file_to_parse):
        self.excel = file_to_parse

    def excel_to_dataframe(self):
        '''explain what this fonction does here'''
        # Open the Excel file
        workbook = openpyxl.load_workbook(self.excel)
        # Get the sheet names
        sheet_names = workbook.sheetnames
        # Check if there is at least one sheet
        if len(sheet_names) > 1:
            print('There is at least one sheet in the file.')
            sheet_name = input("Quel est le nom de la feuille que vous voulez processer ? ")
            # WARNING : must handle bad user input -> no sheet name after user_input
            excel_data = pd.read_excel(self.excel, sheet_name=sheet_name)
        else:
            excel_data = pd.read_excel(self.excel)

        df = pd.DataFrame(excel_data)
        return df.head()


# parser_instance = excelParser(excel_file)
# print(parser_instance.excel_to_dataframe())
