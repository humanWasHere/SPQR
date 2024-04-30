import re
import pandas as pd
import numpy as np
import lxml.etree as ET
from pathlib import Path
from .parse import FileParser, DataframeValidator


class CalibreXMLParser(FileParser):
    """Single entry point for parsing of Calibre Ruler and Clip files"""
    unit = None

    def __init__(self, tree: str | Path | ET._ElementTree):
        if not isinstance(tree, ET._ElementTree):
            tree = ET.parse(tree)
        self.tree = tree
        self.type = tree.getroot().tag
        self.unit = tree.findtext('units') or 'dbu'
        # clips: units are defined in XML root / rulers: findtext -> None

    def gen_rows_ruler(self):
        """Generate ruler name and center row by row from Calibre ruler XML"""
        for ruler in self.tree.findall('ruler'):
            # unit = ruler.findtext('units')
            # formatting for display only, data is stored in dbu
            name = ruler.findtext('comment')
            x_range = [int(float(coord.text)) for coord in ruler.findall('points/point/x')]
            y_range = [int(float(coord.text)) for coord in ruler.findall('points/point/y')]
            x = sum(x_range) / 2
            y = sum(y_range) / 2
            yield name, x, y

    def gen_rows_clip(self):
        """Generate clip name and center row by row from Calibre clip XML."""
        for clip in self.tree.findall('clip'):
            name = clip.findtext('name')
            box = {key: float(clip.findtext(key)) for key in ['x', 'y', 'width', 'height']}
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            yield name, x, y

    @DataframeValidator.validate
    def parse_data_decorated(self):
        # TODO dtypes = enfer
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
        # TODO: name as index? / enforce format?
        parsed_data = pd.DataFrame(rows, columns=['name', 'x', 'y'])
        # Normalize name - keep alphanumeric only
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r' ', '_', s))
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r'\W+', '', s))
        # TODO add generic name if empty
        parsed_data['x_ap'] = np.nan
        parsed_data['y_ap'] = np.nan
        # TODO manage default columns
        if not parsed_data.empty:  # TODO add more logic - log
            print('\tcalibre ruler parsing done')
        return parsed_data  # .astype({'name': "string"})
