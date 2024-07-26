from pathlib import Path

import logging
import pandas as pd

from .parse import FileParser

# TODO checker de présence des colonnes 'name', 'coord x', 'coord y' 'unit' ?


class TACXParser(FileParser):
    """Parse TACX files"""

    unit = None

    def __init__(self, file_to_parse: str | Path):
        self.ssfile = Path(file_to_parse)
        self.constant_sections: dict[str, str] = {}
        self.table_sections: dict[str, pd.DataFrame] = {}
        self.data: pd.DataFrame

    def parse_data(self) -> pd.DataFrame:
        """Call the dedicated parsing logic depending on OPCField type"""
        logger = logging.getLogger(__name__)
        logger.info("1. Parsing TACX reports")
        # parse
        # convert columns name to internal column names
        if not self.data.empty:
            logger.info('TACX report parsing done')
        return self.data

    def parse_tac_x(self):
        pass
        # 'default' -> naming
        # get columns -> name -> data -> x/y
        # try csv:
            # \t
        # except open file + regex
            # get -- sections
            # line skip
        # make constant and table sections
