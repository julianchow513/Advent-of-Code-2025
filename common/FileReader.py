import csv
import logging
from abc import ABC, abstractmethod
from typing import Any, TextIO
from pathlib import Path

logger = logging.getLogger(__name__)


class ParserStrategy(ABC):

    def read_file(self, file_path: str) -> Any:
        try:
            file_path = Path(file_path)
            with open(file_path, "r") as file:
                return self._parse(file)
        except FileNotFoundError:
            logger.error(f"File {file_path} not found")
            return []

    @abstractmethod
    def _parse(self, file: TextIO) -> Any:
        pass


class LineByLineParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[str]:
        logger.debug("Using LineByLineParser")
        return [line.strip() for line in file]


class CSVParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[list[str]]:
        logger.debug("Using CSVParser")
        return list(csv.reader(file))


class CommaSeparatedStringParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[str]:
        return file.read().split(",")


class IntArrayParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[list[int]]:
        res = []
        for line in file:
            res.append([int(num) for num in line])
        return res


class StrArrayParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[list[str]]:
        res = []
        for line in file:
            res.append(list(line.strip()))
        return res


class TwoPartParser(ParserStrategy):

    def _parse(self, file: TextIO) -> tuple[list[str], list[str]]:
        part1 = []
        part2 = []
        flag = False
        for raw_line in file:
            line = raw_line.strip()
            if not flag and line == "":
                flag = True
                continue
            if not flag:
                part1.append(line)
            else:
                part2.append(line)

        return part1, part2


class CordParser(ParserStrategy):

    def _parse(self, file: TextIO) -> list[list[int]]:
        res = []

        for raw_line in file:
            line = raw_line.strip()
            line_parts = list(map(int, map(str.strip, line.split(","))))
            res.append(line_parts)

        return res
