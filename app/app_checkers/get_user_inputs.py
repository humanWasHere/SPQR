from app_checkers.user_input_checker import UserInputChecker
from parser_modules.parse import CalibreXMLParser
from parser_modules.ssfile_parser import SsfileParser
from parser_modules.excel_parser import ExcelParser
from xml.etree.ElementTree import ParseError


class GetUserInputs():

    def __init__(self) -> None:
        self.user_input_checker_instance = UserInputChecker()
        self.parser = ''
        self.layout = ''
        self.layers = []  # should be str() for measure.py

    def get_user_parser_path(self):
        # Get parser input
        if not self.parser:
            while True:
                self.parser = self.user_input_checker_instance.get_secured_user_file_path("Enter a path to your parser :\n")
                if self.parser:
                    break

    def get_user_layout_path(self):
        if not self.layout:
            while True:
                self.layout = self.user_input_checker_instance.get_secured_user_file_path("Enter a path to your layout :\n")
                if self.layout:
                    break

    def get_user_layers_list(self):
        if not self.layers:
            while True:
                self.layers = self.user_input_checker_instance.get_secured_user_int_float_list("Enter layer(s) number list (separated with comma + space ', ' each time):\n")
                if self.layers:
                    # self.layers = self.layers.join(', ')
                    break

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

    def get_user_inputs(self):
        self.get_user_parser_path()
        self.get_user_layout_path()
        self.get_user_layers_list()
