from pathlib import Path
base = Path(__file__).resolve().parents[1]
(base / 'MIDI').mkdir(exist_ok=True)
(base / 'Audio').mkdir(exist_ok=True)
print('regen placeholder for 043-country-fence-line-loop')
