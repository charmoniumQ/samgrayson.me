from typing import TypeVar, List, Callable
T = TypeVar("T")

def compose_all(funcs: List[Callable[[T], T]]) -> Callable[[T], T]:
    def func(data: T) -> T:
        for func in funcs:
            data = func(data)
        return data
    return func
