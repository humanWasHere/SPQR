from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from .parsers.parse import FileParser
from .interfaces.calibre_python import get_layout_precision, get_layout_topcell
# from .interfaces.calibre_python import layout_peek


@dataclass
class Block:
    """Dataclass that holds the layout values."""
    # maskset: str
    # device: str
    layout_path: Path
    topcell: str = field(init=False)
    precision: int = field(init=False)
    # rotation: int

    def __post_init__(self):
        self.precision = get_layout_precision(self.layout_path)
        self.topcell = get_layout_topcell(self.layout_path)
        # self.precision = int(float(layout_peek(self.layout_path, "-precision")))
        # self.topcell = layout_peek(self.layout_path, "-topcell")


class CoreData:
    """Mother class of different configuration values."""
    SCHEMA = {
        'name': "string",
        'x': int, 'y': int, 'x_ap': int, 'y_ap': int, 'x_af': int, 'y_af': int,
        'orientation': "string", 'target_cd': int, 'magnification': int
    }

    def __init__(self, parser: FileParser, block: Block, mag: int) -> None:
        self.parser = parser
        self.block = block
        self.data = pd.DataFrame(columns=self.SCHEMA.keys())

        parsed_data = parser.parse_data_dbu(block.precision)
        self.data.update(parsed_data)
        self.magnification = mag

    # TODO use pandera?
    @classmethod
    def validate(cls, func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            cls.validate_schema(data)
        return wrapper

    @classmethod
    def validate_schema(cls, dataframe) -> None:
        for col_name, series in dataframe.items():
            assert series.dtype == cls.SCHEMA[col_name], \
                f"Wrong dtype for {col_name}: expected {cls.SCHEMA[col_name]} got {series.dtype}"

    def measure(self):
        pass
