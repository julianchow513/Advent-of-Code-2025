from typing import TextIO

from common.FileReader import ParserStrategy


class Indicator:
    __slots__ = ("_bits", "_max_bit")

    def __init__(self, size: int, flip_idx: list[int] = None):
        self._max_bit = size - 1
        if flip_idx is None:
            self._bits = 0
        else:
            bits = 0
            for idx in flip_idx:
                if idx <= self._max_bit:
                    bits |= 1 << idx
            self._bits = bits

    def flip(self, i: int) -> None:
        if i > self._max_bit:
            return
        self._bits ^= 1 << i

    def press_button(self, button: Button) -> Indicator:
        new_indicator = object.__new__(Indicator)
        new_indicator._max_bit = self._max_bit
        new_indicator._bits = self._bits ^ button.bits
        return new_indicator

    def __eq__(self, other) -> bool:
        return (
            type(other) is Indicator
            and self._bits == other._bits
            and self._max_bit == other._max_bit
        )

    def __hash__(self) -> int:
        return hash((self._bits, self._max_bit))

    def get_size(self):
        return self._max_bit + 1

    def all_false(self) -> bool:
        return self._bits == 0


class Button:
    __slots__ = ("bits",)

    def __init__(self, flip_idx: list[int], max_bit: int | None = None) -> None:
        bits = 0
        if max_bit is None:
            if flip_idx:
                max_bit = max(flip_idx)
            else:
                max_bit = -1
        for idx in flip_idx:
            if 0 <= idx <= max_bit:
                bits |= 1 << idx
        self.bits = bits


class CounterParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[tuple[list[list[int]], list[int]]]:
        problems = []

        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue

            counter, buttons = CounterParser._parse_line(line)
            n_buttons = len(buttons)
            m_counter = len(counter)

            A = [[0 for _ in range(n_buttons)] for _ in range(m_counter)]
            for j, b in enumerate(buttons):
                for idx in b:
                    if idx < m_counter:
                        A[idx][j] = 1
                    else:
                        raise ValueError(
                            f"Button index {idx} out of bounds for counter length {m_counter}"
                        )

            T = [int(x) for x in counter]

            problems.append((A, T))

        return problems

    @staticmethod
    def _parse_line(line: str):
        i = 0
        counter = None
        buttons = []

        while i < len(line):
            cur_char = line[i]
            if cur_char == "(":
                i, nums = CounterParser._parse_numbers(line, i, ")")
                buttons.append(nums)
            elif cur_char == "{":
                i, nums = CounterParser._parse_numbers(line, i, "}")
                counter = nums
            i += 1

        if counter is None:
            raise ValueError(f"No counter found in line: {line}")

        return counter, buttons

    @staticmethod
    def _parse_numbers(line: str, i: int, end_char: str):
        end_idx = line.index(end_char, i)
        numbers_str = line[i + 1 : end_idx].split(",")
        numbers = [int(n.strip()) for n in numbers_str if n.strip()]
        return end_idx, numbers


class LightsParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[tuple[Indicator, list[Button]]]:
        res = []
        for raw_line in file:
            line = raw_line.strip()
            res.append(self._parse_line(line))
        return res

    @staticmethod
    def _parse_line(line: str) -> tuple[Indicator, list[Button]]:
        i = 0
        indicator = None
        buttons = []

        while i < len(line):
            cur_char = line[i]
            if cur_char == "[":
                i, indicator = LightsParser._parse_indicator(line, i)
            elif cur_char == "(":
                i, button = LightsParser._parse_button(line, i)
                buttons.append(button)
            i += 1

        return indicator, buttons

    @staticmethod
    def _parse_sequence(
        line: str, start_idx: int, close_char: str, match_fn
    ) -> tuple[int, list[int]]:
        indices = []

        for idx in range(start_idx + 1, len(line)):
            cur_char = line[idx]
            if cur_char == close_char:
                return idx, indices
            elif match_fn(cur_char):
                indices.append(idx - start_idx - 1)

        raise ValueError(f"No closing {close_char} found in line")

    @staticmethod
    def _parse_indicator(line: str, i: int) -> tuple[int, Indicator]:
        idx, indices = LightsParser._parse_sequence(line, i, "]", lambda c: c == "#")
        indicator_size = idx - i - 1
        return idx, Indicator(indicator_size, indices)

    @staticmethod
    def _parse_button(line: str, i: int) -> tuple[int, Button]:
        end_idx = line.index(")", i)
        numbers_str = line[i + 1 : end_idx].split(",")
        flip_idx = [int(n) for n in numbers_str if n.strip()]
        return end_idx, Button(flip_idx)
