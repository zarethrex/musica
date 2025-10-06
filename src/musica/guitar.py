"""Methods and Classes specific to Guitar theory."""

from __future__ import annotations

import typing
import dataclasses
from musica.tone import CHROMATIC_SCALE, Chord, Note, CyclicList

N = typing.TypeVar("N", bound=Note)
S = typing.TypeVar("S", bound="String[Note]")


class String(CyclicList[N]):
    def __init__(self, n_frets: int, *args, **kwargs) -> None:
        kwargs.pop("limit", None)
        super().__init__(*CHROMATIC_SCALE.values, limit=n_frets, **kwargs)


class Tuning(typing.Generic[S]):
    def __init__(self, n_strings: int, n_frets: int) -> None:
        self._strings: list[String[Note]] = list(
            String(n_frets=n_frets) for _ in range(n_strings)
        )

    def tune(self, string_index: int, base_note: str) -> None:
        _index = self._strings[string_index].values.index(base_note)
        self._strings[string_index] = self._strings[string_index].copy(
            start_index=_index
        )

    def __getitem__(self, index: int) -> String[Note]:
        return self._strings[index]

    @classmethod
    def from_notes(
        cls, *base_notes: str, n_frets: int, n_strings: int = 6
    ) -> typing.Self:
        _tuning = cls(n_strings=n_strings, n_frets=n_frets)
        for label, string_index in zip(
            base_notes, range(len(_tuning._strings)), strict=True
        ):
            _tuning.tune(string_index, label)
        return _tuning

    @property
    def base_notes(self) -> tuple[str, ...]:
        return tuple(string[string._start_index] for string in self._strings)

    @property
    def strings(self) -> list[String[Note]]:
        return self._strings


STANDARD_TUNING: Tuning[String[Note]] = Tuning.from_notes(
    "E", "A", "D", "G", "B", "E", n_frets=22
)


class Guitar:
    _tuning: Tuning[String[Note]] = STANDARD_TUNING

    def strum(self, finger_position: tuple[int, ...] | None) -> tuple[str, ...]:
        finger_position = finger_position or tuple([0] * len(self._tuning.strings))
        _notes = [
            string[finger_position[i]] if finger_position[i] is not None else None
            for i, string in zip(
                range(len(finger_position)), self._tuning.strings, strict=False
            )
        ]
        _chord = Chord(tuple(Note(note) for note in _notes if note))
        _chord.play()
        return _notes


if __name__ in "__main__":
    print(Guitar().strum((None, 1, 2, 3, 4, 1)))
