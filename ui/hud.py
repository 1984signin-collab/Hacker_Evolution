#!/usr/bin/env python3
# HACKER EVOLUTION — HUD Background
# Matrix rain, vignetta animata, effetti CRT e synthwave sunset.

import math
import random
import tkinter as tk

from engine.config import Colors, KATA


class HUDBackground:
    """Full-screen HUD background with animated matrix rain, CRT effects,
    synthwave sunset, vignette, and data-flow particles."""

    def __init__(self, parent, bg='#060d1a'):
        self.canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.running = True
        self._anim_frame = 0
        self._data_drops = []
        self._kata_drops = []
        self._noise_pixels = []
        self.canvas.bind('<Configure>', lambda e: self._resize())
        self._redraw()
        self._animate()

    def _resize(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w > 20:
            self._data_drops = [
                {'x': random.randint(0, w), 'y': random.randint(-h, 0),
                 'speed': random.uniform(2, 6), 'len': random.randint(5, 15)}
                for _ in range(max(2, w // 150))
            ]
            self._kata_drops = [
                {'x': random.randint(0, w), 'y': random.randint(-h, 0),
                 'speed': random.uniform(1, 3), 'len': random.randint(8, 20),
                 'chars': [random.choice(KATA) for _ in range(20)]}
                for _ in range(max(5, w // 60))
            ]

    def _animate(self):
        if not self.running:
            return
        self._anim_frame += 1
        self.canvas.delete('vignette')
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w > 20 and h > 20:
            # Animated vignette border
            for i in range(6):
                a = 1 - i / 6
                p = 0.5 + 0.5 * math.sin(self._anim_frame / 30 + i)
                c = f'#{int(8 * a):02x}{int(15 * a + 5 * p):02x}{int(25 * a + 10 * p):02x}'
                self.canvas.create_rectangle(i, i, w - i, h - i,
                                             outline=c, width=1, tags='vignette')

            # Data rain (hexadecimal drops)
            for d in self._data_drops:
                d['y'] += d['speed']
                if d['y'] > h:
                    d['y'] = random.randint(-50, 0)
                    d['x'] = random.randint(0, w)
                    d['speed'] = random.uniform(2, 6)
                for j in range(d['len']):
                    yy = d['y'] - j * 8
                    b = max(0.05, 1 - j / d['len'])
                    if 0 < yy < h:
                        self.canvas.create_text(
                            d['x'], yy,
                            text=random.choice('0123456789ABCDEF'),
                            fill=f'#{int(10 + 50 * b):02x}{int(20 + 80 * b):02x}{int(40 + 160 * b):02x}',
                            font=('Consolas', 6), tags='vignette',
                        )

            # Katakana matrix rain (green/purple cyberpunk style)
            for d in self._kata_drops:
                d['y'] += d['speed']
                if d['y'] > h:
                    d['y'] = random.randint(-80, 0)
                    d['x'] = random.randint(0, w)
                    d['speed'] = random.uniform(1, 3)
                    d['chars'] = [random.choice(KATA) for _ in range(20)]
                for j in range(d['len']):
                    yy = d['y'] - j * 12
                    b = max(0.05, 1 - j / d['len'])
                    if 0 < yy < h:
                        ch = d['chars'][j % len(d['chars'])]
                        bright = int(20 + 180 * b)
                        r = min(255, int(5 * bright))
                        g = min(255, bright)
                        bv = min(255, int(bright * 0.6))
                        self.canvas.create_text(
                            d['x'], yy, text=ch,
                            fill=f'#{r:02x}{g:02x}{bv:02x}',
                            font=('Consolas', 11), tags='vignette',
                        )
                        # Leading character is bright white/cyan
                        if j == 0:
                            r2 = min(255, int(50 + 200 * b))
                            g2 = min(255, int(200 + 55 * b))
                            b2 = min(255, 255)
                            self.canvas.create_text(
                                d['x'], yy, text=ch,
                                fill=f'#{r2:02x}{g2:02x}{b2:02x}',
                                font=('Consolas', 11, 'bold'), tags='vignette',
                            )

            # CRT noise pixels
            if random.random() < 0.3:
                for _ in range(random.randint(1, 5)):
                    nx, ny = random.randint(0, w - 2), random.randint(0, h - 2)
                    b = random.random() * 0.3
                    self.canvas.create_rectangle(
                        nx, ny, nx + 1, ny + 1,
                        fill=f'#{int(80 * b):02x}{int(160 * b):02x}{int(200 * b):02x}',
                        outline='', tags='vignette',
                    )
        self.canvas.after(200, self._animate)

    def _redraw(self):
        self.canvas.delete('all')
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 20 or h < 20:
            return

        # Vignette — dark edges
        for i in range(5):
            a = 1 - i / 5
            c = f'#{int(8 * a):02x}{int(10 * a):02x}{int(25 * a):02x}'
            self.canvas.create_rectangle(i, i, w - i, h - i,
                                         outline=c, width=1, tags='vignette')

        # Synthwave sunset
        sun_cx, sun_cy = w // 2, int(h * 0.85)
        sun_r = int(h * 0.35)
        for i in range(35, 0, -1):
            r = sun_r * i / 35
            frac = i / 35
            rr = int(255 * frac)
            gg = int(100 * frac * max(0, 1 - frac * 1.5))
            bb = int(50 * frac * (1 - frac))
            self.canvas.create_oval(
                sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r,
                outline='', fill=f'#{rr:02x}{gg:02x}{bb:02x}', tags='sun',
            )

        # Horizontal horizon lines
        for li in range(5, 40, 5):
            ly = sun_cy + li * 3
            if ly > h:
                break
            bright = 0.1 + 0.9 * (1 - li / 40)
            self.canvas.create_line(
                0, ly, w, ly,
                fill=f'#{int(255 * bright):02x}{int(100 * bright):02x}{int(200 * bright * 0.3):02x}',
                width=2, tags='sun',
            )
        self.canvas.lower('sun')

        # Animated grid
        gs = 40
        t = self._anim_frame * 0.02
        for x in range(0, w, gs):
            bright = (0.06 + 0.05 * math.sin(x / 80 + t)
                      + 0.03 * math.sin(x / 30 - t * 2))
            self.canvas.create_line(
                x, 0, x, h,
                fill=f'#0a{int(20 * bright):02x}{int(40 * bright):02x}',
                width=1, tags='hud',
            )
        for y in range(0, h, gs):
            bright = (0.06 + 0.05 * math.sin(y / 80 + t)
                      + 0.03 * math.sin(y / 30 + t * 1.5))
            self.canvas.create_line(
                0, y, w, y,
                fill=f'#0a{int(20 * bright):02x}{int(40 * bright):02x}',
                width=1, tags='hud',
            )

        # Double corner brackets with glow
        for br, inset, l, alpha in [
            (20, 8, 28, 1), (24, 4, 32, 0.3),
        ]:
            for x, y, dx, dy in [
                (inset, inset, 1, 1),
                (w - inset, inset, -1, 1),
                (inset, h - inset, 1, -1),
                (w - inset, h - inset, -1, -1),
            ]:
                col = f'#{int(alpha * 30):02x}{int(180 + alpha * 75):02x}{int(255):02x}'
                self.canvas.create_line(x, y, x + dx * l, y,
                                        fill=col, width=2, tags='hud')
                self.canvas.create_line(x, y, x, y + dy * l,
                                        fill=col, width=2, tags='hud')
                if alpha == 1:
                    self.canvas.create_line(
                        x + dx * 2, y, x + dx * l // 2, y,
                        fill=Colors.cyan, width=4, tags='hud',
                    )
                    self.canvas.create_line(
                        x, y + dy * 2, x, y + dy * l // 2,
                        fill=Colors.cyan, width=4, tags='hud',
                    )

        # Scanlines
        for y in range(2, h, 4):
            self.canvas.create_line(0, y, w, y, fill='#000000',
                                    width=1, stipple='gray25', tags='hud')
        self.canvas.lower('hud')
