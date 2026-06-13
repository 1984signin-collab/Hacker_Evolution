#!/usr/bin/env python3
"""HACKER EVOLUTION — Font Manager.

Tries to load JetBrains Mono Nerd Font; falls back to Consolas.
Provides a single `get_font()` entry point.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont


class FontManager:
    """Manages font discovery and caching.

    Usage:
        FontManager.discover()
        font = FontManager.get_font(11, 'bold')
        widget.config(font=font)
    """

    _family: str = 'Consolas'
    _cache: dict = {}

    @classmethod
    def discover(cls):
        """Scan available system fonts. Prefer JetBrains Mono."""
        families = set(tkfont.families())
        preferred = [
            'JetBrains Mono NF',
            'JetBrainsMono NF',
            'JetBrains Mono',
            'JetBrainsMono',
            'Consolas',
        ]
        for name in preferred:
            if name in families:
                cls._family = name
                break
        # If none of the above, take the first monospace
        if cls._family == 'Consolas' and 'Consolas' not in families:
            for f in families:
                if any(kw in f.lower() for kw in ('mono', 'console', 'courier')):
                    cls._family = f
                    break

    @classmethod
    def get_font(cls, size: int = 11, weight: str = '') -> tuple:
        """Return a (family, size, weight) tuple for tkinter."""
        key = (cls._family, size, weight)
        if key not in cls._cache:
            if weight:
                cls._cache[key] = (cls._family, size, weight)
            else:
                cls._cache[key] = (cls._family, size)
        return cls._cache[key]

    @classmethod
    def family(cls) -> str:
        return cls._family

    @classmethod
    def measure(cls, text: str, size: int = 11) -> int:
        """Estimate pixel width of text in the current font."""
        # Rough estimate: average char width ≈ size * 0.6
        return int(len(text) * size * 0.6)
