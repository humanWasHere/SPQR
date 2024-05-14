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
        # TODO data -> convert int to int or float to float when possible -> first level
        # TODO change var name / make it more pandas friendly
        first_level = {}
        second_level = {}
        # TODO change to index[-1] == "#" à la place de stocker dans une var ?
        previous_row_type = ""
        current_section = ""
        # current_second_section_series = pd.Series
        result = pd.read_csv(csv_recipe, index_col=False, header=None)
        for index, row in result.iterrows():
            # print(f"{row.iloc[0]}")
            row.dropna(axis=0, how='all', inplace=True)
            if str(row.iloc[0]).startswith("<") & str(row.iloc[0]).endswith(">"):
                # row.is_section
                current_section = str(row.iloc[0])
                previous_row_type = "<"
            elif str(row.iloc[0]).startswith("#"):
                # row.is_sous_section
                # current_second_section_series = row
                previous_row_type = "#"
                # TODO remove # from column names
                # TODO row.dropna ?
                second_level[current_section] = pd.DataFrame(columns=row.to_list())
            else:
                # row.is_value
                if previous_row_type == "<":
                    # row.dropna(axis=0, how='all', inplace=True)
                    first_level[current_section] = str(row.values)
                elif previous_row_type == "#":
                    # TODO check this row
                    # if len(second_level[current_section]) == len(row.to_list()):
                    #     for i in range(0, len(second_level[current_section].columns)):
                    #         for columns in second_level[current_section].columns:
                    #             second_level[current_section][columns] = row.to_list()[i]
                    # else:
                    #     print(f"dataframe {current_section} has columns/values mismatch")
                    columns = second_level[current_section].columns
                    values = row.to_list()
                    data_to_add = dict(zip(columns, values))
                    second_level[current_section] = pd.DataFrame([data_to_add])
                    previous_row_type = "value"
                elif previous_row_type == "value":
                    # TODO EPS_Data -> don't override
                    second_level[current_section] = row.to_list()
                    previous_row_type = "value"
                else:
                    print("should not exist : error in csv parsing (row syntax)")

        # print(f"first level : {first_level}")
        # print(f"{second_level}")
                    
        return first_level, second_levelssss
