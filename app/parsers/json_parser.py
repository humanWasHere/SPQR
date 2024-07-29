import json
import logging
from pathlib import Path

import pandas as pd

from .file_parser import FileParser


def import_json(json_file: str | Path) -> dict[str, dict]:
    """Parse generic JSON file"""
    try:
        return json.loads(Path(json_file).read_text())
    except FileNotFoundError:
        raise ValueError(f"The file {json_file} was not found.")
    except json.JSONDecodeError as e:
        raise ValueError(f"The file {json_file} contains invalid JSON:\n\t{e}.")


class JSONParser(FileParser):

    def __init__(self, json_file_path: str | Path) -> None:
        self.json_content = import_json(json_file_path)
        # TODO schema validation
        self.constant_sections: dict[str, str] = {}
        self.table_sections: dict[str, pd.DataFrame] = {}
        self.epsdata_section: pd.DataFrame
        self._unit = "nm"  # HSS default

    @property
    def unit(self):
        return self._unit

    def parse_data(self):
        logger = logging.getLogger(__name__)
        logger.info("1. Parsing JSON")
        self.json_to_section_dicts()
        # TODO: reverse core data from EPS_Data content
        self.epsdata_section = self.table_sections['<EPS_Data>'].loc[
            :, ['EPS_Name', 'Move_X', 'Move_Y', 'AP1_X', 'AP1_Y']].copy()
        self.epsdata_section.columns = ['name', 'x', 'y', 'x_ap', 'y_ap']
        if not self.epsdata_section.empty:
            logger.info('JSON parsing done')
        return self.epsdata_section

    def json_to_section_dicts(self) -> 'JSONParser':
        """Parse a valid HSS JSON template into two dictionaries of unique sections:
        - a dict of strings for unique values -> {'section_name': "value"},
        - a dict of dataframes for table content -> {'section_name': pd.DataFrame}."""
        # Split other sections
        for section_name, content in self.json_content.items():
            if isinstance(content, dict):
                if isinstance(list(content.values())[0], list):
                    self.table_sections[section_name] = pd.DataFrame(content)
                else:
                    self.table_sections[section_name] = pd.json_normalize(content)
            else:
                self.constant_sections[section_name] = content
        return self
