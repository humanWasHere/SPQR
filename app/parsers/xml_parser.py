import re
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from .parse import FileParser  # , DataframeValidator


class DataframeValidator:
    # TODO: implement or rework
    SCHEMA = {
        'name': str,
        'x': int,
        'y': int,
        'x_ap': int,
        'y_ap': int,
        'orient': str,
        'target_cd': int,
        'magnification': int
    }

    @classmethod
    def validate(cls, func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            cls.validate_schema(data)
        return wrapper

    @classmethod
    def validate_schema(cls, dataframe) -> None:
        for col_name, series in dataframe.items():
            # TODO try conversion
            assert series.dtype == cls.SCHEMA[col_name], f"wrong dtype for {col_name}: expected {cls.SCHEMA[col_name]} got {series.dtype}"


class CalibreXMLParser(FileParser):
    # TODO commonaliser gen_rows_ruler et gen_rows_clip ?
    unit = None

    def __init__(self, tree: str | Path | ET.ElementTree, precision):
        if not isinstance(tree, ET.ElementTree):
            tree = ET.parse(tree)
        self.tree = tree
        self.type = tree.getroot().tag
        self.unit = tree.findtext('units') or 'dbu'  # rulers -> None
        self.precision = precision  # TODO to remove ?

    def gen_rows_ruler(self):
        """Generate ruler name and center row by row from Calibre ruler XML. Data is stored in DBU."""
        if self.type != "rulers":
            raise TypeError("Can only be used on XML rulers")
        for ruler in self.tree.findall('ruler'):
            # unit = ruler.findtext('units')  # formatting for display only
            name = ruler.findtext('comment')
            # unit = ruler.findtext('units')  # Romain C
            x_range = [int(float(coord.text)) for coord in ruler.findall('points/point/x')]
            y_range = [int(float(coord.text)) for coord in ruler.findall('points/point/y')]
            x = sum(x_range) / 2
            y = sum(y_range) / 2
            # x = self.convert_to_dbu(unit, x)
            # y = self.convert_to_dbu(unit, y)
            yield name, x, y

    def gen_rows_clip(self):
        """Generate clip name and center row by row from Calibre clip XML. Units are defined in XML root"""
        for clip in self.tree.findall('clip'):
            name = clip.findtext('name')
            # unit = clip.findtext('units')  # Romain C
            box = {key: float(clip.findtext(key)) for key in ['x', 'y', 'width', 'height']}  # FIXME should convert to int ?
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            # x = self.convert_to_dbu(unit, x)
            # y = self.convert_to_dbu(unit, y)
            yield name, x, y

    @DataframeValidator.validate
    def parse_data_decorated(self):
        return self.parse_data()

    def parse_data(self):
        """Dispatch content type to row generators and return dataframe of coordinates"""
        # print('1. calibre ruler parsing')  # TODO log
        if self.type == "rulers":
            rows = self.gen_rows_ruler()
        elif self.type == "clips":
            rows = self.gen_rows_clip()
        else:
            raise ValueError("Unknown XML type")
        parsed_data = pd.DataFrame(rows, columns=['name', 'x', 'y'])  # TODO: name as index? / enforce format?
        # Normalize name
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r' ', '_', s))
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r'\W+', '', s))  # keep alphanumeric only
        # TODO add generic name if empty
        parsed_data['x_ap'] = None
        parsed_data['y_ap'] = None
        # TODO manage default columns
        # if not parsed_data.empty:  # TODO add more logic - log
        #     print('\tcalibre ruler parsing done')
        return parsed_data
