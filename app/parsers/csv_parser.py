import numpy as np
import pandas as pd
import re
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
    '''should parse existing recipe'''

    unit = None

    def parse_data(self) -> pd.DataFrame:
        return self.parse_hss()

    def parse_hss(self, csv_recipe) -> dict:
        """Parse HSS file. Do not handle exceptions yet"""
        # FIXME not all dataframe are working
        # FIXME must rename 'Type' columns before parsing
        # FIXME trouver la manière la plus propre entre prendre la première valeur de first_level, dropna for rows, autre ? -> comparer à l'existant
        # TODO data -> convert int to int or float to float when possible -> first level
        constant_sections = {}
        table_sections = {}
        previous_row_type = ""
        current_section = ""
        # parsing engine ?
        result = pd.read_csv(csv_recipe, index_col=False, header=None)
        for index, row in result.iterrows():
            # section
            if str(row.iloc[0]).startswith("<") & str(row.iloc[0]).endswith(">"):
                current_section = str(row.iloc[0])
                previous_row_type = "<"
            # subsection
            elif str(row.iloc[0]).startswith("#"):
                # TODO remove # from column  (beginning of the row)
                # if str(row.iloc[0]).startswith('#'):
                #    row = str(row.iloc[0])[1:]
                table_sections[current_section] = pd.DataFrame(columns=row.to_list())
                previous_row_type = "#"
            # value
            else:
                # first level
                if previous_row_type == "<":
                    row.dropna(axis=0, how='all', inplace=True)
                    constant_sections[current_section] = list(row.values)
                # second level
                elif previous_row_type == "#" or previous_row_type == "value":
                    table_sections[current_section] = pd.concat([table_sections[current_section],
                                                                pd.DataFrame([row.to_list()],
                                                                columns=table_sections[current_section].columns)],
                                                                ignore_index=True)
                    previous_row_type = "value"
                else:
                    print("should not exist : error in csv parsing (row syntax)")
        table_sections = [table_sections[section].loc[:, table_sections[section].columns.notnull()] for section in table_sections]
        return constant_sections, table_sections
