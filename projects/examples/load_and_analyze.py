from converters import midifile_to_score
from analysis import score_analyze

score = midifile_to_score('Sousta.mid')
score_analyze (score)
