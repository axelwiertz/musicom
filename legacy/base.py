# -*- coding: utf-8 -*-
"""LEGACY — base class, copied so the quarantined package is self-contained.

This is a byte-for-byte copy of the original ``structures/base.py``. It is
duplicated rather than imported so that nothing in the modern tree has to
point at quarantined code, and so that removing ``legacy/`` later leaves no
dangling references in ``structures/``.
"""
from abc import ABC


class Base(ABC):
    # Base class for project structures
    def __init__(self, name: str = 'MusicBase'):
        self.name = name

    def __repr__(self):
        return f"Instance(class='{self.__class__}', name='{self.name}')"
