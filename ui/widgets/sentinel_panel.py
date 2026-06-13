#!/usr/bin/env python3
"""Canvas-drawn Sentinel AI panel with animated threat states."""

from __future__ import annotations

import math
import tkinter as tk

from ui.theme import Theme


class SentinelPanel:
    """Sentinel AI status panel drawn on Canvas.

    States:
        IDLE      — cyan dim, scan bars scroll slowly
        ANALYZING — amber, pulse glow, bars faster
        ACTIVE    — red, aggressive pulse + corner flash
    """

    HEIGHT = 84

    def __init__(self, canvas: tk.Canvas, x: int, y: int, width: int = 300):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = width
        self.h = self.HEIGHT
        self.tag = f'_sentinel_{id(self)}'
        self._state = 'IDLE'
        self._anim_frame = 0
        self._pulse_phase = 0.0
        self._draw()

    @property
    def _state_colors(self):
        if self._state == 'ACTIVE':
            return dict(col=Theme.RED, dim=Theme.RED_DIM, label='ACTIVE')
        elif self._state == 'ANALYZING':
            return dict(col=Theme.AMBER, dim=Theme.CYAN_ULTRADIM, label='ANALYZING')
        else:
            return dict(col=Theme.CYAN, dim=Theme.CYAN_ULTRADIM, label='MONITORING')

    def set_state(self, state: str):
        if state != self._state:
            self._state = state
            self.redraw()

    def redraw(self):
        self.canvas.delete(self.tag)
        self._draw()

    def _draw(self):
        c = self.canvas
        t = self.tag
        sc = self._state_colors
        col = sc['col']
        dim = sc['dim']
        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)
        flash = 0.3 + 0.7 * math.sin(self._pulse_phase * 2) if self._state == 'ACTIVE' else 0

        # Outer glow ring (drawn behind panel)
        glow_pad = 6
        glow_alpha = 0.08 + 0.12 * pulse if self._state == 'ACTIVE' else 0.05
        glow_col = Theme.rgba(col, glow_alpha)
        c.create_rectangle(self.x - glow_pad, self.y - glow_pad,
                           self.x + self.w + glow_pad, self.y + self.h + glow_pad,
                           outline=glow_col, width=2, tags=t)

        # Background
        c.create_rectangle(self.x, self.y, self.x + self.w, self.y + self.h,
                           fill=Theme.BG_SURFACE, outline=dim,
                           width=1, tags=t)

        # Corner brackets — pulse on ACTIVE
        bracket_len = 12
        bw = 2 if self._state == 'ACTIVE' else 1
        bc = Theme.rgba(col, 0.4 + 0.6 * pulse) if self._state != 'IDLE' else col
        for ox, oy, dx, dy in [(1, 1, 1, 0), (1, 1, 0, 1),
                               (self.w - 1, 1, -1, 0), (self.w - 1, 1, 0, 1),
                               (1, self.h - 1, 1, 0), (1, self.h - 1, 0, -1),
                               (self.w - 1, self.h - 1, -1, 0), (self.w - 1, self.h - 1, 0, -1)]:
            x0 = self.x + ox + (0 if dx != 0 else (0 if dx < 0 else 0))
            y0 = self.y + oy + (0 if dy != 0 else (0 if dy < 0 else 0))
            c.create_line(self.x + ox, self.y + oy,
                          self.x + ox + dx * bracket_len, self.y + oy + dy * bracket_len,
                          fill=bc, width=bw, tags=t)

        # Section header
        c.create_text(self.x + 8, self.y + 6,
                      text='[ SENTINEL AI ]', fill=Theme.CYAN_MID,
                      font=Theme.FONT_HEADER, anchor='w', tags=t)

        # Status label — with glow on ACTIVE
        if self._state == 'ACTIVE':
            for i in range(3):
                alpha = 0.1 + 0.15 * (1 - i / 3) * pulse
                c.create_text(self.x + self.w - 8 + i * 2, self.y + 6,
                              text=sc['label'], fill=Theme.rgba(col, alpha),
                              font=Theme.FONT_LOG_TIME, anchor='e', tags=t)
        c.create_text(self.x + self.w - 8, self.y + 6,
                      text=sc['label'], fill=col,
                      font=Theme.FONT_LOG_TIME, anchor='e', tags=t)

        # Scan bars — state-dependent pattern
        mid_y = self.y + 48
        bar_count = 8
        bar_spacing = (self.w - 40) // (bar_count - 1)
        for i in range(bar_count):
            if self._state == 'ACTIVE':
                h_normal = 4 + 16 * abs(math.sin(i * 1.2 + self._anim_frame * 0.4))
                bar_w = 6 + 4 * abs(math.sin(self._anim_frame * 0.2))
            elif self._state == 'ANALYZING':
                h_normal = 4 + 14 * (0.5 + 0.5 * math.sin(i * 0.8 + self._anim_frame * 0.25))
                bar_w = 8
            else:
                h_normal = 4 + 10 * (0.5 + 0.5 * math.sin(i * 0.5 + self._anim_frame * 0.12))
                bar_w = 8
            bar_x = self.x + 20 + i * bar_spacing
            bar_bright = 0.5 + 0.5 * abs(math.sin(i + self._anim_frame * 0.15))
            bar_fill = Theme.rgba(col, bar_bright) if i % 2 == 0 else dim
            c.create_rectangle(bar_x - bar_w // 2, mid_y - h_normal // 2,
                               bar_x + bar_w // 2, mid_y + h_normal // 2,
                               fill=bar_fill, outline='', tags=t)

        # Pulsing data dots (horizontal flow)
        dot_y = mid_y + 18
        for i in range(12):
            offset = (self._anim_frame * (1.5 if self._state == 'ACTIVE' else 0.8)) % 24
            dot_x = self.x + 10 + ((i * 18 - offset) % (self.w - 20))
            dot_alpha = 0.1 + 0.4 * (1 - abs(i - offset / 2) / 12) if abs(i - offset / 2) < 6 else 0.1
            c.create_oval(dot_x - 1, dot_y - 1, dot_x + 1, dot_y + 1,
                          fill=Theme.rgba(col, dot_alpha), outline='', tags=t)

        # Threat level bar
        bar_y = self.y + self.h - 22
        c.create_text(self.x + 8, bar_y,
                      text='THREAT', fill=Theme.TEXT_DIM,
                      font=('Consolas', 7), anchor='w', tags=t)

        # Threat bar bg
        c.create_rectangle(self.x + 60, bar_y - 4,
                           self.x + self.w - 8, bar_y + 6,
                           fill=Theme.BG_VOID, outline=dim,
                           width=1, tags=t)

        # Filled threat — animated width
        if self._state == 'ACTIVE':
            base_pct = 0.85 + 0.15 * pulse
        elif self._state == 'ANALYZING':
            base_pct = 0.55 + 0.15 * pulse
        else:
            base_pct = 0.1 + 0.1 * pulse
        fill_w = (self.w - 68) * base_pct
        c.create_rectangle(self.x + 61, bar_y - 3,
                           self.x + 61 + int(fill_w), bar_y + 5,
                           fill=col, outline='', tags=t)

        # Threat percentage text
        pct = int(base_pct * 100)
        c.create_text(self.x + self.w - 8, bar_y,
                      text=f'{pct}%', fill=col,
                      font=('Consolas', 7), anchor='e', tags=t)

    def animate(self):
        self._anim_frame += 1
        self._pulse_phase += 0.08 if self._state == 'ACTIVE' else 0.04
        self.redraw()
