import pandas as pd
import re
from .parse import FileParser


# abstract class ? -> should be mother class ?
class CsvParser:
    '''should parse different type of csv'''
    def __init__(self):
        pass

    def parse_csv(self):
        '''this function actually parses csv'''
        pass


class TACRulerParser(FileParser):
    '''this class is used to parse TAC rulers'''
    unit = "nm"

    def __init__(self, file: str):
        self.unit = "nm"

    def parse_data(self) -> pd.DataFrame:
        """Dispatch content to corresponding column mapping and return dataframe of coordinates"""
        # Try to identify type by column labels
        {'cols': lambda x: x in ['gauge', 'base_x', 'base_y', 'head_x', 'head_y'], 'method': self.parse_tac_ruler}
        return self.parse_tac_ruler()

    def post_parse(self):
        """Fix names"""
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\s+', '_', s))  # remove whitespace
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\W+', '', s))  # keep alphanumeric only
        return self.data

    def parse_tac_ruler(self) -> pd.DataFrame:
        cols = ['gauge', 'base_x', 'base_y', 'head_x', 'head_y']
        data = pd.read_csv(self.file, usecols=cols, delimiter='\t', index_col=False, comment='#')  
        self.data = pd.DataFrame({
            'name': data.gauge,
            'x': round((data.base_x + data.head_x) / 2),
            'y': round((data.base_y + data.head_y) / 2)
        })
        self.post_parse()


class HssParser:
    '''sould parse existing recipe'''
    def __init__(self):
        pass

    def parse_recipe(self):
        pass
