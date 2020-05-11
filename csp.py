from music21.note import Note
from music21.stream import Score, Measure, Part
from music21.chord import Chord
from music21.voiceLeading import VoiceLeadingQuartet
from music21.roman import romanNumeralFromChord
from music21.clef import BassClef, TrebleClef

Note.__hash__ = lambda self: hash(self.nameWithOctave)
# ^ Add hash function to Note


def tessitura(bottom, top, key=None):
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
            for acc in ['', '-', '#']:
                all_notes.append(Note(f'{n}{acc}{o}'))
        o += 1
    return all_notes


satb_tessituras = {
    's': [Note('G4')],
    'a': [Note('F4')],
    't': [Note('E4')],
    'b': [Note('D4')]
}


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


def no_parallel_fifths(*notes) -> bool:
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
                                   notes2[n2 + 1]).parallelFifth():
                return False
    return True


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
        variables: The file location of the spreadsheet
        domains: A dictionary that maps variables to their domains
        constraints: A list of constraints
        variables_to_constraints: A dictionary that maps variables to the 
            set of contstraints that they're involved in
        parts: A dictionary of that maps parts ('s', 'a', 't', or 'b') to
            a list of the variables in that part
    """
    def __init__(self, notes: int, part_list=['s', 'a', 't', 'b']):
        """Initialize the data structures for the problem
        
        Args:
            notes: Number of notes for the csp
            parts: A list of the parts for the csp. Can contain
                's' (soprano), 'a' (alto), 't' (tenor), or 'b' (bass)
        """
        # Create a variable for each note in each part
        self.notes = notes
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
            self.domains[v] = satb_tessituras[voice]

        # Create the no parallel fifths constraints
        self.constraints = []
        for i in range(notes - 1):
            scope = []
            for p in part_list:
                scope.append(self.parts[p][i])
                scope.append(self.parts[p][i + 1])
            con = Constraint(tuple(scope), no_parallel_fifths)
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
        print(f'Variables: {", ".join(self.variables)}')
        print('\nDomain Size:')
        for v in self.variables:
            print(f'{v}: {len(self.domains[v])}')
        print('\nConstraints:')
        for v in self.variables:
            print(f'{v}: {self.variables_to_constraints[v]}')
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
    csp = SimpleHarmonizerCSP(4)
    csp.display()
