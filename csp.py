from music21.note import Note
from music21.stream import Score, Measure, Part
from music21.chord import Chord
from music21.voiceLeading import VoiceLeadingQuartet
from music21.roman import romanNumeralFromChord
from music21.clef import BassClef, TrebleClef
from music21.key import Key
from constraints import *

Note.__hash__ = lambda self: hash(self.nameWithOctave)
# ^ Add hash function to Note


def tessitura(bottom, top, key=Key('C')):
    """Generate all possible notes between two notes (inclusive) in a given key"""
    all_notes = []
    o = bottom.octave
    while o <= top.octave:
        notes = 'ABCDEFG'
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
        tessiturats: A dictionary mapping the parts to their ranges, which is 
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
                 tessituras=None,
                 key=Key('C')):
        """Initialize the data structures for the problem
        
        Args:
            name: Name for the CSP
            notes: Number of notes for the CSP
            list: A list of all numerals (as strings) to be used in the constraints. The
                length must be equal to the number of notes.
            part_list: A list of the parts for the CSP. Can contain
                's' (soprano), 'a' (alto), 't' (tenor), or 'b' (bass)
            tessiturats: A dictionary mapping parts to their tessituras.
                It is used for the domains of each variables. If not specified,
                then the default satb_tessituras are used.
            key: The key we would like the piece to be in. It is C Major 
                by default.
        """
        self.name = name
        self.notes = notes
        self.numerals = numerals
        self.key = key

        # Set the tessituras for the domains later on
        if not tessituras:
            # These are the default tessituras for SATB
            satb_tessituras = {
                's': tessitura(Note('G3'), Note('C4'), key=key),
                'a': tessitura(Note('C4'), Note('G4'), key=key),
                't': tessitura(Note('G3'), Note('C4'), key=key),
                'b': tessitura(Note('C3'), Note('G3'), key=key)
            }
            self.tessituras = satb_tessituras
        else:
            self.tessituras = tessituras

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

        # Set the domains to the parts' tessituras
        self.domains = {}
        for v in self.variables:
            voice = v[0]
            self.domains[v] = self.tessituras[voice]

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

        # Create the numeral constraints
        for i in range(notes):
            scope = []
            for p in part_list:
                scope.append(self.parts[p][i])
            con = Constraint(tuple(scope), in_numeral(numerals[i], key))
            self.constraints.append(con)

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
    print(tessitura(Note('G4'), Note('G5'), Key('G-')))
    csp = SimpleHarmonizerCSP('Test', 4, ['I', 'ii', 'V', 'I'])
    csp.display()
