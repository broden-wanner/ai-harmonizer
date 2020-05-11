import copy
from music21.note import Note
from music21.stream import Part, Measure, Score
from music21.instrument import Soprano, Alto, Tenor, Bass
from music21.clef import TrebleClef, BassClef
from music21.tempo import MetronomeMark

satb_voicing = {'s': Soprano(), 'a': Alto(), 't': Tenor(), 'b': Bass()}

def show_sovler_solution(solution, csp, bpm=60, instruments=satb_voicing, method='text'):
    """Displays the solution using music21
    
    Args:
        solution: A dictionary mapping variables to notes
        csp: The CSP used to solve the problem.
        method: A string of either 'text', 'midi', or 'music' to dictate
            whether to display test or music for the solution
    """
    s = Score(id='Solution Score')
    clefs = {
        's': TrebleClef(),
        'a': TrebleClef(),
        't': BassClef(),
        'b': BassClef()
    }
    tempo = MetronomeMark(number=bpm)

    for (i, p) in enumerate(csp.parts):
        m = Measure()
        if i == 0:
            m.append(tempo)

        for i in range(1, 1 + len(csp.parts[p])):
            n = copy.deepcopy(solution[f'{p}{i}'])
            m.append(n)

        new_part = Part(id=p)
        new_part.append([instruments[p], clefs[p], csp.key, m])
        s.append(new_part)

    # Add tempo
    s.recurse().getElementsByClass('Measure').append(tempo)
    s.show('text')

    if method == 'text' or method == 'midi':
        s.show(method)
    elif method == 'music':
        s.show()
    else:
        raise Exception('Invalid method to display')