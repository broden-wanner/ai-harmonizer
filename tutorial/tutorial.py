from music21 import *
from settings import *

# Initial setup
environment.set('musicxmlPath', MUSICXMLPATH)
environment.set('midiPath', MIDIPATH)
environment.set('lilypondPath', LILYPONDPATH)
environment.set('musescoreDirectPNGPath', MUSESCOREPATH)

f = note.Note('b-5')
f.show('midi')
