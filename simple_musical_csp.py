from csp import NaryCSP
from music21.note import Note
from music21.stream import Score, Measure, Part
from music21.chord import Chord
from music21.voiceLeading import VoiceLeadingQuartet
from music21.roman import romanNumeralFromChord


def tessitura(bottom, top):
    """Generate all possible notes between two notes"""
    all_notes = []
    o = bottom.octave
    while o <= top.octave:
        notes = 'ABCDEFG'
        if o == bottom.octave:
            notes = notes[notes.find(bottom.name[0]):]
        elif o == top.octave:
            notes = notes[:notes.find(top.name[0]) + 1]

        for n in notes:
            for acc in ['', '-', '#', '--', '##']:
                all_notes.append(Note(f'{n}{acc}{o}'))
        o += 1
    return all_notes


satb_tessituras = {
    's': tessitura(Note('G4'), Note('A5')),
    'a': tessitura(Note('A4'), Note('C5')),
    't': tessitura(Note('C3'), Note('G4')),
    'b': tessitura(Note('C2'), Note('D4'))
}


class Constraint:
    """
    A Constraint consists of:
    scope    : a tuple of variables
    condition: a function that can applied to a tuple of values
    for the variables.
    """
    def __init__(self, scope, condition):
        self.scope = scope
        self.condition = condition

    def __repr__(self):
        return self.condition.__name__ + str(self.scope)

    def holds(self, assignment):
        """Returns the value of Constraint con evaluated in assignment.

        precondition: all variables are assigned in assignment
        """
        return self.condition(*tuple(assignment[v] for v in self.scope))


def in_numeral(s, a, t, b, numeral, key):
    """Assert that all four voices are within the numeral"""
    c = Chord([s, a, t, b])
    rn = romanNumeralFromChord(c, key)
    return numeral == rn


def no_parallel_fifths(s1, a1, t1, b1, s2, a2, t2, b2):
    """Assert that there are no paralle fifths between all voices"""
    vlq = VoiceLeadingQuartet(s1, s2, a1, a2)
    if vlq.parallelFifth():
        return False


class SimpleHarmonizerCSP:
    def __init__(self, m):
        """Initialize the data structures for the problem"""
        # Create a variable for each note in each part
        self.variables = []
        for p in 'satb':
            for i in range(1, m + 1):
                self.variables.append(f'{p}{i}')

        # Set the domains to the parts' tessituras
        self.domains = {}
        for v in self.variables:
            voice = v[0]
            self.domains[v] = satb_tessituras[voice]

        # Create the constraints

        # Create a stream of four parts
        self.score = Score(id='mainScore')
        sop = Part(id='Soprano')
        alt = Part(id='Alto')
        ten = Part(id='Tenor')
        bas = Part(id='Bass')

        m01 = Measure(number=1)
        sop.append(m01)

        m11 = Measure(number=1)
        alt.append(m11)

        m21 = Measure(number=1)
        ten.append(m21)

        m21 = Measure(number=1)
        m21.append(clef.BassClef())
        bas.append(m21)

        for p in [sop, alt, ten, bas]:
            self.score.insert(0, p)

        self.nassigns = 0

    def __str__(self):
        """String representation of the CSP"""
        return str(self.domains)

    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any."""
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment.
        DO NOT call this if you are changing a variable to a new value;
        just call assign for that."""
        if var in assignment:
            del assignment[var]


if __name__ == '__main__':
    t = tessitura(Note('G4'), Note('G5'))
    print(t)