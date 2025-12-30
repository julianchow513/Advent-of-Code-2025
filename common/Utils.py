import pprint
import time
from functools import wraps
from typing import Any
from typing import Callable, ParamSpec, TypeVar


def int_list_to_int(int_list: list[int]):
    return int("".join(map(str, int_list)))


def print_array(array: list[list[Any]]):
    pprint.pprint(array)


T = TypeVar("T")
P = ParamSpec("P")


def timer(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()

        duration = end_time - start_time
        print(f"Function '{func.__name__}' took {duration:.4f}s")
        return result

    return wrapper
