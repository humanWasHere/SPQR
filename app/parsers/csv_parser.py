import pandas as pd
import re
from .parse import FileParser


# TODO make it fit the flow
class TACRulerParser(FileParser):
    '''this class is used to parse TAC rulers'''

    def __init__(self, file: str):
        self.file = file
        self.unit = "nm"

    def parse_data(self) -> pd.DataFrame:
        """Dispatch content to corresponding column mapping and return dataframe of coordinates"""
        # Try to identify type by column labels
        {'cols': lambda x: x in ['gauge', 'base_x', 'base_y', 'head_x', 'head_y'], 'method': self.parse_tac_ruler}
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
        """Fix names"""
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\s+', '_', s))  # remove whitespace
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\W+', '', s))  # keep alphanumeric only
        return self.data


class HssParser(FileParser):
    '''should parse existing recipe'''
    def __init__(self):
        self.unit = ""

    def parse_data(self):
        pass