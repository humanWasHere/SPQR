from app_checkers.input_checker import UserInputChecker
# from parser_modules.parse import CalibreXMLParser
# from parser_modules.ssfile_parser import SsfileParser
# from parser_modules.excel_parser import ExcelParser
# from xml.etree.ElementTree import ParseError


class GetUserInputs():

    def __init__(self) -> None:
        self.user_input_checker_instance = UserInputChecker()

    def get_user_secured_path(self, message) -> str:
        user_path = ""
        if not user_path:
            while True:
                user_path = self.user_input_checker_instance.get_secured_user_filepath(message)
                if user_path:
                    return user_path

    def get_user_secured_list_int_float(self, message) -> list:
        user_list = []
        if not user_list:
            while True:
                user_list = self.user_input_checker_instance.get_secured_user_list_int_float(message)
                if user_list:
                    return user_list

    # def auto_select_parser(self):
    #     # TODO change selection logic
    #     try:
    #         # try parsing XML files
    #         # TODO should have under selection in XML files
    #         calibre_ruler_parser_instance = CalibreXMLParser(self.parser)  # test input
    #         data_parsed = calibre_ruler_parser_instance.parse_data()
    #     except ParseError:
    #         # try in indent between 2 other than XML
    #         try:
    #             # select between genepy or other ssfile in ssfile parser -> is_genepy
    #             ssfile_parser_instance = SsfileParser(self.parser, is_genepy=True)
    #             data_parsed = ssfile_parser_instance.parse_data().iloc[60:70]
    #         except ParseError:
    #             excel_parser_instance = ExcelParser()
    #             data_parsed = excel_parser_instance.parse_data()
    #     return data_parsed
