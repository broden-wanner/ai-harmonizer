import copy
from music21.note import Note
from music21.stream import Part, Measure, Score


def show_sovler_solution(solution, parts, method='text'):
    """Displays the solution using music21
    
    Args:
        solution: A dictionary mapping variables to notes
        parts: A dictionary where the keys are the parts and
            the values are the value is a list of the variables
            associated with that part
        method: A string of either 'text' or 'music' to dictate
            whether to display test or music for the solution
    """
    s = Score(id='Solution Score')
    current_part = ''
    for p in parts:
        m = Measure()
        for i in range(1, 1 + len(parts[p])):
            m.append(copy.deepcopy(solution[f'{p}{i}']))
        new_part = Part(id=p)
        new_part.append(m)
        s.append(new_part)

    if method == 'text':
        s.show(method)
    elif method == 'music':
        s.show()