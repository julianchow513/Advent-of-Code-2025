from typing import TextIO, Any

from common.FileReader import ParserStrategy


class ServerConnectionParser(ParserStrategy):

    def _parse(self, file: TextIO) -> dict[str, tuple[str]]:
        connection_map = {}

        for raw_line in file:
            line = raw_line.strip()
            server, targets = line.split(":")
            targets = targets.strip().split(" ")
            connection_map[server] = tuple(targets)

        return connection_map
