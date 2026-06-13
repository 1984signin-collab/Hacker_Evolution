#!/usr/bin/env python3
"""Canvas-based stat card for cyberpunk HUD panels."""

from __future__ import annotations

import tkinter as tk

from ui.theme import Theme


class CanvasStatCard:
    """A stat card drawn entirely on a tkinter Canvas.

    Each card shows a LABEL (dim text) and a VALUE (bright text)
    with optional bottom accent bar and glow.
    """

    WIDTH = 160
    HEIGHT = 64

    def __init__(self, canvas: tk.Canvas, x: int, y: int,
                 label: str, value: str,
                 color: str = Theme.CYAN,
                 width: int = 160, height: int = 64):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.label = label
        self._value = value
        self.color = color
        self._tags = set()
        self._draw()

    def _draw(self):
        t = f'_card_{id(self)}'
        self._tags.add(t)
        c = self.canvas

        # Background rect
        c.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h,
                           fill=Theme.BG_SURFACE, outline=Theme.CYAN_ULTRADIM,
                           width=1, tags=t)

        # Top accent line
        c.create_line(self.x + 4, self.y + 2, self.x + self.w - 4, self.y + 2,
                      fill=self.color, width=2, tags=t)

        # Label
        c.create_text(self.x + self.w // 2, self.y + 18,
                      text=self.label, fill=Theme.TEXT_DIM,
                      font=Theme.FONT_STAT_LABEL, tags=t)

        # Value
        c.create_text(self.x + self.w // 2, self.y + self.h - 16,
                      text=self._value, fill=self.color,
                      font=Theme.FONT_STAT_VALUE, tags=t)

    def update(self, value: str, color: str | None = None):
        t = f'_card_{id(self)}'
        self._value = value
        if color:
            self.color = color
        self.canvas.delete(t)
        self._draw()

    def show(self):
        t = f'_card_{id(self)}'
        self.canvas.itemconfigure(t, state='normal')

    def hide(self):
        t = f'_card_{id(self)}'
        self.canvas.itemconfigure(t, state='hidden')

    def delete(self):
        self.canvas.delete(f'_card_{id(self)}')


class CanvasSectionHeader:
    """Section header bar drawn on Canvas."""

    def __init__(self, canvas: tk.Canvas, x: int, y: int,
                 text: str, width: int = 300, color: str = Theme.CYAN_MID):
        self.canvas = canvas
        self.tag = f'_hdr_{id(self)}'
        self.x = x
        self.y = y
        self.w = width
        self.color = color

        # Left bracket
        canvas.create_text(x + 4, y, text='[', fill=color,
                           font=Theme.FONT_HEADER, anchor='w', tags=self.tag)
        # Label
        canvas.create_text(x + 14, y, text=text, fill=color,
                           font=Theme.FONT_HEADER, anchor='w', tags=self.tag)
        # Right bracket
        lbl_w = 14 + len(text) * 8
        canvas.create_text(x + lbl_w, y, text=']', fill=color,
                           font=Theme.FONT_HEADER, anchor='w', tags=self.tag)
        # Line
        canvas.create_line(x + lbl_w + 10, y + 5, x + width, y + 5,
                           fill=Theme.CYAN_ULTRADIM, width=1, tags=self.tag)

    def delete(self):
        self.canvas.delete(self.tag)
