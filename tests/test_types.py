from musica.custom_types import CyclicList


def test_cyclic_behaviour() -> None:
    _list = list(range(10))
    _fifth = _list[4]
    _cycles = 10
    _counter = 0

    for i in CyclicList(*_list, counts=_cycles):
        if i == _fifth:
            _counter += 1

    assert _counter == _cycles, f"{_counter} != {_cycles}"


def test_indexing() -> None:
    _list = list(range(10))
    _cycle = CyclicList(*_list, counts=10)
    _counters = {}

    for i, value in enumerate(_cycle):
        _counters.setdefault(_list[i % len(_list)], 0)
        assert _list[i % len(_list)] == value
        _counters[_list[i % len(_list)]] += 1

    assert all(total == 10 for total in _counters.values())


def test_stepped() -> None:
    _list = list(range(10))
    _stepped = list(range(0, 10, 3))
    _cyclic = CyclicList(*range(10)).custom_iter(step=3)

    for i, (c, l) in enumerate(zip(_cyclic, _stepped)):
        assert c == l, f"[{i}] {c} != {l}"


def test_intervals() -> None:
    _list = list(range(10))
    _intervals: list[int] = [1, 2, 3, 3]
    _expected: list[int] = [0, 1, 3, 6, 9]
    _cyclic = CyclicList(*_list).custom_iter(intervals=_intervals)

    for i, (c, l) in enumerate(zip(_cyclic, _expected)):
        assert c == l, f"[{i}] {c} != {l}"
