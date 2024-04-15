from dataclasses import dataclass
from ..interfaces.calibre_python import layout_peek


@dataclass
class Block:
    # maskset: str
    # index: str
    layout_path: str
    # rotation: int
    # FIXME layers ???

    def __post_init__(self):
        # TODO ensure it is int(float(precision))
        self.precision = int(float(layout_peek(self.layout_path, "precision")))
        self.topcell = layout_peek(self.layout_path, "topcell")
