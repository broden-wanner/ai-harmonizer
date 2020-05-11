import copy
from music21.note import Note
from music21.stream import Part, Measure, Score
from music21.instrument import Soprano, Alto, Tenor, Bass


def show_sovler_solution(solution, csp, method='text'):
    """Displays the solution using music21
    
    Args:
        solution: A dictionary mapping variables to notes
        csp: The CSP used to solve the problem.
        method: A string of either 'text' or 'music' to dictate
            whether to display test or music for the solution
    """
    s = Score(id='Solution Score')
    instruments = {'s': Soprano(), 'a': Alto(), 't': Tenor(), 'b': Bass()}
    for p in csp.parts:
        m = Measure()
        for i in range(1, 1 + len(csp.parts[p])):
            m.append(copy.deepcopy(solution[f'{p}{i}']))
        new_part = Part(id=p)
        new_part.append(instruments[p])
        new_part.append(csp.key)
        new_part.append(m)
        s.append(new_part)

    if method == 'text':
        s.show(method)
    elif method == 'music':
        s.show()