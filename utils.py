import music21 as m
import copy

# ______________________________________________________________________________
# Music21 utils


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


# ______________________________________________________________________________
# CSP utils

identity = lambda x: x


def argmin_random_tie(seq, key=identity):
    """Return a minimum element of seq; break ties at random."""
    return min(shuffled(seq), key=key)


def count(seq):
    """Count the number of items in sequence that are interpreted as true."""
    return sum(map(bool, seq))


def first(iterable, default=None):
    """Return the first element of an iterable; or default."""
    return next(iter(iterable), default)


def extend(s, var, val):
    """Copy dict s and extend it by setting var to val; return copy."""
    try:  # Python 3.5 and later
        return eval('{**s, var: val}')
    except SyntaxError:  # Python 3.4
        s2 = s.copy()
        s2[var] = val
        return s2