from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import islice

from common.FileReader import CordParser
from common.Utils import timer


@timer
def main(cls):
    # input_coords = CordParser().read_file("./test_input.txt")
    input_coords = CordParser().read_file("./input.txt")
    print(cls.run(input_coords))


@dataclass(frozen=True)
class Coord:
    x: int
    y: int

    def get_area(self, other_coord: Coord) -> int:
        return (abs(self.x - other_coord.x) + 1) * (abs(self.y - other_coord.y) + 1)

    def get_max_area(self, other_coords: Iterable[Coord], start: int = 0):
        return max(map(self.get_area, islice(other_coords, start, None)))

    def get_rec_coords(self, other: Coord) -> tuple[Coord, Coord, Coord, Coord]:
        x1, y1 = self.x, self.y
        x2, y2 = other.x, other.y

        min_x = x1 if x1 < x2 else x2
        max_x = x2 if x1 < x2 else x1
        min_y = y1 if y1 < y2 else y2
        max_y = y2 if y1 < y2 else y1

        return (
            Coord(min_x, min_y),
            Coord(max_x, min_y),
            Coord(max_x, max_y),
            Coord(min_x, max_y),
        )

    def distance_to(self, other_coord: Coord) -> int:
        return abs(self.x - other_coord.x) + abs(self.y - other_coord.y)
