import csv
import json
import logging
import re
from pathlib import Path
from typing import Type

import numpy as np
import pandas as pd
from lxml import etree

from .csv_parser import HSSParser, TACRulerParser
from .file_parser import FileParser
from .json_parser import JSONParser
from .ssfile_parser import SSFileParser
from .xml_parser import CalibreXMLParser

logger = logging.getLogger(__name__)


def get_parser(value: str) -> Type[FileParser]:
    if value == "":
        return OPCFieldReverse
    if not Path(value).exists():
        logger.error(f"FileNotFoundError: {value} not found. Check input file path, or leave empty.")
        raise FileNotFoundError(f'{value} not found. Check input file path, or leave empty.')
    # Sample the file to detect content type
    # CSV
    with open(value, 'r', encoding='utf-8') as file:
        sample = file.read(2048)
    # if re.search(r"<\w+>", sample):  # matches XML
    if not sample.strip().startswith('{') and re.search("<FileID>", sample):
        return HSSParser
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=';\t,')
        header = next(csv.reader(sample.splitlines(), dialect))
        if {'gauge', 'base_x', 'base_y', 'head_x', 'head_y'}.issubset(header):
            return TACRulerParser
        if {'Name', 'X_coord_Pat', 'Y_coord_Pat', 'X_coord_Addr'}.issubset(header):
            return SSFileParser
    except csv.Error:
        logger.debug("csv.Error: ?")
        pass  # not a CSV or dialect not found
    # Read all file
    content = Path(value).read_text()
    # XML
    try:
        root = etree.fromstring(content)
        # CalibreXMLParser(root.getroottree())
        return CalibreXMLParser
    except etree.XMLSyntaxError:
        logger.debug("etree.XMLSyntaxError: ?")
        pass  # not an XML
    # JSON
    try:
        json.loads(content)
        return JSONParser
    except json.JSONDecodeError:
        logger.debug("json.JSONDecodeError: ?")
        pass
    return None


class OPCFieldReverse(FileParser):

    unit = 'um'

    def __init__(self, origin_x: float, origin_y: float, step_x: float, step_y: float,
                 n_rows: int, n_cols: int, ap_x: float, ap_y: float,
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
        logger.info("1. Running OPCField reverse gen")
        self.opcfield_reverse()
        self.data[['x_ap', 'y_ap']] = self.ap_offset
        if not self.data.empty:
            logger.info('OPCField reverse done')
        return self.data
