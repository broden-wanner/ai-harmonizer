import pytest
from csp import no_parallel_fifths, no_parallel_octaves
from music21.note import Note


class TestParallelFifths:
    def test_no_parallel_fiths_false(self):
        s1 = Note('C5')
        s2 = Note('D5')
        a1 = Note('F4')
        a2 = Note('G4')
        t1 = Note('C4')
        t2 = Note('D4')
        b1 = Note('C3')
        b2 = Note('D3')
        assert not no_parallel_fifths(s1, a1, t1, b1, s2, a2, t2, b2)

    def test_no_parallel_fiths_true(self):
        s1 = Note('C5')
        s2 = Note('D5')
        a1 = Note('F4')
        a2 = Note('C4')
        assert no_parallel_fifths(s1, a1, s2, a2)


class TestParallelOctaves:
    def test_no_parallel_octaves_false(self):
        s1 = Note('C5')
        s2 = Note('D5')
        a1 = Note('F4')
        a2 = Note('G4')
        t1 = Note('C4')
        t2 = Note('D4')
        b1 = Note('C3')
        b2 = Note('D3')
        assert not no_parallel_octaves(s1, a1, t1, b1, s2, a2, t2, b2)

    def test_no_parallel_octaves_true(self):
        s1 = Note('C5')
        s2 = Note('D5')
        a1 = Note('F4')
        a2 = Note('G4')
        t1 = Note('C4')
        t2 = Note('E4')
        b1 = Note('C3')
        b2 = Note('F3')
        assert no_parallel_octaves(s1, a1, t1, b1, s2, a2, t2, b2)

    def test_no_parallel_octaves_same_note(self):
        s1 = Note('C5')
        s2 = Note('C5')
        a1 = Note('C4')
        a2 = Note('C4')
        assert no_parallel_octaves(s1, a1, s2, a2)
