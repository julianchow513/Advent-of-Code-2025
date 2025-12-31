from __future__ import annotations

import os
from bisect import bisect_right
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from itertools import pairwise
from math import ceil, floor
from threading import Lock

from Utils import Coord, main
from day_9 import MaxAreaCoordFinder


class MaxAreaWithinColourFinder(MaxAreaCoordFinder):

    @staticmethod
    def run(input_list: list[list[int]]) -> int:
        coords = MaxAreaWithinColourFinder._parse_coords(input_list)
        polygon = Polygon(coords)
        return MaxAreaWithinColourFinder._get_max_colour_area(polygon)

    @staticmethod
    def _get_max_colour_area(polygon: Polygon) -> int:
        rectangles = list(polygon.iter_rectangles_largest_to_smallest())
        print(f"Checking {len(rectangles)} possible rectangles...")
        num_threads = min(os.cpu_count(), len(rectangles))

        if num_threads <= 1:
            print("Running single-threaded...")
            for i, (c1, c2) in enumerate(rectangles):
                if i % 1000 == 0:
                    print(f"Checked {i}/{len(rectangles)} rectangles...")
                if polygon.within_area(c1, c2):
                    area = c1.get_area(c2)
                    print(f"Found valid rectangle with area {area}")
                    return area
            print("No valid rectangles found")
            return 0

        chunks = [rectangles[i::num_threads] for i in range(num_threads)]

        largest_area_lock = Lock()
        largest_area = [0]
        checked_count = [0]

        def check_chunk(thread_id, chunk):
            local_checked = 0
            for c1, c2 in chunk:
                current_area = c1.get_area(c2)

                with largest_area_lock:
                    if current_area <= largest_area[0]:
                        print(
                            f"Thread {thread_id}: Early termination (checked {local_checked} rectangles)"
                        )
                        return None

                if polygon.within_area(c1, c2):
                    with largest_area_lock:
                        if current_area > largest_area[0]:
                            largest_area[0] = current_area
                            print(
                                f"Thread {thread_id}: Found valid rectangle with area {current_area}"
                            )
                    return c1, c2

                local_checked += 1
                if local_checked % 500 == 0:
                    with largest_area_lock:
                        checked_count[0] += 500
                        print(
                            f"Progress: {checked_count[0]}/{len(rectangles)} rectangles checked, best area so far: {largest_area[0]}"
                        )

            print(f"Thread {thread_id}: Finished checking {local_checked} rectangles")
            return None

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(check_chunk, i, chunk) for i, chunk in enumerate(chunks)
            ]

            largest_found = None

            for future in futures:
                result = future.result()
                if result is not None:
                    c1, c2 = result
                    area = c1.get_area(c2)
                    if largest_found is None or area > c1.get_area(largest_found[1]):
                        largest_found = result

        if largest_found:
            c1, c2 = largest_found
            final_area = c1.get_area(c2)
            print(f"Final result: Maximum area = {final_area}")
            return final_area
        print("No valid rectangles found")
        return 0


