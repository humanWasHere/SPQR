import numpy as np
import pandas as pd
import re
from io import StringIO

from .parse import FileParser


class TACRulerParser(FileParser):
    '''this class is used to parse TAC rulers'''

    unit = "nm"

    def __init__(self, file: str):
        self.file = file
        self.unit = "nm"

    def parse_data(self) -> pd.DataFrame:
        """Dispatch content to corresponding column mapping and return dataframe of coordinates"""
        # Try to identify type by column labels
        # ['gauge', 'base_x', 'base_y', 'head_x', 'head_y'] subset of columns
        return self.parse_tac_ruler()

    def parse_tac_ruler(self) -> pd.DataFrame:
        cols = ['gauge', 'base_x', 'base_y', 'head_x', 'head_y']
        data = pd.read_csv(self.file, usecols=cols, delimiter='\t', index_col=False, comment='#')
        self.data = pd.DataFrame({
            'name': data.gauge,
            'x': round((data.base_x + data.head_x) / 2),
            'y': round((data.base_y + data.head_y) / 2)
        })
        self.post_parse()

    def post_parse(self):
        """Fix names: remove whitespace and keep alphanumeric only"""
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\s+', '_', s))
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\W+', '', s))
        return self.data


class HSSParser(FileParser):
    '''parse existing hss recipe'''

    def __init__(self, csv_recipe_path) -> None:
        self.csv_recipe = csv_recipe_path

    unit = None

    def parse_data(self) -> pd.DataFrame:
        return self.parse_hss()

    def parse_hss(self) -> dict:
        """Parse HSS file. Do not handle exceptions yet"""
        # TODO check 'Type' columns before parsing ?
        # TODO data -> convert int to int or float to float when possible -> first level
        file_content = ""
        with open(self.csv_recipe, "r") as f:
            file_content = f.read()
        hss_sections: list[tuple[str, str]] = re.findall(r"(<\w+>),*([^<]*)", file_content)
        # sections = dict(hss_sections)
        constant_sections = {name: content.replace(',', '').replace('\n', '')
                             for name, content in hss_sections
                             if not content.strip().startswith('#')}
        table_sections = {name: pd.read_csv(StringIO(content))
                          for name, content in hss_sections
                          if content.strip().startswith('#')}
        # renaming '#', 'Type' and drop nan columns
        table_sections = {section: table_sections[section].rename(columns=lambda x: x.replace('#', ''))for section in table_sections}
        # TODO change for whole file ?
        table_sections['<EPS_Data>'].columns = [re.sub(r"Type\.(\d+)", r"Type\1", str(column)) for column in table_sections['<EPS_Data>'].columns]
        table_sections = {
            section: table_sections[section].drop(
                columns=table_sections[section].columns[
                    table_sections[section].columns.str.contains('Unnamed', case=False)
                ],
                axis=1
            )
            for section in table_sections
        }
        return (constant_sections, table_sections)
