from music21.chord import Chord
from music21.roman import romanNumeralFromChord
from music21.voiceLeading import VoiceLeadingQuartet
from music21.key import Key


class Constraint:
    """Constraint with a scope of variabes and the function

    Attributes:
        scope: A tuple of variables
        condition: A function that can applied to a tuple of values
            for the variables. It should return a boolean.
    """
    def __init__(self, scope, condition):
        self.scope = scope
        self.condition = condition

    def __repr__(self):
        return self.condition.__name__ + str(self.scope)

    def holds(self, assignment) -> bool:
        """Returns the value of Constraint con evaluated in assignment.

        precondition: all variables are assigned in assignment
        """
        return self.condition(*tuple(assignment[v] for v in self.scope))


def in_numeral(numeral: str, key: Key):
    """Assert that all four voices are within the numeral.
    
    Args:
        numeral: A string of the numeral to adhere the chord to.
        key: The key in which to analyze the numerals.

    Returns:
        A function that tests whether all notes are in the given 
        roman numeral.
    """
    def is_n(*notes) -> bool:
        c = Chord(notes)
        rn = romanNumeralFromChord(c, key)
        return numeral == rn.romanNumeralAlone

    return is_n


def no_parallel_fifths(*notes) -> bool:
    """Assert that there are no parallel fifths between all voices.

    Args:
        notes: A tuple in the form of (s1, a1, t1, b1, s2, a2, t2, b2) where the first
            note voices come first and the second ones last
    """
    notes1 = notes[:len(notes) // 2]
    notes2 = notes[len(notes) // 2:]
    for n1 in range(len(notes1) - 1):
        for n2 in range(len(notes2) - 1):
            if VoiceLeadingQuartet(notes1[n1], notes2[n2], notes1[n1 + 1],
                                   notes2[n2 + 1]).parallelFifth():
                return False
    return True


def no_parallel_octaves(*notes) -> bool:
    """Assert that there are no parallel fifths between all voices

    Args:
        notes: A tuple in the form of (s1, a1, t1, b1, s2, a2, t2, b2) where the first
            note voices come first and the second ones last
    """
    notes1 = notes[:len(notes) // 2]
    notes2 = notes[len(notes) // 2:]
    for n1 in range(len(notes1) - 1):
        for n2 in range(len(notes2) - 1):
            if VoiceLeadingQuartet(notes1[n1], notes2[n2], notes1[n1 + 1],
                                   notes2[n2 + 1]).parallelOctave():
                return False
    return True


def different_notes(n1, n2) -> bool:
    """Assert that the next note is different than the current one in a single part

    Args:
        n1: First note in the part
        n2: Next note in the pat
    """
    return n1 != n2
