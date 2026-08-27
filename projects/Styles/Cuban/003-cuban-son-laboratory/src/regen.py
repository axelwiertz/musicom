from pathlib import Path

root = Path(__file__).resolve().parent.parent
(root / 'Analysis' / 'regen_marker.txt').write_text('regen ready\n')
print('regen ready')
