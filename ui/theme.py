#!/usr/bin/env python3
"""HACKER EVOLUTION — Theme engine (UI redesign v2).

Single source of truth for all visual constants.
Calibrated on update/generated-image.png reference.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class Theme:
    """Complete theme palette and spacing constants.

    Usage:
        from ui.theme import Theme
        widget.config(bg=Theme.BG, fg=Theme.CYAN)
    """

    # ── Background stack (4 levels of depth) ──
    BG_VOID: ClassVar[str] = '#000000'      # deepest — console background
    BG_CANVAS: ClassVar[str] = '#000504'    # main canvas, map
    BG_SURFACE: ClassVar[str] = '#000a0a'   # card bg, panel bg
    BG_HEADER: ClassVar[str] = '#001212'    # card header, section title

    # ── Cyan / Teal (primary, 90% of interface) ──
    CYAN: ClassVar[str] = '#00cccc'         # bright — cursor, prompt, active link
    CYAN_MID: ClassVar[str] = '#008888'     # mid — panel borders, header text
    CYAN_DIM: ClassVar[str] = '#004444'     # dim — separators, inactive state
    CYAN_ULTRADIM: ClassVar[str] = '#002222'  # inactive buttons, DORMANT state

    # ── Purple / Magenta (alert, <5%) ──
    MAGENTA: ClassVar[str] = '#cc44cc'      # bright — sentinel ACTIVE, critical alert
    MAGENTA_MID: ClassVar[str] = '#882288'   # mid — alert borders
    MAGENTA_DIM: ClassVar[str] = '#440044'   # dim — alert card bg

    # ── Green (success, positive states) ──
    GREEN: ClassVar[str] = '#00cc88'        # hacked status, money, achievement

    # ── Amber (warning) ──
    AMBER: ClassVar[str] = '#ccaa00'        # trace > 50%, sentinel ANALYZING

    # ── White / Text ──
    TEXT: ClassVar[str] = '#ddeeff'         # primary text — console output, labels
    TEXT_DIM: ClassVar[str] = '#7799aa'     # secondary — dim labels, timestamps
    TEXT_MUTED: ClassVar[str] = '#334455'   # tertiary — debug, hints, border text

    # ── Special ──
    RED: ClassVar[str] = '#cc2244'          # error / game over
    RED_DIM: ClassVar[str] = '#440011'      # error bg

    # ── Spacing ──
    PAD_TINY: ClassVar[int] = 2
    PAD_SMALL: ClassVar[int] = 4
    PAD: ClassVar[int] = 8
    PAD_LARGE: ClassVar[int] = 12

    # ── Typography ──
    FONT_FAMILY: ClassVar[str] = 'Consolas'  # will be overridden by FontManager
    FONT_CONSOLE: ClassVar[tuple] = ('Consolas', 11)
    FONT_CONSOLE_BOLD: ClassVar[tuple] = ('Consolas', 12, 'bold')
    FONT_INPUT: ClassVar[tuple] = ('Consolas', 12, 'bold')
    FONT_STAT_VALUE: ClassVar[tuple] = ('Consolas', 14, 'bold')
    FONT_STAT_LABEL: ClassVar[tuple] = ('Consolas', 8)
    FONT_HEADER: ClassVar[tuple] = ('Consolas', 9, 'bold')
    FONT_TITLE: ClassVar[tuple] = ('Consolas', 16, 'bold')
    FONT_MAP_LABEL: ClassVar[tuple] = ('Consolas', 8, 'bold')
    FONT_LOG: ClassVar[tuple] = ('Consolas', 10)
    FONT_LOG_TIME: ClassVar[tuple] = ('Consolas', 9)
    FONT_BUTTON: ClassVar[tuple] = ('Consolas', 10, 'bold')

    # ── Theme transition helpers ──

    @classmethod
    def with_font(cls, family: str) -> type[Theme]:
        """Return a new Theme with the given font family applied."""
        new = cls
        new.FONT_FAMILY = family
        def _make(size, weight=''):
            return (family, size, weight) if weight else (family, size)
        new.FONT_CONSOLE = _make(11)
        new.FONT_CONSOLE_BOLD = _make(12, 'bold')
        new.FONT_INPUT = _make(12, 'bold')
        new.FONT_STAT_VALUE = _make(14, 'bold')
        new.FONT_STAT_LABEL = _make(8)
        new.FONT_HEADER = _make(9, 'bold')
        new.FONT_TITLE = _make(16, 'bold')
        new.FONT_MAP_LABEL = _make(8, 'bold')
        new.FONT_LOG = _make(10)
        new.FONT_LOG_TIME = _make(9)
        new.FONT_BUTTON = _make(10, 'bold')
        return new

    @classmethod
    def rgba(cls, hex_color: str, alpha: float) -> str:
        """Return an RGBA tuple from hex + alpha (for Canvas)."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f'#{int(r * alpha):02x}{int(g * alpha):02x}{int(b * alpha):02x}'

    @classmethod
    def linear(cls, color_a: str, color_b: str, t: float) -> str:
        """Lerp between two hex colors at t ∈ [0, 1]."""
        t = max(0, min(1, t))
        r1, g1, b1 = int(color_a[1:3], 16), int(color_a[3:5], 16), int(color_a[5:7], 16)
        r2, g2, b2 = int(color_b[1:3], 16), int(color_b[3:5], 16), int(color_b[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f'#{r:02x}{g:02x}{b:02x}'

    @classmethod
    def alpha(cls, hex_color: str, alpha: float) -> str:
        """Return modified hex with applied alpha (multiplied into RGB)."""
        return cls.linear(hex_color, '#000000', 1 - alpha)

    @classmethod
    def text_color(cls, bg_hex: str) -> str:
        """Return black or white text color depending on bg brightness."""
        r = int(bg_hex[1:3], 16)
        g = int(bg_hex[3:5], 16)
        b = int(bg_hex[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return '#ffffff' if luminance < 0.5 else '#000000'
