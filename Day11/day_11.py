from Parser import ServerConnectionParser
from common.Utils import main


class AllPathFinder:
    START: str = "you"
    TARGET: str = "out"

    @classmethod
    def run(cls, conns: dict[str, tuple[str]]) -> int:
        return cls._get_all_path_counter(conns, cls.START)

    @classmethod
    def _get_all_path_counter(cls, conns: dict[str, tuple[str]], server: str) -> int:
        if server == cls.TARGET:
            return 1

        return sum(
            cls._get_all_path_counter(conns, sev) for sev in conns.get(server, tuple())
        )


if __name__ == "__main__":
    main(ServerConnectionParser, AllPathFinder, test=False)
