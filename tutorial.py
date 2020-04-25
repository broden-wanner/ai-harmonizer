from music21 import *
from settings import *

environment.set('musicxmlPath', MUSICXMLPATH)
environment.set('midiPath', MIDIPATH)

f = note.Note('b-5')
f.show('midi')