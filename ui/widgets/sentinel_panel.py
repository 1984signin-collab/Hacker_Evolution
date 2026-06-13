#!/usr/bin/env python3
"""Canvas-drawn Sentinel AI panel with animated threat states."""

from __future__ import annotations

import math
import time
import tkinter as tk

from ui.theme import Theme


class SentinelPanel:
    """Sentinel AI status panel drawn on Canvas.

    States:
        IDLE      — cyan, scanning bars
        ANALYZING — amber, pulse glow
        ACTIVE    — red, aggressive pulse + shake
    """

    HEIGHT = 100

    def __init__(self, canvas: tk.Canvas, x: int, y: int, width: int = 300):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = width
        self.h = self.HEIGHT
        self.tag = f'_sentinel_{id(self)}'
        self._state = 'IDLE'
        self._anim_frame = 0
        self._draw()

    def set_state(self, state: str):
        """Set state: IDLE, ANALYZING, or ACTIVE."""
        if state != self._state:
            self._state = state
            self.redraw()

    def redraw(self):
        self.canvas.delete(self.tag)
        self._draw()

    def _draw(self):
        c = self.canvas
        t = self.tag

        # Background
        c.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h,
                           fill=Theme.BG_SURFACE, outline=Theme.CYAN_ULTRADIM,
                           width=1, tags=t)

        # Section header
        c.create_text(self.x + 8, self.y + 6,
                      text='[ SENTINEL AI ]', fill=Theme.CYAN_MID,
                      font=Theme.FONT_HEADER, anchor='w', tags=t)

        # State-dependent colors
        if self._state == 'ACTIVE':
            col = Theme.RED
            status = 'ACTIVE'
            secondary = Theme.RED_DIM
        elif self._state == 'ANALYZING':
            col = Theme.AMBER
            status = 'ANALYZING'
            secondary = Theme.CYAN_ULTRADIM
        else:
            col = Theme.CYAN
            status = 'MONITORING'
            secondary = Theme.CYAN_ULTRADIM

        # Status label
        c.create_text(self.x + self.w - 8, self.y + 6,
                      text=status, fill=col,
                      font=Theme.FONT_LOG_TIME, anchor='e', tags=t)

        # Scan line animation
        mid_y = self.y + 50
        for i in range(8):
            bar_h = 4 + 16 * abs(math.sin(i + self._anim_frame * 0.3))
            bar_x = self.x + 20 + i * 22
            c.create_rectangle(bar_x, mid_y - bar_h // 2,
                               bar_x + 8, mid_y + bar_h // 2,
                               fill=col if i % 2 == 0 else secondary,
                               outline='', tags=t)

        # Threat level bar
        bar_y = self.y + 75
        c.create_text(self.x + 8, bar_y,
                      text='THREAT', fill=Theme.TEXT_DIM,
                      font=('Consolas', 7), anchor='w', tags=t)

        # Empty bar bg
        c.create_rectangle(self.x + 60, bar_y - 4,
                           self.x + self.w - 8, bar_y + 6,
                           fill=Theme.BG_VOID, outline=Theme.CYAN_ULTRADIM,
                           width=1, tags=t)

        # Filled bar — width based on state
        if self._state == 'ACTIVE':
            fill_w = self.w - 68
        elif self._state == 'ANALYZING':
            fill_w = (self.w - 68) * 0.6
        else:
            fill_w = (self.w - 68) * 0.15

        c.create_rectangle(self.x + 61, bar_y - 3,
                           self.x + 61 + int(fill_w), bar_y + 5,
                           fill=col, outline='', tags=t)

    def animate(self):
        self._anim_frame += 1
        self.redraw()
