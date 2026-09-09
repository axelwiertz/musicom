"""Unified render pipeline - MIDI to WAV to OGG.

Chains FluidSynth + ffmpeg for complete render workflows.
Supports both full mix rendering and individual track (stem) rendering.
"""

import subprocess
import os
import tempfile
from typing import Optional, Dict, List

import mido

from .fluidsynth import FluidSynthRenderer


class RenderPipeline:
    """Full render chain: MIDI → WAV → OGG/MP3."""

    def __init__(self,
                 fluidsynth_bin: Optional[str] = None,
                 soundfont_path: Optional[str] = None,
                 sample_rate: int = 44100,
                 gain: float = 1.2):
        """Args:
            fluidsynth_bin: Path to fluidsynth binary (default: resolved via
                utilities.env.fluidsynth_bin() — $MUSICOM_FLUIDSYNTH, env dir,
                or PATH; fixes bare-'fluidsynth'-not-found on cron envs)
            soundfont_path: Path to .sf2 SoundFont file
            soundfont_path: Default SoundFont path
            sample_rate: Output sample rate
            gain: Gain multiplier
        """
        if fluidsynth_bin is None:
            from utilities.env import fluidsynth_bin as _resolve_fluid
            fluidsynth_bin = _resolve_fluid()
        self.renderer = FluidSynthRenderer(
            fluidsynth_bin=fluidsynth_bin,
            soundfont_path=soundfont_path,
            sample_rate=sample_rate,
            gain=gain
        )

    def render_to_wav(self, midi_path: str, output_path: str,
                      soundfont: Optional[str] = None) -> str:
        """Render MIDI to WAV."""
        return self.renderer.render(midi_path, output_path, soundfont=soundfont)

    def render_to_ogg(self, midi_path: str, output_path: str,
                      soundfont: Optional[str] = None,
                      bitrate: str = "128k") -> str:
        """Render MIDI to OGG (via WAV intermediate)."""
        wav_path = output_path.rsplit('.', 1)[0] + '.wav'
        self.renderer.render(midi_path, wav_path, soundfont=soundfont)
        
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", wav_path,
            "-codec:a", "libvorbis",
            "-b:a", bitrate,
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path

    def render_to_opus(self, midi_path: str, output_path: str,
                       soundfont: Optional[str] = None,
                       bitrate: str = "48k") -> str:
        """Render MIDI to Opus OGG (low bandwidth)."""
        wav_path = output_path.rsplit('.', 1)[0] + '.wav'
        self.renderer.render(midi_path, wav_path, soundfont=soundfont)
        
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", wav_path,
            "-codec:a", "libopus",
            "-application", "voip",
            "-b:a", bitrate,
            output_path
        ]
        subprocess.run(cmd, check=True)
        return output_path

    def render_stems(self, midi_path: str, output_dir: str,
                     soundfont: Optional[str] = None,
                     format: str = "wav") -> Dict[str, str]:
        """Render individual MIDI tracks as separate WAV files (stems).
        
        Extracts each track from the MIDI file and renders it independently.
        Track 0 (tempo/meta) is skipped. Output files named by track index
        and program name.
        
        Args:
            midi_path: Input MIDI file (multi-track)
            output_dir: Directory for stem WAV files
            soundfont: SoundFont path override
            format: Output format ('wav' or 'ogg')
            
        Returns:
            Dict mapping track_name → output_path
        """
        sf = soundfont or self.renderer.soundfont_path
        if not sf:
            raise ValueError("No SoundFont specified.")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Parse MIDI to get track info
        mid = mido.MidiFile(midi_path)
        stems = {}
        
        # GM program names for labeling
        GM_PROGRAMS = [
            "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano",
            "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord",
            "Clavi", "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba",
            "Xylophone", "Tubular Bells", "Dulcimer", "Drawbar Organ", "Percussive Organ",
            "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica",
            "Tango Accordion", "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)",
            "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)",
            "Overdriven Guitar", "Distortion Guitar", "Guitar harmonics",
            "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)",
            "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
            "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings",
            "Pizzicato Strings", "Orchestral Harp", "Timpani", "String Ensemble 1",
            "String Ensemble 2", "Synth Strings 1", "Synth Strings 2", "Choir Aahs",
            "Voice Oohs", "Synth Voice", "Orchestra Hit", "Trumpet", "Trombone",
            "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1",
            "Synth Brass 2", "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax",
            "Oboe", "English Horn", "Bassoon", "Clarinet", "Piccolo", "Flute",
            "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle",
            "Ocarina", "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)",
            "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)",
            "Lead 8 (bass + lead)", "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)",
            "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)",
            "Pad 8 (sweep)", "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)",
            "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)",
            "FX 7 (echoes)", "FX 8 (sci-fi)", "Sitar", "Banjo", "Shamisen", "Koto",
            "Kalimba", "Bag pipe", "Fiddle", "Shanai", "Tinkle Bell", "Agogo",
            "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum",
            "Reverse Cymbal", "Guitar Fret Noise", "Breath Noise", "Seashore",
            "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"
        ]
        
        # Skip track 0 (tempo/meta track) — render each voice track
        track_idx = 0
        for i, track in enumerate(mid.tracks):
            # Check if this track has note events (voice track)
            has_notes = any(msg.type in ('note_on', 'note_off') for msg in track)
            if not has_notes:
                continue
            
            # Find program change for this track
            program = 0
            channel = 0
            for msg in track:
                if msg.type == 'program_change':
                    program = msg.program
                    channel = msg.channel
                    break
            # If no program_change found, infer from note channels (some
            # exports omit program changes on drums / default-0 tracks).
            if channel == 0 and program == 0:
                note_chans = {m.channel for m in track if m.type == 'note_on'}
                if note_chans == {9}:
                    channel = 9

            # Instrument name: channel 9 (GM percussion) is ALWAYS drums —
            # program 0 on channel 9 means "standard kit", NOT Acoustic Grand
            # Piano. Previously the code labeled by program alone, so every
            # drum stem came out as "Acoustic_Grand_Piano" (mislabel bug,
            # fixed 2026-09-08).
            if channel == 9:
                inst_name = "Drums"
            else:
                inst_name = GM_PROGRAMS[program] if program < len(GM_PROGRAMS) else f"Program_{program}"
            # Sanitize for filename
            safe_name = inst_name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
            stem_name = f"track{track_idx:02d}_{safe_name}"
            
            # Create single-track MIDI file
            single_mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
            
            # Add tempo track
            tempo_track = mido.MidiTrack()
            for msg in mid.tracks[0]:
                if msg.type == 'set_tempo':
                    tempo_track.append(msg)
                    break
            single_mid.tracks.append(tempo_track)
            
            # Add voice track
            voice_track = mido.MidiTrack()
            for msg in track:
                voice_track.append(msg)
            single_mid.tracks.append(voice_track)
            
            # Write temp MIDI
            temp_midi = os.path.join(output_dir, f"{stem_name}.mid")
            single_mid.save(temp_midi)
            
            # Render to WAV
            if format == "wav":
                output_path = os.path.join(output_dir, f"{stem_name}.wav")
                self.renderer.render(temp_midi, output_path, soundfont=sf)
            elif format == "ogg":
                wav_path = os.path.join(output_dir, f"{stem_name}.wav")
                self.renderer.render(temp_midi, wav_path, soundfont=sf)
                output_path = os.path.join(output_dir, f"{stem_name}.ogg")
                cmd = [
                    "ffmpeg", "-y", "-loglevel", "error",
                    "-i", wav_path,
                    "-codec:a", "libopus",
                    "-application", "voip",
                    "-b:a", "48k",
                    output_path
                ]
                subprocess.run(cmd, check=True)
                os.unlink(wav_path)  # Clean up intermediate WAV
            else:
                raise ValueError(f"Unknown format: {format}")
            
            stems[stem_name] = output_path
            
            # Clean up temp MIDI
            os.unlink(temp_midi)
            track_idx += 1
        
        return stems


if __name__ == "__main__":
    print("RenderPipeline ready. Call render_to_wav/ogg/opus(midi, output, soundfont=...).")
