import pytest
from csp import no_parallel_fifths
from music21.note import Note


class TestNoParallelFifths:
    def test_no_parallel_fiths(self):
        s1 = Note('C5')
        s2 = Note('D5')
        a1 = Note('F4')
        a2 = Note('G4')
        t1 = Note('C4')
        t2 = Note('D4')
        b1 = Note('C3')
        b2 = Note('D3')
        assert not no_parallel_fifths(s1, a1, t1, b1, s2, a2, t2, b2)