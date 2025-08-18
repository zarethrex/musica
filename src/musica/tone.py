"""Defines classes relating to musical tonality."""

import dataclasses
from typing import Literal, Self, Iterable
from musica.custom_types import CyclicList

CHROMATIC_SCALE = CyclicList(
    "A",
    "A#",
    "B",
    "C",
    "C#",
    "D",
    "Eb",
    "E",
    "F",
    "F#",
    "G",
    "G#",
)

MAJOR_INTERVAL = CyclicList(2, 2, 1, 2, 2, 2, 1)
BLUES_INTERVAL = CyclicList(3, 2, 1, 1, 3, 2)


class Chord:
    def __init__(
        self,
        triad: tuple["Note", "Note", "Note"],
        chord_type: Literal["maj", "min", "dim"] | None = None,
    ):
        self.name = f"{triad[0]}{chord_type or ''}"
        self.triad = triad

    def __getitem__(self, index: int) -> "Note":
        return self.triad[index]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Chord(name={self.name}, triad={[str(n) for n in self.triad]})"


@dataclasses.dataclass
class Note:
    label: str

    def diminish(self) -> Self:
        _scale = self.chromatic_scale.copy(reverse=True)
        next(_scale)
        return next(_scale)

    def augment(self) -> Self:
        _scale = self.chromatic_scale
        next(_scale)
        return next(_scale)

    def __str__(self) -> str:
        return self.label

    def _triad(
        self, scale_generator: Iterable[Self], label: Literal["maj", "min", "dim"]
    ) -> Chord:
        _output: list[Note] = []
        _output.append(next(scale_generator))
        next(scale_generator)
        _output.append(next(scale_generator))
        next(scale_generator)
        _output.append(next(scale_generator))
        return Chord(_output, label)

    @property
    def major_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(intervals=MAJOR_INTERVAL[:-1])

    @property
    def dorian_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=1)[:-1]
        )

    @property
    def phrygian_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=2)[:-1]
        )

    @property
    def lydian_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=3)[:-1]
        )

    @property
    def mixolydian_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=4)[:-1]
        )

    @property
    def minor_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=5)[:-1]
        )

    @property
    def ionian_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=6)[:-1]
        )

    @property
    def dominant(self) -> Self:
        return self.major_scale[4]

    @property
    def secondary_dominant(self) -> Self:
        return self.dominant.dominant

    @property
    def aeolian_scale(self) -> Iterable[Self]:
        return self.minor_scale

    @property
    def relative_minor(self) -> Self:
        return self.major_scale[5]

    @property
    def major_triad(self) -> tuple[Self, Self, Self]:
        return self._triad(self.major_scale, "maj")

    @property
    def minor_triad(self) -> tuple[Self, Self, Self]:
        return self._triad(self.minor_scale, "min")

    @property
    def diminished_triad(self) -> tuple[Self, Self, Self]:
        return self._triad(self.ionian_scale, "dim")

    @property
    def blues_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(intervals=BLUES_INTERVAL[:-1])

    @property
    def index(self) -> int:
        return CHROMATIC_SCALE.index(self.label)

    @property
    def chromatic_scale(self) -> CyclicList:
        return CHROMATIC_SCALE.map(Note).copy(start_index=self.index)

    @property
    def major_chords(self) -> CyclicList:
        def _compare(other: Note, this: Note = self) -> tuple[Note, Note, Note]:
            _triad_self = this.major_triad
            _triad_other = other.major_triad
            _triad_other_minor = other.minor_triad
            if _triad_other[1].diminish() not in this.major_scale:
                return other.major_triad
            if (
                _triad_other[1].diminish() in this.major_scale
                and _triad_other[2].diminish() in this.major_scale
            ):
                return other.diminished_triad
            return other.minor_triad

        for note in Note("C").major_scale:
            yield _compare(note)


def circle_of_fifths() -> str:
    _print_format = """
                {o[0]:^2}
        {o[11]:^2}              {o[1]:^2}
                {i[0]:^2}
           {i[11]:^2}        {i[1]:^2}
    {o[10]:^2}                       {o[2]:^2}
        {i[10]:^2}               {i[2]:^2}
    
  {o[9]:^2}   {i[9]:^2}                 {i[3]:^2}   {o[3]:^2}
    
        {i[8]:^2}               {i[4]:^2}
   {o[8]:^2}                        {o[4]:^2} 
          {i[7]:^2}         {i[5]:^2}
                {i[6]:^2}
       {o[7]:^2}                {o[5]:^2}
                {o[6]:^2} 
    """
    _outer_start: str = "C"
    _inner_start: str = "A"
    _iterable_outer = Note(_outer_start)
    _iterable_inner = Note(_inner_start)
    _outer_list: list[Note] = [f"{str(_iterable_outer):^2}"]
    _inner_list: list[Note] = [f"{str(_iterable_inner):^2}"]
    _iterable_outer = _iterable_outer.major_triad[2]
    _iterable_inner = _iterable_inner.major_triad[2]

    while _outer_start != _iterable_outer.label:
        _outer_list.append(f"{str(_iterable_outer):^2}")
        _inner_list.append(f"{str(_iterable_inner):^2}")
        _iterable_outer = _iterable_outer.major_triad[2]
        _iterable_inner = _iterable_inner.major_triad[2]

    return _print_format.format(o=_outer_list, i=_inner_list)


if __name__ in "__main__":
    print(list(Note("C").major_chords))
    print(list(Note("A").major_chords))
