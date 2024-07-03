from lxml.etree import XMLSyntaxError
import numpy as np
import pandas as pd

from .file_parser import FileParser
from .ssfile_parser import SSFileParser
from .xml_parser import CalibreXMLParser


class ParserSelection():
    """Automatically defines which parser we should use"""
    def __init__(self, json_conf):
        self.json_conf = json_conf

    def run_parsing_selection(self) -> FileParser:
        # TODO change to better selection logic (must choose between path or empty but not accept to take both)
        if self.json_conf['parser'] == "":
            parser_instance = OPCfieldReverse(self.json_conf['opcfield_x'], self.json_conf['opcfield_y'],
                                              self.json_conf['step_x'], self.json_conf['step_y'],
                                              self.json_conf['n_cols'], self.json_conf['n_rows'],
                                              self.json_conf['ap1_offset'][0], self.json_conf['ap1_offset'][1])
        else:
            try:
                parser_instance = CalibreXMLParser(self.json_conf['parser'])
            except (XMLSyntaxError, AttributeError):
                parser_instance = SSFileParser(self.json_conf['parser'], is_genepy=True)
                # /!\ only manages genepy ssfile at the moment
        return parser_instance


class OPCfieldReverse(FileParser):

    unit = None

    def __init__(self, origin_x: float, origin_y: float, step_x: float, step_y: float,
                 n_cols: int, n_rows: int, ap_x: float, ap_y: float,
                 origin_letter="A", origin_number=1) -> None:
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.step_x = step_x
        self.step_y = step_y
        self.n_cols = n_cols
        self.n_rows = n_rows
        self.ap_offset = ap_x, ap_y
        self.origin_letter = origin_letter
        self.origin_number = origin_number
        self.data: pd.DataFrame
        self.unit = 'um'

    def opcfield_reverse(self) -> pd.DataFrame:
        """Build an OPCField coordinate matrix in arbitrary unit"""
        x_coords = np.arange(
            self.origin_x, self.origin_x + self.step_x * self.n_cols, self.step_x)
        y_coords = np.arange(
            self.origin_y, self.origin_y + self.step_y * self.n_rows, self.step_y)
        xx, yy = np.meshgrid(x_coords, y_coords)
        coords = np.vstack([xx.ravel(), yy.ravel()]).T
        self.data = pd.DataFrame(coords.round(3), columns=['x', 'y'])

        rows = np.repeat(np.arange(self.n_rows), self.n_cols)
        cols = np.tile(np.arange(self.n_cols), self.n_rows)
        self.data['row'] = rows + self.origin_number

        # nested function that generates column names with following logic : A-Z, AA-ZZ, etc.
        def get_column_letter(col_num):
            col_letter_str = ''
            while col_num >= 0:
                col_num, remainder = divmod(col_num, 26)
                col_letter_str = chr(ord(self.origin_letter.upper()) + remainder) + col_letter_str  # chr 65 = A
                col_num -= 1
            return col_letter_str

        self.data['col'] = [get_column_letter(col) for col in cols]
        # self.data['col'] = [chr(ord(self.origin_letter.upper()) + col) for col in cols]
        self.data.index = self.data['col'] + self.data['row'].astype(str)
        self.data['name'] = self.data.index
        return self.data

    def parse_data(self) -> pd.DataFrame:
        print("1. Running OPCField reverse gen")
        self.opcfield_reverse()
        self.data[['x_ap', 'y_ap']] = self.ap_offset
        if not self.data.empty:  # TODO add more logic - log
            print('\tOPCField reverse done')
        return self.data
