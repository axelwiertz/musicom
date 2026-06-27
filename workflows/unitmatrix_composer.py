"""UnitMatrix-first composition workflow.

This module provides a high-level API for composing music using the UnitMatrix approach:
1. Define voices (rows) - e.g., Lead, Bass, Drums
2. Define sections (columns) - e.g., Intro, Verse, Chorus
3. Fill cells with MusicUnit material
4. Validate timing alignment
5. Export to MIDI

This solves the track alignment problem where tracks had different lengths.
"""

from typing import List, Tuple, Optional, Dict, Any

# Import structures - use absolute path since package structure is flat
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from structures import (
    UnitMatrix, 
    MusicUnit, 
    MusicEvent,
    MusicTimeGrid,
    TimeConverter,
    MidiInstrument
)

# Optional mido import - will be checked at runtime
_mido_available = False
try:
    import mido
    _mido_available = True
except ImportError:
    pass


class UnitMatrixComposer:
    """High-level composer using UnitMatrix workflow.
    
    Ensures all tracks have identical duration by validating timing
    before MIDI export.
    """
    
    def __init__(self, 
                 bpm: int = 120, 
                 ticks_per_beat: int = 480,
                 beats_per_bar: int = 4):
        """Initialize composer with timing parameters.
        
        Args:
            bpm: Beats per minute
            ticks_per_beat: MIDI ticks per beat (standard: 480)
            beats_per_bar: Beats per measure (standard: 4)
        """
        self.bpm = bpm
        self.ticks_per_beat = ticks_per_beat
        self.beats_per_bar = beats_per_bar
        self.ticks_per_bar = ticks_per_beat * beats_per_bar
        
        self.time_grid = MusicTimeGrid(
            ticks_per_cycle=ticks_per_beat * beats_per_bar,
            beats_per_cycle=beats_per_bar
        )
        
        self.matrix: Optional[UnitMatrix] = None
        self.voices: List[Dict[str, Any]] = []  # List of voice configs
        self.sections: List[Dict[str, Any]] = []  # List of section configs
        
    def create_matrix(self, num_voices: int, num_sections: int) -> UnitMatrix:
        """Create a new UnitMatrix with specified dimensions.
        
        Args:
            num_voices: Number of rows (voices/instruments)
            num_sections: Number of columns (sections)
            
        Returns:
            New UnitMatrix instance
        """
        self.matrix = UnitMatrix(shape=(num_voices, num_sections))
        return self.matrix

    def add_voice(self, name: str, program: int = 0, channel: int = 0) -> int:
        """Add a voice definition.
        
        Args:
            name: Voice name (e.g., 'Lead Guitar', 'Bass')
            program: MIDI program number
            channel: MIDI channel (0-15)
            
        Returns:
            Voice index (row number)
        """
        voice_idx = len(self.voices)
        self.voices.append({
            'name': name,
            'program': program,
            'channel': channel,
            'row': voice_idx
        })
        return voice_idx

    def add_section(self, name: str, bars: int = 4) -> int:
        """Add a section definition.
        
        Args:
            name: Section name (e.g., 'Intro', 'Verse')
            bars: Number of bars in this section
            
        Returns:
            Section index (column number)
        """
        section_idx = len(self.sections)
        self.sections.append({
            'name': name,
            'bars': bars,
            'column': section_idx
        })
        return section_idx

    def set_unit(self, row: int, col: int, unit: MusicUnit):
        """Place a MusicUnit in the matrix.
        
        Args:
            row: Voice index
            col: Section index
            unit: MusicUnit to place
        """
        if self.matrix is None:
            raise ValueError("Matrix not created. Call create_matrix() first.")
        self.matrix.set_unit((row, col), unit)

    def fill_voice_section(self, voice_name: str, section_name: str, unit: MusicUnit):
        """Fill a cell by voice and section names.
        
        Args:
            voice_name: Name of voice (must match add_voice)
            section_name: Name of section (must match add_section)
            unit: MusicUnit to place
        """
        voice = next((v for v in self.voices if v['name'] == voice_name), None)
        section = next((s for s in self.sections if s['name'] == section_name), None)
        
        if voice is None:
            raise ValueError(f"Voice '{voice_name}' not found")
        if section is None:
            raise ValueError(f"Section '{section_name}' not found")
        
        self.set_unit(voice['row'], section['column'], unit)

    def validate(self) -> Tuple[bool, str]:
        """Validate matrix timing alignment.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.matrix is None:
            return False, "Matrix not created"
        
        if not self.matrix.validate_timing():
            lengths = self.matrix.get_all_row_lengths()
            return False, f"Track length mismatch: {lengths}"
        
        return True, "OK"

    def get_track_length_ticks(self) -> int:
        """Get total composition length in ticks."""
        if self.matrix is None:
            return 0
        return self.matrix.get_track_length()

    def get_track_length_bars(self) -> float:
        """Get total composition length in bars."""
        return self.get_track_length_ticks() / self.ticks_per_bar

    def to_midi(self, output_path: str, include_tempo: bool = True) -> str:
        """Export UnitMatrix to MIDI file.
        
        Args:
            output_path: Path to save MIDI file
            include_tempo: Whether to include tempo meta message
            
        Returns:
            Path to saved MIDI file
            
        Raises:
            ValueError: If matrix is not created or timing not validated
            ImportError: If mido is not installed
        """
        if not _mido_available:
            raise ImportError("mido is required for MIDI export. Install with: pip install mido")
            
        if self.matrix is None:
            raise ValueError("Matrix not created. Call create_matrix() first.")
        
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(f"Timing validation failed: {error}")
        
        # Create MIDI file
        mid = mido.MidiFile()
        mid.ticks_per_beat = self.ticks_per_beat
        
        # Add tempo meta message to first track
        if include_tempo:
            tempo_track = mido.MidiTrack()
            tempo_track.append(mido.MetaMessage(
                'set_tempo', 
                tempo=mido.bpm2tempo(self.bpm), 
                time=0
            ))
            mid.tracks.append(tempo_track)
        
        # Add one track per voice
        for voice in self.voices:
            track = mido.MidiTrack()
            
            # Get MIDI messages for this voice
            messages = self.matrix.to_midi_track_messages(
                voice['row'], 
                program=voice['program'],
                channel=voice['channel']
            )
            
            for msg in messages:
                track.append(msg)
            
            mid.tracks.append(track)
        
        mid.save(output_path)
        return output_path

    def to_midi_bytes(self) -> bytes:
        """Export UnitMatrix to MIDI bytes.
        
        Returns:
            MIDI file as bytes
        """
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as f:
            self.to_midi(f.name)
            with open(f.name, 'rb') as rf:
                data = rf.read()
            os.unlink(f.name)
            return data


# ==================== HELPER FUNCTIONS ====================


def create_blues_form_matrix(bpm: int = 80, 
                             num_bars: int = 12,
                             ticks_per_beat: int = 480) -> Tuple['UnitMatrixComposer', Dict]:
    """Create a UnitMatrixComposer pre-configured for 12-bar blues.
    
    Args:
        bpm: Tempo in BPM
        num_bars: Number of bars (default 12 for standard blues)
        ticks_per_beat: MIDI ticks per beat
        
    Returns:
        Tuple of (composer, section_info) where section_info describes the form
    """
    composer = UnitMatrixComposer(
        bpm=bpm,
        ticks_per_beat=ticks_per_beat,
        beats_per_bar=4
    )
    
    # Create matrix: 3 voices (Lead, Bass, Drums) x sections
    # Standard 12-bar blues: 3 sections of 4 bars each
    num_sections = num_bars // 4
    composer.create_matrix(num_voices=3, num_sections=num_sections)
    
    # Add voices
    composer.add_voice('Lead', program=MidiInstrument.ACOUSTIC_GUITAR, channel=0)
    composer.add_voice('Bass', program=MidiInstrument.BASS, channel=1)
    composer.add_voice('Drums', program=0, channel=9)  # Channel 9 = percussion
    
    # Add sections
    section_names = []
    for i in range(num_sections):
        bar_start = i * 4
        bar_end = bar_start + 4
        section_names.append(f"Bars {bar_start+1}-{bar_end}")
        composer.add_section(f"Bars {bar_start+1}-{bar_end}", bars=4)
    
    section_info = {
        'form': '12-bar blues',
        'sections': section_names,
        'harmony': ['I', 'I', 'I', 'I', 'IV', 'IV', 'I', 'I', 'V', 'IV', 'I', 'I']
    }
    
    return composer, section_info


def create_empty_unit(duration_ticks: int) -> MusicUnit:
    """Create an empty MusicUnit of specified duration.
    
    Useful for placeholder cells in the matrix.
    
    Args:
        duration_ticks: Duration in ticks
        
    Returns:
        Empty MusicUnit
    """
    # Create a rest that lasts the full duration
    rest = MusicEvent(
        pitch=0,
        volume=0,
        start_tick=0,
        end_tick=duration_ticks
    )
    return MusicUnit(events=[rest])


def create_note_unit(pitch: int, duration_ticks: int, start_tick: int = 0) -> MusicUnit:
    """Create a MusicUnit with a single note.
    
    Args:
        pitch: MIDI note number
        duration_ticks: Duration in ticks
        start_tick: Start position in ticks (default 0)
        
    Returns:
        MusicUnit with one note
    """
    note = MusicEvent(
        pitch=pitch,
        volume=100,
        start_tick=start_tick,
        end_tick=start_tick + duration_ticks
    )
    return MusicUnit(events=[note])


def create_chord_unit(pitches: List[int], duration_ticks: int, start_tick: int = 0) -> MusicUnit:
    """Create a MusicUnit with a chord (multiple simultaneous notes).
    
    Args:
        pitches: List of MIDI note numbers
        duration_ticks: Duration in ticks
        start_tick: Start position in ticks (default 0)
        
    Returns:
        MusicUnit with chord
    """
    events = []
    for pitch in pitches:
        note = MusicEvent(
            pitch=pitch,
            volume=100,
            start_tick=start_tick,
            end_tick=start_tick + duration_ticks
        )
        events.append(note)
    return MusicUnit(events=events)
