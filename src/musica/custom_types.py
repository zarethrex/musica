"""Special types used for defining scales etc."""

import collections.abc

import functools
from typing import Callable, TypeVar, Iterator, Self, overload, Union, Any

T = TypeVar("T")
C = TypeVar("C", bound="CyclicList[Any]")

_UNDEFINED = object()


class CyclicList(collections.abc.Iterable[T]):
    """Provides an infinite iterable allowing the user to repeatedly redraw values."""
    def __init__(
        self,
        *values: T,
        limit: int | None | object = _UNDEFINED,
        reverse: bool = False,
        counts: int | None | object = _UNDEFINED,
        start_index: int | None = None,
    ) -> None:
        """Initialise a new CyclicList using the given values.
        
        Parameters
        ----------
        *values: object
            the objects on which to iterate
        limit : int | None, optional
            the limit in values to be drawn, by default this is one iteration
            setting to 'None' removes the constraint
        reverse : bool, optional
            iterate in reverse, default is False
        counts : int | None, optional
            limit the number of cycles, by default one cycle is performed
            setting to 'None' removes the constraint
        start_index : int | None, optional
            the index to commence iteration from
        """
        if limit and limit is not _UNDEFINED and counts and counts is not _UNDEFINED:
            raise ValueError("Specifying both counts and limit is ambiguous.")
        if not values:
            raise ValueError("Empty list.")
        self._reverse: bool = reverse
        self._values: tuple[T, ...] = values
        self._limit: int | None | object = limit
        self._counts: int | None | object = counts
        self._counter: int = 0
        self._start_index: int = start_index or 0
        self._current_index: int = self._start_index

    def map(self: C, func: Callable[[T], object]) -> "C":
        """Map a function to each element in the iterable and return a new instance."""
        return self.__class__(*map(func, self._values)) 

    def copy(
        self,
        *args: T,
        start_index: int | None = None,
        reverse: bool | None = None,
        limit: int | None = None,
        counts: int | None = None,
    ) -> Self:
        """Create a copy of this iterable with new values.
        
        Parameters
        ----------
        *args
        start_index : int | None, optional
            the start index to iterate from
        reverse : bool | None, optional
            reverse the ordering
        limit : int | None, optional
            the maximum number of elements to yield.
        counts : int | None, optional
            number of iterations to perform

        Returns
        -------
        CyclicList
            a new iterable with these options
        """
        _start_index: int | None = start_index if start_index is not None else self._start_index
        if reverse or (reverse is None and self._reverse):
            _start_index = len(self._values) - _start_index - 1
        return self.__class__(
            *(args or self._values),
            limit=limit or self._limit,
            reverse=reverse if reverse is not None else self._reverse,
            counts=counts or self._counts,
            start_index=_start_index,
        )

    def __iter__(self) -> Iterator[T]:
        """Returns a new iterator from this iterable."""
        return self.copy()
    
    def __str__(self) -> str:
        """String format printing."""
        _out_str: str = (
            f"CyclicList[{type(self._values[0]).__name__}]"
            f"({', '.join(str(i) for i in self._values)}"
        )

        if self._limit:
            return _out_str + f", limit={len(self._values) - 1 if not isinstance(self._limit, int) else self._limit})"
        if self._counts:
            return _out_str + f", counts={1 if not isinstance(self._counts, int) else self._counts})"
        return _out_str + ")"
    
    def __len__(self) -> int | object:
        """Return length of iterable."""
        _length: int = len(self._values)
        if isinstance(self._counts, int):
            return _length * self._counts
        elif isinstance(self._limit, int):
            return self._limit
        return _UNDEFINED

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    def __getitem__(self, index: int | slice) -> T | Self:
        """Retrieve an item either by index or slicing."""
        if isinstance(index, slice):
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
                ],
            )

        else:
            if self._reverse:
                index = (len(self._values) - index - 1) % len(self._values)
            else:
                index = index % len(self._values)
            return self._values[index]
        

    @functools.lru_cache()
    def index(self, value: T) -> int:
        """Retrieve the index of a value in the cyclic list."""
        return self._values.index(value)

    def __next__(self) -> T:
        """Return the next value in the sequence."""
        if not self._values:
            raise StopIteration
        _value: T = self[self._current_index]
        _counts: int | None | object = self._counts
        _limit: int | None | object = self._limit

        if self._counts is _UNDEFINED and self._limit is _UNDEFINED:
            _counts = 1

        self._counter += 1

        if isinstance(_counts, int):
            _limit = _counts * len(self._values)

        if isinstance(_limit, int) and self._counter > _limit:
            raise StopIteration

        self._current_index = (self._current_index + 1) % len(self._values)

        return _value

    def custom_iter(
        self,
        *,
        intervals: Union["CyclicList[int]", list[int], None] = None,
        step: int | None = None,
        start_index: int | None = None,
        counts: int | None = None, 
        limit: int | None = None,
    ) -> Self:
        """Returns a copy of this iteratable with additional configuration.

        If values are unspecified they are copied from the class instance.
        
        Parameters
        ----------
        *_
        intervals : CyclicList[int] | list[int] | None, optional
            if specified, the intervals at which to select values.
        step : int | None, optional
            if specified, the step size (constant intervals).
        start_index : int | None, optional
            the start index to iterate from
        counts : int | None, optional
            number of iterations to perform
        limit : int | None, optional
            the maximum number of elements to yield.

        Returns
        -------
        CyclicList[T]
            new cyclic list
        """
        _inf_iter = self.copy(limit=None, counts=None)
        _current_value_order: list[T] = [val for val, _ in zip(_inf_iter, self._values)]
        _values = _current_value_order
        if intervals is not None and step is not None:
            raise ValueError("Specifying both intervals and step is ambiguous.")
        if step:
            _values = [
                val for i, val in enumerate(_current_value_order) if i % step == 0
            ]
        if isinstance(intervals, (list, CyclicList)):
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
