from dataclasses import dataclass, field
from .parsers.parse import FileParser
from .interfaces.calibre_python import layout_peek


@dataclass
class Block:
    # maskset: str
    # device: str
    layout_path: str
    topcell: str = field(init=False)
    precision: int = field(init=False)
    # rotation: int

    def __post_init__(self):
        self.precision = int(float(layout_peek(self.layout_path, "precision")))
        self.topcell = layout_peek(self.layout_path, "topcell")


class CoreData:
    def __init__(self, parser: FileParser, block: Block) -> None:
        self.coords = parser
        self.data = parser.parse_data_dbu(block.precision)
        self.block = block

    def validate_data(self):
        pass

    def measure(self):
        pass
