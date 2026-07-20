"""
Configuration settings for music composition application.
"""
import os
import tempfile


class Config:
    # Default configuration (cross-platform temp dir; override as needed).
    DEFAULT_PATH = os.path.join(tempfile.gettempdir(), 'Music')
    DEFAULT_MIDI_FILE_IN = 'in.mid'
    DEFAULT_MIDI_FILE_OUT = 'out.mid'

    DEFAULT_ONSET_INTERVAL = 1
    DEFAULT_DURATION = 1
    DEFAULT_VOLUME = 100

