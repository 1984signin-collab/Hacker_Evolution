#!/usr/bin/env python3
"""Canvas-drawn network map with enhanced visual effects."""

from __future__ import annotations

import math
import random
import time
import tkinter as tk

from ui.theme import Theme
from engine.game import g


class NetworkMapRenderer:
    """Renders the network map with glow nodes, data flow, and sweep radar.

    Callbacks:
        on_click(name, x, y)  — left-click node
        on_right_click(name, x, y, e)  — right-click node
    """

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self._anim_frame = 0
        self._data_packets: list[dict] = []
        self._particles: list[dict] = []

    def set_callbacks(self, on_click=None, on_right_click=None):
        self.on_click = on_click
        self.on_right_click = on_right_click

    def draw(self):
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 160
        n = len(g.servers)
        if n == 0:
            return

        self.canvas.delete('all')
        cx, cy = w // 2, h // 2
        radius = min(w, h) * 0.35

        self._draw_radar_grid(cx, cy, radius)
        self._position_nodes(cx, cy, radius, n)
        self._draw_radar_sweep(cx, cy, radius)
        self._draw_connections(n)
        self._draw_bounce_chain()
        self._update_data_packets()
        self._draw_data_packets()
        self._draw_nodes()
        self._update_particles()
        self._draw_particles()
        self._draw_compromised_data(cx, cy)
        self._draw_map_status(n)
        self._anim_frame += 1

    def _draw_radar_grid(self, cx, cy, radius):
        c = self.canvas
        step_ = max(1, int(radius * 0.25))
        for rng in range(step_, int(radius) + 1, step_):
            c.create_oval(cx - rng, cy - rng, cx + rng, cy + rng,
                          outline=Theme.CYAN_ULTRADIM, width=1)
        for a in [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4]:
            dx = radius * math.cos(a)
            dy = radius * math.sin(a)
            c.create_line(cx - dx, cy - dy, cx + dx, cy + dy,
                          fill=Theme.CYAN_ULTRADIM, width=1)
        c.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                      fill=Theme.CYAN_DIM, outline='')

    def _position_nodes(self, cx, cy, radius, n):
        for i, s in enumerate(g.servers):
            a = 2 * math.pi * i / n - math.pi / 2
            x = cx + radius * math.cos(a)
            y = cy + radius * math.sin(a)
            s['pos'] = (x, y)

    def _draw_radar_sweep(self, cx, cy, radius):
        c = self.canvas
        angle = self._anim_frame * 0.02
        rx = cx + radius * math.cos(angle)
        ry = cy + radius * math.sin(angle)
        for ri in range(20, 0, -1):
            alpha = 0.12 * (1 - ri / 20)
            a2 = angle - 0.03 * ri
            rrx = cx + radius * 0.3 * math.cos(a2)
            rry = cy + radius * 0.3 * math.sin(a2)
            c.create_line(cx, cy, rrx, rry,
                          fill=Theme.rgba(Theme.CYAN, alpha),
                          width=ri // 4 + 1)
        c.create_line(cx, cy, rx, ry, fill=Theme.CYAN, width=2)
        self.canvas.after(500, lambda: self.canvas.delete('radar_sweep'))

    def _draw_connections(self, n):
        c = self.canvas
        now_t = time.time()
        for i, s1 in enumerate(g.servers):
            x1, y1 = s1['pos']
            for j in range(i + 1, n):
                x2, y2 = g.servers[j]['pos']
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                steps = max(1, int(dist / 8))
                for s in range(steps):
                    t1, t2 = s / steps, (s + 1) / steps
                    bright = 0.1 + 0.15 * math.sin(t1 * math.pi)
                    c.create_line(x1 + dx * t1, y1 + dy * t1,
                                  x1 + dx * t2, y1 + dy * t2,
                                  fill=f'#{int(15 * bright):02x}'
                                       f'{int(40 * bright):02x}'
                                       f'{int(40 * bright):02x}',
                                  width=1)

        # Animated data packets along random connections
        if self._anim_frame % 6 == 0:
            i = random.randrange(n)
            j = random.randrange(n)
            if i != j:
                x1, y1 = g.servers[i]['pos']
                x2, y2 = g.servers[j]['pos']
                self._data_packets.append({
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                    't': 0.0, 'speed': 0.02 + random.random() * 0.03,
                })

    def _draw_bounce_chain(self):
        c = self.canvas
        chain = g.bounce_chain
        for bi in range(1, len(chain)):
            h1, h2 = chain[bi - 1], chain[bi]
            p1 = next((s for s in g.servers if s['name'] == h1), None)
            p2 = next((s for s in g.servers if s['name'] == h2), None)
            if not p1 or not p2:
                continue
            x1, y1 = p1['pos']
            x2, y2 = p2['pos']

            # Mission-critical path: thick glow + bright line
            c.create_line(x1, y1, x2, y2, fill=Theme.CYAN_ULTRADIM, width=7)
            c.create_line(x1, y1, x2, y2, fill=Theme.CYAN_MID, width=3)
            c.create_line(x1, y1, x2, y2, fill=Theme.CYAN, width=1)

            # Animated dot along bounce path
            t = (self._anim_frame * 0.015) % 1
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            sz = 2 + int(1.5 * (0.5 + 0.5 * math.sin(self._anim_frame * 0.2)))
            c.create_oval(px - sz, py - sz, px + sz, py + sz,
                          fill=Theme.CYAN, outline=Theme.rgba(Theme.TEXT, 0.3),
                          width=1)

    def _update_data_packets(self):
        alive = []
        for pkt in self._data_packets:
            pkt['t'] += pkt['speed']
            if pkt['t'] <= 1.0:
                alive.append(pkt)
        self._data_packets = alive

    def _draw_data_packets(self):
        c = self.canvas
        for pkt in self._data_packets:
            t = pkt['t']
            px = pkt['x1'] + (pkt['x2'] - pkt['x1']) * t
            py = pkt['y1'] + (pkt['y2'] - pkt['y1']) * t
            brightness = 0.3 + 0.7 * math.sin(t * math.pi)
            sz = 1 + int(brightness * 2)
            c.create_oval(px - sz, py - sz, px + sz, py + sz,
                          fill=Theme.rgba(Theme.CYAN, brightness), outline='')

    def _draw_nodes(self):
        c = self.canvas
        now = time.time()
        for s in g.servers:
            x, y = s['pos']
            is_hacked = g.hacked(s)

            if is_hacked:
                col, fill, icon = Theme.GREEN, Theme.CYAN_ULTRADIM, '✓'
            elif s['decrypted']:
                col, fill, icon = Theme.AMBER, Theme.BG_CANVAS, '◉'
            elif s['scanned']:
                col, fill, icon = Theme.AMBER, Theme.BG_CANVAS, '◌'
            else:
                col, fill, icon = Theme.CYAN_DIM, Theme.BG_VOID, '○'

            in_bounce = s['name'] in g.bounce_chain
            is_connected = s is g.current_server
            r = 9 if not in_bounce else 13
            glow_r = 18 if in_bounce else 14
            if is_connected:
                r, glow_r = 15, 22

            # Glow layers
            for layer in range(3, 0, -1):
                lr = glow_r * layer / 3
                frac = layer / 3
                lc = Theme.alpha(col, frac * 0.5)
                c.create_oval(x - lr, y - lr, x + lr, y + lr,
                              outline='', fill=lc)

            # Hacked pulse
            if is_hacked:
                p = 0.5 + 0.5 * math.sin(now * 3 + self._anim_frame * 0.05)
                pr = glow_r + 4 + int(p * 6)
                pc = Theme.rgba(Theme.GREEN, 0.3 + 0.7 * p)
                c.create_oval(x - pr, y - pr, x + pr, y + pr,
                              outline=pc, width=2)

            # Connected ring
            if is_connected:
                cr = glow_r + 8
                c.create_oval(x - cr, y - cr, x + cr, y + cr,
                              outline=Theme.CYAN, width=1, dash=(3, 3))

            # Node body
            c.create_oval(x - r, y - r, x + r, y + r,
                          outline=col, fill=fill, width=2)
            if is_hacked or s['decrypted']:
                hi = r * 0.4
                c.create_oval(x - hi, y - hi, x + hi, y + hi,
                              outline='', fill=Theme.GREEN if is_hacked else Theme.AMBER)

            # Icon
            desc_lower = s['desc'].lower()
            if 'bank' in desc_lower or 'atm' in desc_lower:
                icon = '$'
            elif 'military' in desc_lower or 'satellite' in desc_lower:
                icon = '!'
            elif 'gsm' in desc_lower or 'tower' in desc_lower:
                icon = '~'
            elif 'corporate' in desc_lower or 'mainframe' in desc_lower:
                icon = '#'
            elif 'office' in desc_lower:
                icon = '@'
            elif s.get('is_gov'):
                icon = 'G'

            c.create_text(x, y - r - 10, text=s['name'][:28],
                          fill=col, font=('Consolas', 8, 'bold'), anchor='s')
            c.create_text(x, y - r - 24, text=icon,
                          fill=col, font=('Consolas', 9), anchor='s')
            if s['scanned']:
                c.create_text(x, y + r + 5,
                              text='/'.join(str(p) for p in s['ports']),
                              fill=Theme.CYAN_DIM, font=('Consolas', 7),
                              anchor='n')
            if is_connected:
                c.create_text(x, y + r + 16, text='← CONNECTED',
                              fill=Theme.GREEN,
                              font=('Consolas', 7, 'bold'), anchor='n')

    def _update_particles(self):
        for p in self._particles:
            p['x'] += p['dx']
            p['y'] += p['dy']
            p['dy'] += 0.02
            p['life'] -= 1
            p['r'] = max(0, int(p['r'] * 0.97))
        self._particles = [p for p in self._particles if p['life'] > 0]

    def _draw_particles(self):
        c = self.canvas
        for p in self._particles:
            alpha = p['life'] / p['max_life']
            c.create_oval(p['x'] - p['r'], p['y'] - p['r'],
                          p['x'] + p['r'], p['y'] + p['r'],
                          fill=Theme.rgba(p['col'], alpha), outline='')

    def emit_particles(self, cx, cy, color=Theme.CYAN, count=15):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.5)
            self._particles.append({
                'x': cx, 'y': cy,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed - 1,
                'r': random.randint(1, 3),
                'col': color,
                'life': 30,
                'max_life': 30,
            })

    def _draw_compromised_data(self, cx, cy):
        c = self.canvas
        now_t = time.time()
        hacked_nodes = [(s['pos'], s) for s in g.servers if g.hacked(s)]
        for (nx, ny), s in hacked_nodes:
            offset = (self._anim_frame * 0.5 + hash(s['name']) % 100) % 100
            for i in range(3):
                angle = (offset + i * 120) * math.pi / 50 + now_t
                dist = 12 + 6 * math.sin(now_t * 2 + i)
                dx = nx + dist * math.cos(angle)
                dy = ny + dist * math.sin(angle)
                c.create_oval(dx - 1, dy - 1, dx + 1, dy + 1,
                              fill=Theme.rgba(Theme.GREEN,
                                              0.3 + 0.3 * math.sin(now_t * 3 + i)),
                              outline='')

    def _draw_map_status(self, n):
        c = self.canvas
        hacked_count = sum(1 for s in g.servers if g.hacked(s))
        text = f'{hacked_count}/{n} COMPROMISED'
        w = c.winfo_width() or 600
        c.create_text(w - 8, 10, text=text, fill=Theme.TEXT_DIM,
                      font=('Consolas', 8), anchor='ne')
        c.create_text(w - 8, 22, text=f'PACKETS {len(self._data_packets):02d}',
                      fill=Theme.CYAN_ULTRADIM,
                      font=('Consolas', 7), anchor='ne')
