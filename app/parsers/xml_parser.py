import logging
import re
from pathlib import Path
from typing import Iterator

import lxml.etree as ET
import numpy as np
import pandas as pd

from .parse import FileParser


class CalibreXMLParser(FileParser):
    """Single entry point for parsing of Calibre Ruler and Clip files"""

    def __init__(self, tree: str | Path | ET._ElementTree):
        if not isinstance(tree, ET._ElementTree):
            tree = ET.parse(tree)
        self.tree: ET._ElementTree = tree
        self.type: str = tree.getroot().tag
        self._unit: str = tree.findtext('units') or 'dbu'
        # clips: units are defined in XML root. rulers: findtext -> None

    @property
    def unit(self) -> str:
        return self._unit

    def gen_rows_ruler(self) -> Iterator[tuple[str | None, float, float]]:
        """Generate rows of ruler name and center coordinates from Calibre ruler file (XML)"""
        for idx, ruler in enumerate(self.tree.findall('ruler')):
            # unit = ruler.findtext('units')
            # 'ruler/units' field is formatting for display only, data is stored in dbu
            # TODO lxml.objectify?
            name = ruler.findtext('comment') or f'Ruler{idx+1}'
            x_range = [int(float(coord.text)) for coord in ruler.findall('points/point/x')
                       if coord.text is not None]
            y_range = [int(float(coord.text)) for coord in ruler.findall('points/point/y')
                       if coord.text is not None]
            x = sum(x_range) / 2
            y = sum(y_range) / 2
            yield name, x, y

    def gen_rows_clip(self) -> Iterator[tuple[str | None, float, float]]:
        """Generate rows of clip name and center coordinates from Calibre clip file (XML)."""
        for clip in self.tree.findall('clip'):
            name = clip.findtext('name')
            box = {key: float(clip.findtext(key)) for key in ['x', 'y', 'width', 'height']}
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            yield name, x, y

    def parse_data(self) -> pd.DataFrame:
        """Dispatch content type to row generators and return dataframe of coordinates"""

        logger = logging.getLogger(__name__)
        logger.info("1. Parsing calibre rulers")
        if self.type == "rulers":
            rows = self.gen_rows_ruler()
        elif self.type == "clips":
            rows = self.gen_rows_clip()
        else:
            raise ValueError("Unknown XML type")
        parsed_data = pd.DataFrame(rows, columns=['name', 'x', 'y'])
        # TODO make post_parse?
        # Normalize name - keep alphanumeric only
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r' ', '_', s))
        parsed_data['name'] = parsed_data['name'].apply(lambda s: re.sub(r'\W+', '', s))
        # TODO add generic name if empty
        parsed_data['x_ap'] = np.nan
        parsed_data['y_ap'] = np.nan
        # TODO manage default columns
        if not parsed_data.empty:
            logger.info('Calibre rulers parsing done')
        return parsed_data  # .astype({'name': "string"})
