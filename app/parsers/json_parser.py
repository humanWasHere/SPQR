import pandas as pd
import json
from pathlib import Path

from .parse import FileParser


def import_json(json_file) -> dict:
    """Parse JSON file. Do not handle exceptions yet"""
    try:
        return json.loads(json_file.read_text())
    except:
        return json.loads(Path(json_file).read_text())


class JsonParser(FileParser):

    def __init__(self, json_file_path) -> None:
        self.json_file = import_json(json_file_path)
        self.constant_sections = {}
        self.table_sections = {}

    def unit(self):
        pass

    def parse_data(self):
        self.json_to_dataframe()

    def json_to_dataframe(self) -> None:
        """Parse a valid HSS JSON template into two dictionaries of unique sections:
        - a dict of strings for unique values -> {'section_name': "value"},
        - a dict of dataframes for table content -> {'section_name': pd.DataFrame}."""
        for section_name, content in self.json_file.items():
            if isinstance(content, dict):
                if isinstance(list(content.values())[0], list):
                    self.table_sections[section_name] = pd.DataFrame(content)
                else:
                    self.table_sections[section_name] = pd.json_normalize(content)
            else:
                self.constant_sections[section_name] = content
        return self.constant_sections, self.table_sections
