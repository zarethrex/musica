"""Defines classes relating to musical tonality."""

import dataclasses
import time
import functools
import platform
import pygame.midi

from typing import Literal, Self, Iterable, Generator, cast
from musica.custom_types import CyclicList

CHROMATIC_SCALE = CyclicList(
    "C",
    "C#",
    "D",
    "Eb",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
)

MAJOR_INTERVAL = CyclicList(2, 2, 1, 2, 2, 2, 1)
BLUES_INTERVAL = CyclicList(3, 2, 1, 1, 3, 2)


@functools.lru_cache
def get_audio_driver() -> pygame.midi.Output:
    """Retrieve MIDI Output device."""
    pygame.midi.init()
    _device_map: dict[str, str] = {
        "Windows": "Microsoft GS Wavetable Synth",
        "Linux": "Midi Through",
    }
    _device_name: str = _device_map[platform.system()]
    for i in range(pygame.midi.get_count()):
        info = pygame.midi.get_device_info(i)
        _, name, __, output, *___ = info
        if output and _device_name in name.decode():
            return pygame.midi.Output(i)
    return pygame.midi.Output(0)


class Chord:
    def __init__(
        self,
        notes: tuple["Note", ...],
        chord_suffix: str | None = None,
    ):
        self.name = f"{notes[0]}{chord_suffix or ''}"
        self.notes = notes

    def play(self, duration: int = 1, loudness_percent: int = 100) -> None:
        _player = get_audio_driver()
        _velocity = loudness_percent * 127 // 100
        for note in self.notes:
            _player.note_on(note.note_index, _velocity)
        time.sleep(duration)
        _player.note_off(100)

    def __getitem__(self, index: int) -> "Note":
        return self.notes[index]

    def __str__(self) -> str:
        return f"Chord(self.name, [{', '.join(str(n) for n in self.notes)}])"

    def __repr__(self) -> str:
        return f"Chord(name={self.name}, triad={[str(n) for n in self.notes]})"


@dataclasses.dataclass
class Note:
    label: str
    octave: int = 4

    def diminish(self) -> Self:
        _scale = self.chromatic_scale.copy(reverse=True)
        next(_scale)
        return next(_scale)

    def augment(self) -> Self:
        _scale = self.chromatic_scale
        next(_scale)
        return next(_scale)

    def __str__(self) -> str:
        return f"{self.label}{self.octave}"

    def _make_chord(
        self,
        scale_generator: CyclicList[Self],
        label: Literal["maj", "min", "dim"],
        size: int = 3,
        rank: int | None = None,
    ) -> Chord:
        _output: list[Note] = []
        _next_item: Self = next(scale_generator)
        _output.append(_next_item)

        for _ in range(size - 1):
            next(scale_generator)
            _output.append(next(scale_generator))
        _chord = cast(tuple[Note, Note, Note], _output)
        return Chord(_chord, f"{label}{str(rank) if rank else ''}")

    @property
    def note_index(self) -> int:
        return 12 * (self.octave + 1) + CHROMATIC_SCALE.index(self.label)

    def play(self, duration: int = 1, loudness_percent: int = 100) -> None:
        _velocity = loudness_percent * 127 // 100
        _player = get_audio_driver()
        _player.note_on(self.note_index, _velocity)
        time.sleep(duration)
        _player.note_off(100)

    @property
    def major_scale(self) -> CyclicList[Self]:
        return self.chromatic_scale.custom_iter(intervals=MAJOR_INTERVAL[:-1])

    @property
    def dorian_scale(self) -> CyclicList[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=1)[:-1]
        )

    @property
    def phrygian_scale(self) -> CyclicList[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=2)[:-1]
        )

    @property
    def lydian_scale(self) -> CyclicList[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=3)[:-1]
        )

    @property
    def mixolydian_scale(self) -> CyclicList[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=4)[:-1]
        )

    @property
    def minor_scale(self) -> CyclicList[Self]:
        return self.chromatic_scale.custom_iter(
            intervals=MAJOR_INTERVAL.copy(start_index=5)[:-1]
        )

    @property
    def ionian_scale(self) -> CyclicList[Self]:
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
    def major_triad(self) -> Chord:
        return self._make_chord(self.major_scale, "maj")

    @property
    def minor_triad(self) -> Chord:
        return self._make_chord(self.minor_scale, "min")

    @property
    def major_seventh(self) -> Chord:
        return self._make_chord(self.major_scale, label="maj", size=4, rank=7)

    @property
    def minor_seventh(self) -> Chord:
        return self._make_chord(self.minor_scale, label="min", size=4, rank=7)

    @property
    def diminished_triad(self) -> Chord:
        return self._make_chord(self.ionian_scale, "dim")

    @property
    def blues_scale(self) -> Iterable[Self]:
        return self.chromatic_scale.custom_iter(intervals=BLUES_INTERVAL[:-1])

    @property
    def index(self) -> int:
        return CHROMATIC_SCALE.index(self.label)

    @property
    def chromatic_scale(self) -> CyclicList[Self]:
        return CyclicList(
            *(self.__class__(n) for n in CHROMATIC_SCALE), start_index=self.index
        )

    @property
    def major_triads(self) -> Generator[Chord, None, None]:
        def _compare(other: Note, this: Note = self) -> Chord:
            _triad_other = other.major_triad
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
    _outer_list: list[str] = [f"{str(_iterable_outer):^2}"]
    _inner_list: list[str] = [f"{str(_iterable_inner):^2}"]
    _iterable_outer = _iterable_outer.major_triad[2]
    _iterable_inner = _iterable_inner.major_triad[2]

    while _outer_start != _iterable_outer.label:
        _outer_list.append(f"{str(_iterable_outer):^2}")
        _inner_list.append(f"{str(_iterable_inner):^2}")
        _iterable_outer = _iterable_outer.major_triad[2]
        _iterable_inner = _iterable_inner.major_triad[2]

    return _print_format.format(o=_outer_list, i=_inner_list)


if __name__ in "__main__":
    print(Note("C").minor_seventh)
