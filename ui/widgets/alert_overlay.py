#!/usr/bin/env python3
"""Canvas-drawn alert overlay for warnings, errors, and notifications."""

from __future__ import annotations

import math
import tkinter as tk

from ui.theme import Theme


class AlertOverlay:
    """Semi-transparent overlay with animated alert.

    Types:
        warning — amber border, CYAN text
        error   — red border, red text
        info    — cyan border, muted text
        success — green border, green text
    """

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self._active = False
        self._frame = 0
        self._type = 'info'
        self._message = ''
        self._duration = 0
        self._callback = None

    @property
    def _colors(self):
        if self._type == 'error':
            return dict(accent=Theme.RED, dim=Theme.RED_DIM, text=Theme.RED)
        elif self._type == 'warning':
            return dict(accent=Theme.AMBER, dim=Theme.CYAN_ULTRADIM, text=Theme.AMBER)
        elif self._type == 'success':
            return dict(accent=Theme.GREEN, dim=Theme.CYAN_ULTRADIM, text=Theme.GREEN)
        else:
            return dict(accent=Theme.CYAN, dim=Theme.CYAN_ULTRADIM, text=Theme.CYAN_MID)

    def show(self, message: str, type_: str = 'info', duration: int = 3000, callback=None):
        self._message = message
        self._type = type_
        self._duration = duration
        self._callback = callback
        self._active = True
        self._frame = 0

    def animate(self):
        if not self._active:
            return
        self._frame += 1
        self._draw()

    def _draw(self):
        c = self.canvas
        w = c.winfo_width() or 800
        h = c.winfo_height() or 600
        cols = self._colors
        ts = self._frame
        t = ts * 16  # time approx in ms

        self.canvas.delete('alert')

        # Background dim overlay
        if ts < 10:
            alpha = ts / 10 * 0.5
        elif t < self._duration:
            alpha = 0.5
        else:
            alpha = max(0, 0.5 * (1 - (t - self._duration) / 500))
        if alpha <= 0:
            self._active = False
            if self._callback:
                self._callback()
            return

        c.create_rectangle(0, 0, w, h,
                           fill=Theme.rgba(Theme.BG_VOID, alpha * 0.6),
                           outline='', tags='alert')

        # Panel dimensions
        pw, ph = min(500, w - 80), 140
        px, py = (w - pw) // 2, (h - ph) // 2

        # Outer glow
        pulse = 0.5 + 0.5 * math.sin(ts * 0.08)
        glow_alpha = 0.1 + 0.15 * pulse
        c.create_rectangle(px - 4, py - 4, px + pw + 4, py + ph + 4,
                           outline=Theme.rgba(cols['accent'], glow_alpha),
                           width=3, tags='alert')

        # Panel bg
        c.create_rectangle(px, py, px + pw, py + ph,
                           fill=Theme.BG_SURFACE,
                           outline=cols['accent'],
                           width=1, tags='alert')

        # Type label
        c.create_text(px + 16, py + 14,
                      text=self._type.upper(),
                      fill=cols['accent'],
                      font=('Consolas', 8, 'bold'), anchor='w', tags='alert')

        # Animated corner brackets
        bracket_len = 16
        for ox, oy, dx, dy in [(2, 2, 1, 0), (2, 2, 0, 1),
                               (pw - 2, 2, -1, 0), (pw - 2, 2, 0, 1),
                               (2, ph - 2, 1, 0), (2, ph - 2, 0, -1),
                               (pw - 2, ph - 2, -1, 0), (pw - 2, ph - 2, 0, -1)]:
            bc = Theme.rgba(cols['accent'], 0.3 + 0.7 * pulse)
            bw = 2 if self._type == 'error' else 1
            c.create_line(px + ox, py + oy,
                          px + ox + dx * bracket_len, py + oy + dy * bracket_len,
                          fill=bc, width=bw, tags='alert')

        # Icon area
        icon = '!' if self._type == 'error' else 'i'
        c.create_oval(px + 20, py + 38, px + 48, py + 66,
                      outline=cols['accent'], width=1, tags='alert')
        c.create_text(px + 34, py + 52,
                      text=icon, fill=cols['accent'],
                      font=('Consolas', 14, 'bold'), anchor='center', tags='alert')

        # Message
        c.create_text(px + 60, py + 52,
                      text=self._message, fill=cols['text'],
                      font=('Consolas', 10), anchor='w', width=pw - 80, tags='alert')

        # Progress bar at bottom
        if t < self._duration:
            pct = t / self._duration
            bar_w = pw - 20
            c.create_rectangle(px + 10, py + ph - 10,
                               px + 10 + int(bar_w * (1 - pct)), py + ph - 4,
                               fill=cols['accent'], outline='', tags='alert')
