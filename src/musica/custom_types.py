"""Special types."""

import collections.abc

from enum import StrEnum
import enum
import functools
from typing import Callable, TypeVar, Iterator, Generic, Self

T = TypeVar("T")
_UNDEFINED = object()


class CyclicList(collections.abc.Iterable, Generic[T]):
    def __init__(
        self,
        *values: T,
        limit: int | None = _UNDEFINED,
        reverse: bool = False,
        counts: int | None = _UNDEFINED,
        start_index: int | None = None,
    ) -> None:
        if limit and limit is not _UNDEFINED and counts and counts is not _UNDEFINED:
            raise ValueError("Specifying both counts and limit is ambiguous.")
        self._reverse: bool = reverse
        self._values: list[T] = values
        self._limit: int | None = limit
        self._counts: int | None = counts
        self._counter: int = 0
        self._start_index: int = start_index or 0
        self._current_index: int = self._start_index

    def map(self, func: Callable) -> Self:
        return self.copy(*map(func, self._values))

    def copy(self, *args, **kwargs: object) -> Self:
        start_index = kwargs.get("start_index", self._start_index)
        if kwargs.get("reverse"):
            start_index = len(self._values) - start_index - 1
        return self.__class__(
            *(args or self._values),
            limit=kwargs.get("limit", self._limit),
            reverse=kwargs.get("reverse", self._reverse),
            counts=kwargs.get("counts", self._counts),
            start_index=start_index,
        )

    def __iter__(self) -> Iterator[T]:
        return self

    def __getitem__(self, index) -> T | Self:
        if isinstance(index, slice):
            _values: list[int] = []
            _range_args: list[int] = []
            if index.start:
                _range_args.append(self._start_index + index.start)
            else:
                _range_args.append(self._start_index)
            if index.stop and index.stop < 0:
                _range_args.append(len(self._values) + index.stop)
            elif index.stop:
                _range_args.append(index.stop % len(self._values))
            else:
                _range_args.append(len(self._values))
            return self.__class__(
                *[
                    value
                    for value in self.copy(
                        start_index=_range_args[0], limit=_range_args[1]
                    )
                ]
            )

        else:
            if self._reverse:
                index = (len(self._values) - index - 1) % len(self._values)
            else:
                index = index % len(self._values)
            return self._values[index]

    @functools.lru_cache()
    def index(self, value: T) -> int:
        return self._values.index(value)

    def __next__(self) -> T:
        if not self._values:
            raise StopIteration
        _value = self[self._current_index]
        _counts = self._counts
        _limit = self._limit

        if self._counts is _UNDEFINED and self._limit is _UNDEFINED:
            _counts = 1

        self._counter += 1

        if _counts and _counts is not _UNDEFINED:
            _limit = _counts * len(self._values)

        if _limit and _limit is not _UNDEFINED and self._counter > _limit:
            raise StopIteration

        self._current_index = (self._current_index + 1) % len(self._values)

        return _value

    def custom_iter(
        self,
        *,
        intervals: list[int] | None = None,
        step: int | None = None,
        start_index: int | None = None,
        counts: int | None = _UNDEFINED,
        limit: int | None = _UNDEFINED,
    ) -> Iterator[T]:
        _inf_iter = self.copy(limit=None, counts=None)
        _current_value_order: list[T] = [val for val, _ in zip(_inf_iter, self._values)]
        _values = _current_value_order
        if intervals and step:
            raise ValueError("Specifying both intervals and step is ambiguous.")
        if step:
            _values = [
                val for i, val in enumerate(_current_value_order) if i % step == 0
            ]
        if intervals:
            _values = [_current_value_order[0]]
            _index: int = 0
            for interval in intervals:
                _index = (_index + interval) % len(self._values)
                _values.append(_current_value_order[_index])
        return self.copy(*_values, start_index=start_index, counts=counts, limit=limit)


if __name__ in "__main__":
    _list = CyclicList(*range(10), start_index=1)
    print(list(_list))
    print(list(_list.copy(reverse=True)))
