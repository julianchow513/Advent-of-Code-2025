import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Iterable, Union

Number = Union[int, float]


class MultiThreadSum:
    def __init__(self, max_workers=os.cpu_count()) -> None:
        self.max_workers = max_workers

    def exec(
        self,
        function: Callable[..., Number],
        iterable: Iterable[Any],
        *args: Any,
        **kwargs: Any
    ) -> Number:
        total: float = 0.0
        with ThreadPoolExecutor(max_workers=self.max_workers) as tpe:
            futures = [tpe.submit(function, item, *args, **kwargs) for item in iterable]

        total += sum(f.result() for f in futures)

        return total


class MultiThreadChunk:
    def __init__(self, max_workers=os.cpu_count()) -> None:
        self.max_workers = max_workers

    def exec(
        self,
        function: Callable[..., Number],
        iterable: Iterable[Any],
        *args: Any,
        **kwargs: Any
    ):
        pass
