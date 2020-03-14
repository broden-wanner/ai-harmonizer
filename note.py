class Note:

    def __init__(self, note: str):
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
