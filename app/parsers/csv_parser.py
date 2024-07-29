import re
import logging
from io import StringIO
from pathlib import Path

import pandas as pd

from .file_parser import FileParser


class TACRulerParser(FileParser):
    """Parse ruler files exported from TACX GUI"""
    unit = "nm"

    def __init__(self, file: str):
        self.file = file
        self.data: pd.DataFrame

    def parse_data(self) -> pd.DataFrame:
        """Dispatch content to corresponding column mapping and return dataframe of coordinates"""
        # Try to identify type by column labels
        # ['gauge', 'base_x', 'base_y', 'head_x', 'head_y'] subset of columns
        self.parse_tac_ruler()
        self.post_parse()
        return self.data

    def parse_tac_ruler(self):
        cols = ['gauge', 'base_x', 'base_y', 'head_x', 'head_y']
        data = pd.read_csv(self.file, usecols=cols, delimiter='\t', index_col=False, comment='#')
        self.data = pd.DataFrame({
            'name': data.gauge,
            'x': round((data.base_x + data.head_x) / 2),
            'y': round((data.base_y + data.head_y) / 2)
        })

    def post_parse(self):
        """Fix names: remove whitespace and keep alphanumeric only"""
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\s+', '_', s))
        self.data['name'] = self.data['name'].apply(lambda s: re.sub(r'\W+', '', s))


logger = logging.getLogger(__name__)


class HSSParser(FileParser):
    """Parse existing HSS recipe"""
    unit = 'nm'

    def __init__(self, csv_recipe_path) -> None:
        self.csv_recipe = Path(csv_recipe_path)
        self.constant_sections: dict[str, str] = {}
        self.table_sections: dict[str, pd.DataFrame] = {}

    def parse_data(self) -> pd.DataFrame:
        logger.info("1. Parsing csv recipe")
        self.parse_hss()
        data = self.table_sections['<EPS_Data>'].loc[
            :, ['EPS_Name', 'Move_X', 'Move_Y', 'AP1_X', 'AP1_Y']].copy()
        data.columns = pd.Index(['name', 'x', 'y', 'x_ap', 'y_ap'])
        if not data.empty:
            logger.info('Genepy ssfile parsing done')
        return data

    def parse_hss(self) -> tuple[dict, dict]:
        """Parse HSS file. Do not handle exceptions yet"""

        def parse_csv(content: str, name: str) -> pd.DataFrame | None:
            try:
                return pd.read_csv(StringIO(content))
            except pd.errors.ParserError:
                logger.error(f'Error parsing CSV data from {name}, skipping.')
                return None

        hss_sections: list[tuple[str, str]] = re.findall(r"(<\w+>),*([^<]*)",
                                                         self.csv_recipe.read_text())

        # Dispatch sections into dataframes or constant values
        for name, content in hss_sections:
            content = content.strip()
            if content.strip().startswith('#'):
                parsed = parse_csv(content.lstrip('#'), name)
                if parsed is None:
                    continue
                self.table_sections[name] = parsed
            else:
                self.constant_sections[name] = content.strip(',')

        # Rename 'Type' and drop null columns
        self.table_sections['<EPS_Data>'].rename(
            columns=lambda c: re.sub(r"Type\.(\d+)", r"Type\1", c), inplace=True)
        for name, table in self.table_sections.items():
            unnamed = table.columns[table.columns.str.contains('Unnamed:', case=False)]
            table.drop(columns=unnamed, inplace=True)

        return self.constant_sections, self.table_sections
