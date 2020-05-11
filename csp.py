from music21.note import Note
from music21.stream import Score, Measure, Part
from music21.chord import Chord
from music21.voiceLeading import VoiceLeadingQuartet
from music21.roman import romanNumeralFromChord, RomanNumeral
from music21.clef import BassClef, TrebleClef
from music21.key import Key
from constraints import *

Note.__hash__ = lambda self: hash(self.nameWithOctave)
# ^ Add hash function to Note


def tessitura(bottom: Note, top: Note, key=Key('C')):
    """Generate all possible notes between two notes (inclusive) in a given key"""
    all_notes = []
    o = bottom.octave
    while o <= top.octave:
        notes = 'CDEFGAB'
        if o == bottom.octave:
            notes = notes[notes.find(bottom.name[0]):]
        if o == top.octave:
            notes = notes[:notes.find(top.name[0]) + 1]

        for n_char in notes:
            n = Note(f'{n_char}{o}')
            n.pitch.accidental = key.accidentalByStep(n.pitch.step)
            all_notes.append(n)
        o += 1
    return all_notes


def notes_from_roman(bottom, top, rn):
    """Generate all possible not for a range that are in a roman numeral"""
    possible_notes = []
    for pitch in rn.pitches:
        possible_notes.append(pitch.name)

    all_notes = []
    octave = bottom.octave
    while octave <= top.octave:
        for n in possible_notes:
            actual_note = Note(f'{n}{octave}')
            if bottom <= actual_note and actual_note <= top:
                all_notes.append(actual_note)
        octave += 1

    return all_notes


class NaryCSP:
    """An abstract class for an n-ary CSP

    Attributes:
        variables: The file location of the spreadsheet
        domains: A dictionary that maps variables to their domains
        constraints: A list of constraints
        variables_to_constraints: A dictionary that maps variables to the 
            set of contstraints that they're involved in
    """
    def __init__(self, domains, constraints):
        """Initialize the CSP

        Args:
            domains: A {variable : domain} dictionary
            constraints: A list of constraints
        """
        self.variables = set(domains)
        self.domains = domains
        self.constraints = constraints
        self.var_to_const = {var: set() for var in self.variables}
        for con in constraints:
            for var in con.scope:
                self.var_to_const[var].add(con)


