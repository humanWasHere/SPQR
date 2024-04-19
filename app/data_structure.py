from dataclasses import dataclass
from .interfaces.calibre_python import layout_peek

@dataclass
class Block:
    # maskset: str
    # device: str
    layout_path: str
    # rotation: int

    def __post_init__(self):
        self.precision = layout_peek(self.layout_path, "precision")
        self.topcell = layout_peek(self.layout_path, "topcell")
