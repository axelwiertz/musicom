"""MusicXML export stub."""

def export_musicxml(matrix, path):
    """Stub musicxml export."""
    import os
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('<?xml version="1.0"?><score-partwise></score-partwise>')
    return True