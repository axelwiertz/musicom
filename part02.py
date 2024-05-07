# modules
import musicpy as mp
from musicpy import *
from musicpy.daw import *

# MIDI files
curpath = 'C:\\Users\\axelw\\OneDrive\Music\\'
pST = read(curpath + 'SuperTrouper.mid', split_channels=True)
pATSW = read(curpath + 'AllThatSheWants.mid')                                                                                                                            
pAT = read(curpath + 'AxelTheme.mid')


play(ST(0))
play(ST(1))
play(ST(1)[1:20])
play(ST(1)[1:10])
play(ST(1)[1:30])
play(ST(1)[1:26])
                                                                                                                         
ST(1)[1:26]
ST(1)[1:26].notes

# Analyis
cht = mp.alg.detect(ST(1)[1:26])
'Cmaj13 omit F sort as [1, 2, 3, 5, 6, 4]'
cht = mp.alg.chord_analysis(ST(1))

# Compose
guitar = (C('CM7', 3, 1/4, 1/8)^2 |
          C('G7sus', 2, 1/4, 1/8)^2 |
          C('A7sus', 2, 1/4, 1/8)^2 |
          C('Em7', 2, 1/4, 1/8)^2 |
           C('FM7', 2, 1/4, 1/8)^2 |
           C('CM7', 3, 1/4, 1/8)@1 |
           C('AbM7', 2, 1/4, 1/8)^2 |
           C('G7sus', 2, 1/4, 1/8)^2) * 2
 
play(guitar, bpm=100, instrument=25)
play(guitar, bpm=100)
play(guitar, bpm=100, instrument=24)
play(guitar, bpm=100, instrument=25)
c1 = C('CM7', 3, 1/4, 1/8)^2
c2 = C('CM7')
c2 = C('CM7', 3)
c3 = C('CM7', 5)
c5 = C('CM7', 3, 1/4, 1/8)
c5 = C('CM7', 3, 1/4)
c6 = C('CM7', 3, 1/4)^2

# drum                                                                                                                                
drum1 = drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')
drum('S[l:.8; i:.; r:4], S[l:.16; i:.], S[l:.8; i:.], S[l:.16; i:.], S[l:.8; i:.], S[l:.8; i:.]')

drum ('K, K;H, S, H, K, K;H;PH, H;S, H')

# DAW
daw1 = daw(3)
daw1.load(0, 'EMU II ACOUSTIC GUITAR.sf2')


song1 = daw(3, name='my first song')

# editor
S('C4 major')%(15654321, 0.4)
S('C major').get('1,1,5,5,6,6,5,-,4,4,3,3,2,2,1,-')
/S('C major').chord_progression(['IM7', 'Vsus', 'vi7', 'IVM7'])

