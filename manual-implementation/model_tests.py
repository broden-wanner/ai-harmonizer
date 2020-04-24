from chord_block import ChordBlock
from note import Note
from figured_bass import FiguredBass
from interval import Interval

n1 = Note('A0')
n2 = Note('A0')
assert n1 == n2

i1 = Interval('P5')
print(i1)

print(Note('B0') - Note('A0'))
print(Note.to_num('B', 0))
