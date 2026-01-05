from functools import lru_cache

from Day11.Parser import ServerConnectionParser
from common.Utils import main


class DACFFTPathFinder:
    START: str = "svr"
    DAC: str = "dac"
    FFT: str = "fft"
    TARGET: str = "out"
    conns: dict[str, tuple[str]]

    @classmethod
    def run(cls, conns: dict[str, tuple[str]]) -> int:
        cls.CONNS = conns
        cls._get_all_path_counter.cache_clear()
        return cls._get_all_path_counter(cls.START, False, False)

    @classmethod
    @lru_cache(maxsize=None)
    def _get_all_path_counter(cls, server: str, dac: bool, fft: bool) -> int:
        if server == cls.TARGET and dac and fft:
            return 1

        dac, fft = dac or server == cls.DAC, fft or server == cls.FFT

        return sum(
            cls._get_all_path_counter(sev, dac, fft)
            for sev in cls.CONNS.get(server, tuple())
        )


if __name__ == "__main__":
    main(ServerConnectionParser, DACFFTPathFinder, test=False)