class SimpleHarmonizerCSP(NaryCSP):
    """Creates a simple harmonizer CSP

    Modeled after the N-ary CSP in Russell. Each constraint can have 
    any number of variables involved in in it.

    Attributes:
        name: The name of the CSP
        notes: The number of notes in the CSP
        key: The key in which the piece will be (must be a KeySignature object)
        ranges: A dictionary mapping a part to a tuple of the range of the part. Different
            from tessituras since tessituras enumerates every note in the range
        tessituras: A dictionary mapping the parts to their ranges, which is 
            a list of all possible notes the part can use
        variables: A string list of all variables in the CSP (one per note)
        domains: A dictionary that maps variables to their domains
        constraints: A list of constraints
        variables_to_constraints: A dictionary that maps variables to the 
            set of contstraints that they're involved in
        parts: A dictionary of that maps parts ('s', 'a', 't', or 'b') to
            a list of the variables in that part
    """
    def __init__(self,
                 name: str,
                 notes: int,
                 numerals: list,
                 part_list=['s', 'a', 't', 'b'],
                 ranges=None,
                 use_tessituras=False,
                 key=Key('C')):
        """Initialize the data structures for the problem
        
        Args:
            name: Name for the CSP
            notes: Number of notes for the CSP
            list: A list of all numerals (as strings) to be used in the constraints. The
                length must be equal to the number of notes.
            part_list: A list of the parts for the CSP. Can contain
                's' (soprano), 'a' (alto), 't' (tenor), or 'b' (bass)
            ranges: A dictionary mapping parts to a tuple of their range.
                It is used for the domains of each variables. If not specified,
                then the default satb_tessituras are used.
            key: The key we would like the piece to be in. It is C Major 
                by default.
        """
        self.name = name
        self.notes = notes
        if len(numerals) != notes:
            raise Exception(
                'Number of numerals must equal the number of notes')
        self.numerals = numerals
        self.key = key

        # Set the ranges and tessituras (if needed) for the domains later on
        self.ranges = {}
        self.tessituras = {}
        if not ranges:
            # These are the default ranges and tessituras for SATB
            self.ranges = {
                's': (Note('G4'), Note('G5')),
                'a': (Note('C4'), Note('C5')),
                't': (Note('G3'), Note('G4')),
                'b': (Note('C3'), Note('C4'))
            }
            self.tessituras = {
                's': tessitura(*self.ranges['s'], key=key),
                'a': tessitura(*self.ranges['a'], key=key),
                't': tessitura(*self.ranges['t'], key=key),
                'b': tessitura(*self.ranges['b'], key=key)
            }
        else:
            self.ranges = ranges
            for p in ranges.keys():
                self.tessituras[p] = tessitura(*self.ranges[p], key=key)

        # Create a variable for each note in each part
        self.variables = []
        self.parts = {}
        for p in part_list:
            self.parts[p] = []
            # Add a variable for each of the m notes
            for i in range(1, notes + 1):
                var_name = f'{p}{i}'
                self.variables.append(var_name)
                self.parts[p].append(var_name)

        # Set the domains to the parts' tessituras if desired
        # Otherwise, set it to the notes in the roman numerals
        # for the range of the parts
        self.domains = {}
        if use_tessituras:
            for v in self.variables:
                part = v[0]
                self.domains[v] = self.tessituras[part]
        else:
            for v in self.variables:
                part = v[0]
                note = int(v[1:])
                rn = RomanNumeral(numerals[note - 1], self.key)
                self.domains[v] = notes_from_roman(*self.ranges[part], rn)

        # Create the no parallel fifths or octaves constraints
        self.constraints = []
        for i in range(notes - 1):
            scope = []
            for p in part_list:
                scope.append(self.parts[p][i])
                scope.append(self.parts[p][i + 1])
            con1 = Constraint(tuple(scope), no_parallel_fifths)
            con2 = Constraint(tuple(scope), no_parallel_octaves)
            self.constraints.append(con1)
            self.constraints.append(con2)

        # Create the different notes constraints
        for p in part_list:
            for i in range(len(self.parts[p]) - 1):
                n1 = self.parts[p][i]
                n2 = self.parts[p][i + 1]
                con = Constraint((n1, n2), different_notes)
                self.constraints.append(con)

        # TODO: See if this is necessary
        # # Create the numeral constraints
        # for i in range(notes):
        #     scope = []
        #     for p in part_list:
        #         scope.append(self.parts[p][i])
        #     con = Constraint(tuple(scope), in_numeral(numerals[i], key))
        #     print(numerals[i], key, con)
        #     self.constraints.append(con)

        # Create a map from a variable to a set of constraints associated
        # with that variable
        self.variables_to_constraints = {var: set() for var in self.variables}
        for con in self.constraints:
            for var in con.scope:
                self.variables_to_constraints[var].add(con)

    def __str__(self) -> str:
        """String representation of the CSP"""
        return str(self.variables)

    def display(self):
        """Print stats for the csp"""
        print(f'{self.name} CSP Problem')
        print(f'Variables: {", ".join(self.variables)}')
        print('Domain Size:')
        for v in self.variables:
            print(f'{v}: {len(self.domains[v])}')
        print('Constraints:')
        for v in self.variables:
            names = [
                c.condition.__name__ for c in self.variables_to_constraints[v]
            ]
            print(f'{v}: {", ".join(names)}')
        print()

    def display_assigment(self, assignment=None):
        """Print the assignment for the CSP"""
        if assignment is None:
            assignment = {}
        print(assignment)

    def show_score(self):
        """Show the score"""
        self.score.show()

    def consistent(self, assignment):
        """Checks to see if an assignment is consistent

        Arguments:
            assignment: A {variable : value} dictionary
        
        Returns:
            True if all of the constraints that can be evaluated
                evaluate to True given assignment.
        """
        return all(
            con.holds(assignment) for con in self.constraints
            if all(v in assignment for v in con.scope))


if __name__ == '__main__':
    csp = SimpleHarmonizerCSP('Test', 4, ['I', 'ii', 'V', 'I'])
    csp.display()
    print(csp.domains)
