from Utils import Coord, main


class MaxAreaCoordFinder:

    @classmethod
    def find_max_area(cls, input_list: list[list[int]]) -> int:
        coords = cls._parse_coords(input_list)
        return cls._get_max_area(coords)

    @staticmethod
    def _parse_coords(input_list: list[list[int]]) -> list[Coord]:
        return [Coord(x, y) for x, y in input_list]

    @staticmethod
    def _get_max_area(coords: list[Coord]) -> int:
        max_area = 0

        for i in range(len(coords) - 1):
            cur_coord = coords[i]
            max_area = max(max_area, cur_coord.get_max_area(coords, start=i + 1))

        return max_area


if __name__ == "__main__":
    main(MaxAreaCoordFinder)
