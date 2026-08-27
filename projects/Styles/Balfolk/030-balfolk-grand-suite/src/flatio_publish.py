
import sys
import os
import base64
import json
import requests
from music21 import stream, note, tempo, meter, midi, instrument

# 0. Auth
FLAT_IO_TOKEN = "16d0fdeb8a6c9016503da23d27ee06bfeeb64d928a936247aa8628634065619e9275275264f60dd6e4509fa97f0e530f87638bcba1d1aaa449548615a54783d3"

def publish_030_flatio():
    # 1. Create Stream
    s = stream.Score()
    p1 = stream.Part()
    p1.id = 'Violin'
    p1.insert(0, instrument.Violin())
    p2 = stream.Part()
    p2.id = 'Bass'
    p2.insert(0, instrument.ElectricBass())
    
    # D Dorian
    scale = [62, 64, 65, 67, 69, 71, 72, 74]
    
    # Sections (6/8 logic)
    intro = [scale[4], None, None, scale[5], 0, 0] * 8
    dance = []
    for _ in range(8): dance.extend([scale[idx] for idx in [0, 2, 4, 3, 3, 5]])
    bridge = []
    for _ in range(8): bridge.extend([scale[idx] for idx in [0, 3, 6, 2, 4, 1]])
    climax = [scale[i % len(scale)] for i in range(48)]
    full = intro + dance + bridge + climax
    
    # Fill Lead
    offset = 0.0
    for p in full:
        if p is None or p == 0:
            offset += 0.5 # Eighth note
            continue
        n = note.Note(p)
        n.quarterLength = 0.5
        p1.insert(offset, n)
        offset += 0.5
        
    # Fill Bass
    offset_b = 0.0
    for i, p in enumerate(full):
        if i % 3 == 0:
            pb = 38 if (i % 6 < 3) else 43
            nb = note.Note(pb)
            nb.quarterLength = 0.5
            p2.insert(offset_b, nb)
        offset_b += 0.5

    s.append(p1)
    s.append(p2)
    s.insert(0, meter.TimeSignature('6/8'))
    s.insert(0, tempo.MetronomeMark(number=118))
    
    # 2. Export MusicXML
    xml_path = "/tmp/030_suite.xml"
    s.write('musicxml', fp=xml_path)
    
    # 3. Publish
    with open(xml_path, 'rb') as f:
        xml_data = f.read()
    
    b64_xml = base64.b64encode(xml_data).decode('utf-8')
    
    payload = {
        'title': '030 - Balfolk Grand Suite',
        'privacy': 'public',
        'data': b64_xml,
        'dataEncoding': 'base64'
    }
    
    headers = {
        'Authorization': f'Bearer {FLAT_IO_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    resp = requests.post('https://api.flat.io/v2/scores', json=payload, headers=headers)
    return resp.json()

if __name__ == "__main__":
    result = publish_030_flatio()
    print(json.dumps(result, indent=2))
