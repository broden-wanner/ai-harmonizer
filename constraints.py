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


def all_notes_different_one_beat(*notes) -> bool:
    """Asserts that all the notes in each part are different on one beat.
    
    Args:
        notes: A tuple of notes on one beat in each part.
    """
    return len(notes) == len(set(notes))


# TODO: Fix this constraint
def maximum_two_same_note_name(*notes) -> bool:
    """Asserts that all the notes in each part are different on one beat.
    
    Args:
        notes: A tuple of notes on one beat in each part.
    """
    name_dict = {}
    for n in notes:
        if n.name in name_dict:
            name_dict[n.name] += 1
        else:
            name_dict[n.name] = 1
    for n in name_dict:
        if name_dict[n] > 1:
            return False
    return True


def assert_is_pac(key):
    """ Asserts that the two beats are a PAC.

    Requirements for a PAC
        - First chord is root position V
        - Second chord is root position I
        - Top voice is tonic in second chord
    
    Args:
        notes: A tuple of notes formatted like (s1, a1, t1, b1, s2, a2, t2, b2)
            in all parts
    """
    def is_pac(*notes) -> bool:
        notes1 = notes[:len(notes) // 2]
        notes2 = notes[len(notes) // 2:]
        b1 = notes1[-1]
        b2 = notes2[-1]
        s1 = notes1[0]
        s2 = notes2[0]
        tonic = key.tonic.name
        # Check for correct notes in bottom and top
        if b2.name != tonic or s2.name != tonic:
            return False

        # Check for correct chord types
        c1 = Chord(notes1)
        c2 = Chord(notes2)
        rn1 = romanNumeralFromChord(c1, key)
        rn2 = romanNumeralFromChord(c2, key)
        if rn1.figure != 'V' and rn1.figure != 'V7':
            return False
        if rn2.figure != 'I' and rn2.figure != 'i':
            return False

        return True

    return is_pac