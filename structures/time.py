"""Music Time Structure: meter and tempo"""
from .timegrid import MusicTimeGrid
from .unit import MusicEvent, MusicUnit
from typing import List, Tuple, Optional


class TempoRange:
    """Common tempo ranges in BPM for different music styles."""
    _dict = {
        'Ballad': (60, 80),
        'Pop': (100, 130),
        'Rock': (120, 160),
        'EDM / Dance': (120, 140),
        'Techno': (125, 150),
        'Drum & Bass': (160, 180),
        'Classical (Allegro)': (120, 168),
        'Classical (Adagio)': (66, 76)
    }
    @classmethod
    def get_range(cls, style: str):
        """Get tempo range for a given music style."""
        return cls._dict.get(style, (60, 120))  # Default to (60, 120) if style not found

    @classmethod
    def styles(cls):
        """Get a list of available music styles."""
        return list(cls._dict.keys())


class MusicLinearTime:
    """Music Linear Time Structure"""
    def __init__(self,
                time_grid: MusicTimeGrid = None,
                bpm: int = None  # beats per minute
                 ):
        ### Linear timescale
        self.time_grid = time_grid if time_grid else MusicTimeGrid.default_time_grid()
        # Tempo
        self.bpm = bpm if bpm else 120  # Default to 120 BPM

    def seconds_per_cycle(self) -> float:
        return self.seconds_per_beat * self.time_grid.beats_per_cycle
    @property
    def seconds_per_beat(self) -> int:
        return 60.0 / self.bpm if self.bpm else 0
    @property
    def seconds_per_tick(self) -> float:
        return self.seconds_per_beat / self.time_grid.ticks_per_beat if self.time_grid.ticks_per_beat else 0


class TimeConverter:
    """Convert between absolute ticks, delta times, and MIDI events.
    
    Absolute time: start_tick and end_tick are absolute positions in the composition
    Delta time: time between events, used in MIDI files
    
    Note: MIDI-specific methods require mido to be installed.
    """
    
    @staticmethod
    def events_to_delta(events: List[MusicEvent]) -> List[Tuple[int, int, int]]:
        """Convert MusicEvents with absolute ticks to delta-time tuples.
        
        Args:
            events: List of MusicEvent sorted by start_tick
            
        Returns:
            List of (delta_time, pitch, duration_ticks) tuples for MIDI export
        """
        if not events:
            return []
        
        # Sort by start_tick to ensure chronological order
        sorted_events = sorted(events, key=lambda e: e.start_tick)
        
        result = []
        prev_end = 0
        
        for event in sorted_events:
            delta = event.start_tick - prev_end
            duration = event.end_tick - event.start_tick
            result.append((delta, event.pitch, duration))
            prev_end = event.end_tick
        
        return result
    
    @staticmethod
    def unit_to_delta_events(unit: MusicUnit) -> List[Tuple[int, int, int]]:
        """Convert a MusicUnit to delta-time events."""
        return TimeConverter.events_to_delta(unit.events)
    
    @staticmethod
    def align_units_to_track(units: List[MusicUnit]) -> List[MusicEvent]:
        """Combine multiple MusicUnits into a single track with aligned absolute timing.
        
        Each unit's events have absolute ticks relative to unit start.
        Units are concatenated in order, preserving their internal timing.
        
        Args:
            units: List of MusicUnit objects in chronological order
            
        Returns:
            List of MusicEvent with absolute ticks across all units
        """
        all_events = []
        time_offset = 0
        
        for unit in units:
            for event in unit.events:
                new_event = MusicEvent(
                    pitch=event.pitch,
                    volume=event.volume,
                    start_tick=event.start_tick + time_offset,
                    end_tick=event.end_tick + time_offset
                )
                all_events.append(new_event)
            
            time_offset += unit.len_ticks()
        
        return all_events
    
    @staticmethod
    def track_to_midi_messages(delta_events: List[Tuple[int, int, int]], 
                               program: int = 0, 
                               channel: int = 0):
        """Convert delta-time events to MIDI messages.
        
        Requires mido to be installed.
        
        Args:
            delta_events: List of (delta_time, pitch, duration) tuples
            program: MIDI program number (0-127)
            channel: MIDI channel (0-15)
            
        Returns:
            List of mido.Message objects (program_change, note_on, note_off)
        """
        try:
            import mido
        except ImportError:
            raise ImportError("mido is required for MIDI message conversion. Install with: pip install mido")
        
        messages = []
        
        # Add program change at start
        messages.append(mido.Message('program_change', 
                                     program=program, 
                                     channel=channel, 
                                     time=0))
        
        for delta, pitch, duration in delta_events:
            # Note on
            messages.append(mido.Message('note_on', 
                                         note=pitch, 
                                         velocity=100, 
                                         channel=channel,
                                         time=delta))
            # Note off
            messages.append(mido.Message('note_off', 
                                         note=pitch, 
                                         velocity=100, 
                                         channel=channel,
                                         time=duration))
        
        return messages
    
    @staticmethod
    def validate_track_length(tracks_events: List[List[MusicEvent]]) -> bool:
        """Check all tracks have the same total duration.
        
        Args:
            tracks_events: List of event lists, one per track
            
        Returns:
            True if all tracks have identical max end_tick, False otherwise
        """
        if not tracks_events:
            return True
        
        lengths = []
        for events in tracks_events:
            if events:
                max_end = max(e.end_tick for e in events)
                lengths.append(max_end)
            else:
                lengths.append(0)
        
        return len(set(lengths)) == 1
    
    @staticmethod
    def get_track_length(events: List[MusicEvent]) -> int:
        """Get the total length of a track in ticks."""
        if not events:
            return 0
        return max(e.end_tick for e in events)
