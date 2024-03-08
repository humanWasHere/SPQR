from typing import Union, TextIO
import re
from pathlib import Path
import pandas as pd
import xml.etree.ElementTree as ET

# FIXME all :)

unit = None


class XMLParser:
    '''this class is used to parse XML files (which can be ?)'''
    def __init__(self, tree):
        if isinstance(tree, str):
            tree = ET.parse(tree)
        self.tree = tree
        self.type = tree.getroot().tag
        self.unit = tree.findtext('units') or 'dbu'  # rulers -> None

    def gen_rows_ruler(self):
        """Generate ruler name and center row by row from Calibre ruler XML. Data is stored in DBU."""
        if self.type != "rulers":
            raise TypeError("Can only be used on XML rulers")
        for ruler in self.tree.findall('ruler'):
            # unit = ruler.findtext('units')  # formatting for display only
            name = ruler.findtext('comment')
            x_range = [int(float(coord.text)) for coord in ruler.findall('points/point/x')]
            y_range = [int(float(coord.text)) for coord in ruler.findall('points/point/y')]
            x = sum(x_range) / 2
            y = sum(y_range) / 2
            yield name, x, y

    def gen_rows_clip(self):
        """Generate clip name and center row by row from Calibre clip XML. Units are defined in XML root"""
        for clip in self.tree.findall('clip'):
            name = clip.findtext('name')
            box = {key: float(clip.findtext(key)) for key in ['x', 'y', 'width', 'height']}
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            yield name, x, y

    def parse_data(self):
        """Dispatch content type to row generators and return dataframe of coordinates"""
        if self.type == "rulers":
            rows = self.gen_rows_ruler()
        elif self.type == "clips":
            rows = self.gen_rows_clip()
        else:
            raise ValueError("Unknown XML type")
        parsed_data = pd.DataFrame(rows, columns=['name', 'x', 'y'])  # todo: name as index? / enforce format?
        # Fix name
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r' ', '_', s))
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r'\W+', '', s))  # keep alphanumeric only
        return parsed_data

    def get_parser(file: Union[Path, str, TextIO]) -> TSVParser:
        """Factory providing the appropriate parser depending on gauge data type, takes path or buffer"""
        try:
            # Check if file is XML type
            xml_tree = ET.parse(file)
            return XMLParser(xml_tree)
        except ET.ParseError:
            # Else assume TSV type
            if hasattr(file, 'seek'):
                file.seek(0)  # to support file-handles, need to read again
            return TSVParser(file)
        # except FileNotFoundError:
        #     return get_parser(StringIO(file))  # works for plain text content but weird
