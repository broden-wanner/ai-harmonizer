import music21 as m
import copy

def play(x):
    """Returns nothing. Outputs a midi realization of x, a note or stream.
    Primarily for use in notebooks and web environments.
    """
    if isinstance(x, m.stream.Stream):
        x = copy.deepcopy(x)
        for subStream in x.recurse(streamsOnly=True, includeSelf=True):
            mss = subStream.getElementsByClass(m.stream.Measure)
            for ms in mss:
                ms.offset += 1.0
    if isinstance(x, m.note.Note):
        s = m.stream.Stream()
        s.append(m.note.Rest(1))
        s.append(x)
        x = s
    x.show('midi')
