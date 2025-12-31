from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import islice

from common.FileReader import CordParser


def main(cls):
    # input_coords = CordParser().read_file("./test_input.txt")
    input_coords = CordParser().read_file("./input.txt")
    print(cls.find_max_area(input_coords))


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def get_area(self, other_coord: Coord) -> int:
        return (abs(self.x - other_coord.x) + 1) * (abs(self.y - other_coord.y) + 1)

    def get_max_area(self, other_coords: Iterable[Coord], start: int = 0):
        return max(map(self.get_area, islice(other_coords, start, None)))
