"""Lossless, counted partitioning shared by source and graph traversal."""
from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar('T')


def counted_windows(values: Sequence[T], measure: Callable[[tuple[T, ...]], int],
                    bound: int, refuse: Callable[[], None]) -> list[tuple[T, ...]]:
    """Keep every record in order; indivisible oversize records explicitly refuse."""
    values = tuple(values)
    if not values:
        return []
    if measure(values) <= bound:
        return [values]
    if len(values) == 1:
        refuse()
        raise ValueError('oversized evidence record')
    middle = len(values) // 2
    return (counted_windows(values[:middle], measure, bound, refuse) +
            counted_windows(values[middle:], measure, bound, refuse))