class Polygon:

    def __init__(self, coords: list[Coord]) -> None:
        self.edges = coords
        xs = [p.x for p in coords]
        ys = [p.y for p in coords]
        self.min_x = min(xs)
        self.max_x = max(xs)
        self.min_y = min(ys)
        self.max_y = max(ys)

        self.scanline_cache = ScanLineCache(coords)

        self.valid_tiles = ValidTilesFinder.get_valid_tiles(coords, self.scanline_cache)

        self.danger_zone = DangerZoneFinder.get_danger_zone(self.valid_tiles)
        print(
            f"Valid tiles: {len(self.valid_tiles)}, Danger zone size: {len(self.danger_zone)}"
        )

    def within_area(self, coord1: Coord, coord2: Coord) -> bool:
        rec_coords = coord1.get_rec_coords(coord2)

        if coord1 not in self.edges or coord2 not in self.edges:
            return False

        if not self._all_points_valid(coord1, coord2):
            return False

        return self._edges_in_area(rec_coords)

    def _all_points_valid(self, coord1: Coord, coord2: Coord) -> bool:
        min_x = min(coord1.x, coord2.x)
        max_x = max(coord1.x, coord2.x)
        min_y = min(coord1.y, coord2.y)
        max_y = max(coord1.y, coord2.y)

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                point = Coord(x, y)
                if point not in self.valid_tiles:
                    return False
        return True

    def _edges_in_area(self, rec_coords: tuple[Coord, Coord, Coord, Coord]) -> bool:
        dz = self.danger_zone

        for i in range(4):
            a = rec_coords[i]
            b = rec_coords[(i + 1) % 4]

            for p in Polygon.iter_edge(a, b):
                if p in dz:
                    return False
        return True

    @staticmethod
    def iter_edge(a: Coord, b: Coord):
        dx = b.x - a.x
        dy = b.y - a.y

        if dx != 0 and dy != 0:
            raise ValueError("Rectangle edges must be axis-aligned")

        if dx != 0:
            step = 1 if dx > 0 else -1
            for x in range(a.x, b.x + step, step):
                yield Coord(x, a.y)
        else:
            step = 1 if dy > 0 else -1
            for y in range(a.y, b.y + step, step):
                yield Coord(a.x, y)

    def iter_rectangles_largest_to_smallest(
        self,
    ) -> Iterable[tuple[Coord, Coord]]:
        rect_candidates = []

        for i, v1 in enumerate(self.edges):
            for v2 in self.edges[i + 1 :]:
                area = v1.get_area(v2)
                rect_candidates.append((area, v1, v2))

        rect_candidates.sort(reverse=True, key=lambda t: t[0])

        for _, v1, v2 in rect_candidates:
            yield v1, v2


class ValidTilesFinder:

    @staticmethod
    def get_valid_tiles(
        coords: list[Coord], scanline_cache: ScanLineCache
    ) -> set[Coord]:
        valid_tiles = set()

        valid_tiles.update(coords)

        for i in range(len(coords)):
            v1 = coords[i]
            v2 = coords[(i + 1) % len(coords)]

            for point in Polygon.iter_edge(v1, v2):
                valid_tiles.add(point)

        xs = [c.x for c in coords]
        ys = [c.y for c in coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        for y in range(min_y, max_y + 1):
            intervals = scanline_cache._compute_scanline(y)
            for x1, x2 in intervals:
                for x in range(x1, x2 + 1):
                    valid_tiles.add(Coord(x, y))

        return valid_tiles


class DangerZoneFinder:

    @staticmethod
    def get_danger_zone(valid_tiles: set[Coord]) -> set[Coord]:
        danger_zone = set()
        directions = [
            (dx, dy)
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            if not (dx == 0 and dy == 0)
        ]

        for point in valid_tiles:
            for dx, dy in directions:
                neighbor = Coord(point.x + dx, point.y + dy)
                if neighbor not in valid_tiles:
                    danger_zone.add(neighbor)

        return danger_zone


class ScanLineCache:
    __slots__ = ("_edges", "_cache", "_lock")

    def __init__(self, polygon: list[Coord]):
        self._edges: list[tuple[Coord, Coord]] = list(pairwise(polygon))
        self._cache: dict[int, list[tuple[int, int]]] = {}
        self._lock = Lock()

    def contains(self, coord: Coord) -> bool:
        y = coord.y
        x = coord.x

        intervals = self._cache.get(y)
        if intervals is None:
            intervals = self._compute_scanline(y)

        starts = [i[0] for i in intervals]
        ends = [i[1] for i in intervals]

        idx = bisect_right(starts, x) - 1
        if idx >= 0 and x <= ends[idx]:
            return True
        return False

    def _compute_scanline(self, y: int) -> list[tuple[int, int]]:
        xs: list[float] = []

        for v1, v2 in self._edges:
            y1, y2 = v1.y, v2.y
            if y1 == y2:
                continue
            if (y1 <= y <= y2) or (y2 <= y <= y1):
                x = v1.x + (y - y1) * (v2.x - v1.x) / (y2 - y1)
                xs.append(x)

        if not xs:
            intervals = []
        else:
            xs.sort()
            intervals = []
            it = iter(xs)
            for x1, x2 in zip(it, it):
                intervals.append((ceil(x1), floor(x2)))

        with self._lock:
            self._cache.setdefault(y, intervals)

        return intervals


if __name__ == "__main__":
    main(MaxAreaWithinColourFinder)
