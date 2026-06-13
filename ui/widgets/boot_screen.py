#!/usr/bin/env python3
"""Canvas-drawn boot screen with typing animation — 6s total."""

from __future__ import annotations

import math
import random
import tkinter as tk

from ui.theme import Theme


class BootScreen:
    """Full-screen Canvas boot animation.

    Phases (6s total):
        0-2s:  Fade in HACKER ASCII art with glow
        2-5s:  Typing boot messages (cyan/teal on black)
        5-6s:  Glitch transition → callback
    """

    def __init__(self, root: tk.Tk, callback):
        self.root = root
        self.callback = callback
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()

        self.win = tk.Toplevel(root)
        self.win.title('Boot')
        self.win.geometry(f'{sw}x{sh}+0+0')
        self.win.overrideredirect(True)
        self.win.configure(bg=Theme.BG_VOID)

        self.c = tk.Canvas(self.win, width=sw, height=sh,
                           bg=Theme.BG_VOID, highlightthickness=0)
        self.c.pack(fill=tk.BOTH, expand=True)
        self.w = sw
        self.h = sh
        self._frame = 0
        self._phase = 0
        self._messages = [
            ('[    0.000] kernel: HACKER EVOLUTION v2.0 — Darius Protocol', Theme.CYAN_ULTRADIM),
            ('[    0.250] kernel: CPU cores detected: 24 @ 5.8 GHz', Theme.TEXT_DIM),
            ('[    0.510] kernel: Memory: 64 GiB DDR5 ECC', Theme.TEXT_DIM),
            ('[    0.800] net:   Interface eth0 — MAC: 0A:1B:2C:3D:4E:5F', Theme.TEXT_DIM),
            ('[    1.100] net:   ip: 192.168.17.42/24 — gateway: 192.168.17.1', Theme.TEXT_DIM),
            ('[    1.400] sec:   WARNING: /tmp/recovery.key — encryption active', Theme.AMBER),
            ('[    1.700] sec:   NOTICE: recovery.key — valid passphrase found', Theme.GREEN),
            ('[    2.000] sys:   Loading Darius.OWC credentials...', Theme.CYAN_DIM),
            ('[    2.300] sys:   Legacy terminal access granted', Theme.GREEN),
            ('[    2.600] net:   Scanning subnet — 2 hosts: secure.corp, nexus.owc', Theme.TEXT_DIM),
            ('[    2.900] sec:   Last login: hacker — 14d ago — IP masked', Theme.CYAN_ULTRADIM),
            ('[    3.200] sys:   Darius connection interrupted — timeout', Theme.AMBER),
            ('[    3.500] sys:   Switching to offline mode', Theme.CYAN_DIM),
            ('[    3.800] sys:   Starting console...', Theme.TEXT_DIM),
        ]
        self._msg_idx = 0
        self._typed_len = 0
        self._msg_text = ''
        self._cx = sw // 2
        self._cy = sh // 2
        self._run()

    def _run(self):
        if not self.win.winfo_exists():
            return
        if self._frame < 120:
            self._phase0_splash()
        elif self._frame < 300:
            self._phase1_messages()
        elif self._frame < 330:
            self._phase2_transition_glitch()
        else:
            self._phase2_transition_done()
            return
        self._frame += 1
        self.win.after(16, self._run)

    def _phase0_splash(self):
        p = min(1, self._frame / 60)
        self.c.delete('splash')

        # ASCII HACKER art
        art = [
            r' ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ ',
            r' ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗',
            r' ███████║███████║██║     █████╔╝ █████╗  ██████╔╝',
            r' ██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗',
            r' ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║',
            r' ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝',
        ]
        cy_offset = -80
        glow_alpha = 0.15 + 0.1 * math.sin(self._frame * 0.08)
        for layer in range(4, 0, -1):
            alpha = glow_alpha * (layer / 4) * p
            for i, line in enumerate(art):
                self.c.create_text(self._cx + layer * 2, self._cy + cy_offset + i * 22 + layer * 2,
                                   text=line, fill=Theme.rgba(Theme.CYAN, alpha),
                                   font=('Consolas', 14, 'bold'), anchor='center', tags='splash')
        for i, line in enumerate(art):
            self.c.create_text(self._cx, self._cy + cy_offset + i * 22,
                               text=line, fill=Theme.rgba(Theme.TEXT, p * 0.7),
                               font=('Consolas', 14, 'bold'), anchor='center', tags='splash')
            self.c.create_text(self._cx, self._cy + cy_offset + i * 22,
                               text=line, fill=Theme.rgba(Theme.CYAN, p * 0.9),
                               font=('Consolas', 14, 'bold'), anchor='center', tags='splash')

        # Subtitle
        if p > 0.5:
            subtitle = 'HACKER EVOLUTION — Darius Protocol'
            sub_alpha = (p - 0.5) * 2
            self.c.create_text(self._cx, self._cy + 70,
                               text=subtitle, fill=Theme.rgba(Theme.CYAN_MID, sub_alpha),
                               font=('Consolas', 10), anchor='center', tags='splash')

    def _phase1_messages(self):
        self.c.delete('splash')
        self.c.delete('msg')

        # Start showing messages after frame 120
        msg_start = 120
        msg_interval = 12
        visible_count = (self._frame - msg_start) // msg_interval

        y_start = self._cy - 40
        for i in range(min(visible_count + 1, len(self._messages))):
            text, col = self._messages[i]
            y = y_start + i * 18
            self.c.create_text(self._cx - 280, y, text=text,
                               fill=col, font=('Consolas', 9), anchor='w', tags='msg')

        # Cursor blink
        if visible_count >= len(self._messages):
            blink = 0.5 + 0.5 * math.sin(self._frame * 0.15)
            if blink > 0.5:
                self.c.create_text(self._cx - 280, y_start + len(self._messages) * 18,
                                   text='_', fill=Theme.CYAN,
                                   font=('Consolas', 9), anchor='w', tags='msg')

    def _phase2_transition_glitch(self):
        self.c.delete('msg')
        self.c.delete('splash')

        for _ in range(12):
            y = self.c.winfo_height() * (0.1 + 0.8 * (_ / 12))
            h = random.randint(2, 8)
            self.c.create_rectangle(0, y, self.w, y + h,
                                    fill=Theme.rgba(Theme.CYAN, 0.3 + 0.4 * random.random()),
                                    outline='')

        flash_alpha = 0.3 * max(0, 1 - (self._frame - 300) / 20)
        self.c.create_rectangle(0, 0, self.w, self.h,
                                fill=Theme.rgba(Theme.CYAN, flash_alpha),
                                outline='')

    def _phase2_transition_done(self):
        self.win.destroy()
        self.callback()
