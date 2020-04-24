import re
from interval import Interval


class Note:

    def __init__(self, note: str):
        if not isinstance(note, str):
            raise ValueError('Note must be a string')

        if not re.match(r'^[A-G][#b]?[0-8]$', note):
            raise ValueError('Note must match regex ^[A-G][#b]?[0-8]$')

        self.note = note[:-1]
        self.octave = int(note[-1])

    def __eq__(self, other) -> bool:
        if isinstance(other, Note):
            return self.note == other.note and self.octave == other.octave
        return False

    def __str__(self) -> str:
        return f'Note({self.note}{self.octave})'

    def __repr__(self) -> str:
        return f'Note({self.note}{self.octave})'

    def __add__(self, other):
        pass

    def __sub__(self, other) -> Interval:
        # n1 - n2

        # Handle size
        n1 = ord(self.note[0])
        n2 = ord(other.note[0])

        if other.octave > self.octave or n2 > n1:
            raise ValueError(f'Invalid subtraction between {self} and {other}')

        size = 7 * (self.octave - other.octave)
        size += (n1 - n2) + 1

        # Handle quality
        acc1 = self.note[1] if len(self.note) > 1 else ''
        acc2 = self.note[1] if len(other.note) > 1 else ''

        return Interval(quality='P', size=size)

    @staticmethod
    def to_num(note, octave) -> int:
        half_steps = {
            'A': 0,
            'A#': 1,
            'Bb': 1,
            'B': 2,
            'C': 3,
            'D': 5,
            'E': 7,
            'F': 8,
            'G': 10
        }
        return octave * 12 + half_steps[note]
