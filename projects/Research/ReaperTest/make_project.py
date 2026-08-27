# Test script to automate REAPER via python and ReaScript.
# Since we are running headless, we can generate a REAPER Project File (.RPP) 
# containing our MIDI notes and track definitions directly, then use REAPER's CLI 
# to render it to an audio format, or inspect it.
#
# An RPP is plain text! We can build a valid .RPP file programmatically, 
# inject a MIDI item with notes, and run REAPER's batch renderer on it.

import sys
import os

def create_reaper_test_project():
    rpp_content = """<REAPER_PROJECT 0.1 "7.77/Linux" 1783080000
  RPR_VERSION 7.77
  <TRACK
    NAME "Lead Synth"
    PEAKCOL 16576
    BEAT 1
    VOLUME 0.0
    PAN 0.0
    MUTE 0
    SOLO 0
    TRACKHEIGHT 0 0 0
    PLAYEDITS 1
    INENDS 0
    <ITEM
      POSITION 0.0
      LENGTH 4.0
      LOOP 1
      NAME "Test Pattern"
      PLAYRATE 1.0
      CHANPLAYTASK 0
      SOFFS 0.0
      <SOURCE MIDI
        HASDATA 1
        E 480 b0 79 00
        E 480 90 3c 64
        E 960 80 3c 00
        E 0 90 40 64
        E 960 80 40 00
        E 0 90 43 64
        E 960 80 43 00
        E 0 90 48 64
        E 960 80 48 00
      >
    >
  >
>
"""
    project_dir = "/opt/data/projects/Research/ReaperTest"
    os.makedirs(project_dir, exist_ok=True)
    
    project_path = os.path.join(project_dir, "test_session.rpp")
    with open(project_path, "w") as f:
        f.write(rpp_content)
        
    print(f"[SUCCESS] Programmatically built RPP session: {project_path}")
    return project_path

if __name__ == '__main__':
    create_reaper_test_project()