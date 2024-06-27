import pandas as pd
import json
from pathlib import Path

from .parse import FileParser


def import_json(json_file: str | Path) -> dict:
    """Parse generic JSON file"""
    try:
        return json.loads(Path(json_file).read_text())
    except FileNotFoundError:
        raise ValueError(f"The file {json_file} was not found.")
    except json.JSONDecodeError:
        raise ValueError(f"The file {json_file} contains invalid JSON.")


class JsonParser(FileParser):

    def __init__(self, json_file_path: str | Path) -> None:
        self.json_content = import_json(json_file_path)
        # TODO schema validation
        self.constant_sections: dict[str, str] = {}
        self.table_sections: dict[str, pd.DataFrame] = {}
        self.epsdata_section: dict = {}
        self._unit = "nm"  # HSS default

    @property
    def unit(self):
        return self._unit

    def parse_data(self):
        self.json_to_section_dicts()
        # TODO: reverse core data from EPS_Data content
        data = self.epsdata_section[['EPS_Name', 'Move_X', 'Move_Y']]
        return data.rename(columns=['name', 'x', 'y'])

    def json_to_section_dicts(self) -> 'JsonParser':
        """Parse a valid HSS JSON template into two dictionaries of unique sections:
        - a dict of strings for unique values -> {'section_name': "value"},
        - a dict of dataframes for table content -> {'section_name': pd.DataFrame}."""

        self.epsdata_section = self.json_content.get('<EPS_Data>')  # pop?
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
