#!/usr/bin/env python3
# HACKER EVOLUTION — Main Application
# HackerApp class: ties together engine, UI, HUD, commands and panels.

import json
import math
import os
import random
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import winsound

from engine.config import SAVE_FILE, AUTO_FILE
from engine.game import g
from data import STORY_MISSIONS, DARIUS_EMAILS
from ui.theme import Theme
from ui.rich_bridge import render_to_widget
from ui.widgets.stat_card import CanvasSectionHeader
from ui.widgets.sentinel_panel import SentinelPanel
from ui.widgets.network_map import NetworkMapRenderer
from ui.widgets.boot_screen import BootScreen
from ui.widgets.alert_overlay import AlertOverlay


# ═══════════════════════════════════════════════════════════════════════════════
# GlowFrame
# ═══════════════════════════════════════════════════════════════════════════════

class GlowFrame(tk.Frame):
    def __init__(self, parent, **kw):
        tk.Frame.__init__(self, parent, **kw)
        self.config(bg=kw.get('bg', Theme.BG_SURFACE),
                    highlightbackground=Theme.CYAN_DIM, highlightthickness=1,
                    relief=tk.RIDGE, bd=1)


# ═══════════════════════════════════════════════════════════════════════════════
# HackerApp
# ═══════════════════════════════════════════════════════════════════════════════

class HackerApp:
    """Main application class. Command handlers and panel methods are
    patched in from ui.commands and ui.panels at import time."""

    def __init__(self):
        self.g = g
        self.root = tk.Tk()
        self.root.title('HACKER EVOLUTION - Created by 404 Fun Not Found')
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f'{int(sw * 0.88)}x{int(sh * 0.88)}+50+30')
        self.root.configure(bg=Theme.BG_HEADER)
        self.root.minsize(1200, 750)
        self.root.after(100, self._fake_boot_desktop)

        self.action_active = False
        self.action_cancel = False
        self.cmd_history = []
        self.history_idx = 0
        self.particles = []
        self.bounce_anim = 0
        self._sound = True
        self._tw_queue = []
        self._tw_active = False
        self._trace_alarm_on = False
        self._sep_canvases = []
        self._shake_active = False
        self._hex_stream_active = False
        self._noise_band_active = False

        self.hud = HUDBackground(self.root, Theme.BG_VOID)

        self.main_frame = tk.Frame(self.root, bg=Theme.BG_VOID)
        self.main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.setup_title()
        self.setup_layout()
        # Alert overlay — canvas placed/unplaced dynamically by AlertOverlay
        self._alert_canvas = tk.Canvas(self.main_frame, bg=Theme.BG_VOID, highlightthickness=0)
        self._alert_overlay = AlertOverlay(self._alert_canvas, self.main_frame)
        self.setup_menu()
        self.setup_bindings()
        self.animate_particles()
        self.update_map()
        self.refresh_all()

        self.restart_requested = False
        self._boot_silent = True
        self._boot_state = 'BOOTING'
        self.root.after(500, self.update_map)
        self.root.after(2000, self._animate_sentinel)
        self.start_ambient()
        # Boot window handles all intro narrative + login drama
        self.root.after(25000, lambda: setattr(self, '_boot_silent', False))

        self.start_random_events()

        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.auto_save_loop()

    # ═══ SOUND ══════════════════════════════════════════════════════════════

    def _beep(self, freq=900, dur=30):
        if not self._sound:
            return
        try:
            winsound.Beep(freq, dur)
        except Exception:
            pass

    def _sound_keystroke(self):
        if getattr(self, '_boot_silent', False):
            return
        self._beep(3000, 3)

    def _sound_keypress(self):
        """Mechanical click on actual keyboard input."""
        if getattr(self, '_boot_silent', False):
            return
        self._beep(2800, 2)

    def _sound_connect(self):
        self._beep(660, 60)
        self.root.after(80, lambda: self._beep(880, 60))

    def _sound_error(self):
        self._beep(220, 120)

    def _sound_success(self):
        self._beep(880, 40)
        self.root.after(60, lambda: self._beep(1100, 40))

    def _sound_trace_warn(self):
        self._beep(180, 150)

    # ═══ BLINKING CURSOR ════════════════════════════════════════════════════

    def _blink_cursor(self):
        if hasattr(self, 'cursor_label') and self.cursor_label.winfo_exists():
            current = self.cursor_label.cget('text')
            self.cursor_label.config(text=' ' if current == '█' else '█')
            self.root.after(500, self._blink_cursor)

    # ═══ TYPEWRITER ═════════════════════════════════════════════════════════

    def console_type(self, text, color='green', speed=25):
        self._tw_queue.append((text, color, speed))
        if not self._tw_active:
            self._process_tw()

    def _process_tw(self):
        if not self._tw_queue:
            self._tw_active = False
            return
        self._tw_active = True
        text, color, speed = self._tw_queue.pop(0)
        self.console.config(state=tk.NORMAL)
        cols = {
            'green': Theme.GREEN, 'red': Theme.RED, 'yellow': Theme.AMBER,
            'cyan': Theme.CYAN, 'orange': Theme.AMBER, 'dim': Theme.TEXT_DIM,
            'white': Theme.TEXT, 'pink': Theme.MAGENTA, 'blue': Theme.CYAN_MID,
        }
        c = cols.get(color, Theme.CYAN)
        self._tw_text = text
        self._tw_idx = 0
        self._tw_color = c
        self._tw_line_start = self.console.index(tk.INSERT)
        self._tw_tick(speed)

    def _tw_tick(self, speed):
        if self._tw_idx >= len(self._tw_text):
            self.console.insert(tk.END, '\n')
            self.console.see(tk.END)
            self.console.config(state=tk.DISABLED)
            self.root.after(10, self._process_tw)
            return
        ch = self._tw_text[self._tw_idx]
        self.console.insert(tk.END, ch)
        self.console.tag_add('tw', f'{self._tw_line_start}+{self._tw_idx}c',
                             f'{self._tw_line_start}+{self._tw_idx + 1}c')
        self.console.tag_config('tw', foreground=self._tw_color)
        self.console.see(tk.END)
        self._tw_idx += 1
        if ch != ' ':
            self._sound_keystroke()
        self.root.after(speed, lambda: self._tw_tick(speed))

    # ═══ TYPEWRITER CONSOLE OUT ═════════════════════════════════════════════

    def console_out_type(self, text, color='green', speed=15):
        """Output a line with typewriter effect (character by character)."""
        self.console.config(state=tk.NORMAL)
        cols = {
            'green': Theme.GREEN, 'red': Theme.RED, 'yellow': Theme.AMBER,
            'cyan': Theme.CYAN, 'orange': Theme.AMBER, 'dim': Theme.TEXT_DIM,
            'white': Theme.TEXT, 'pink': Theme.MAGENTA, 'blue': Theme.CYAN_MID,
        }
        c = cols.get(color, Theme.CYAN)
        self._tw_text = text + '\n'
        self._tw_idx = 0
        self._tw_color = c
        self._tw_line_start = self.console.index(tk.INSERT)
        self._tw_tick(speed)

    # ═══ TRACE ALARM ════════════════════════════════════════════════════════

    def trace_alarm(self):
        tr = g.trace_level
        if tr > 70:
            if not self._trace_alarm_on:
                self._trace_alarm_on = True
            intensity = 0.3 + 0.7 * abs(math.sin(time.time() * 4))
            r = int(255 * intensity)
            gv = int(20 * intensity)
            bv = int(50 * intensity)
            self.root.config(highlightbackground=f'#{r:02x}{gv:02x}{bv:02x}',
                             highlightthickness=2, highlightcolor=f'#{r:02x}0000')
            if tr > 85:
                self._sound_trace_warn()
            self.root.after(150, self.trace_alarm)
        else:
            if self._trace_alarm_on:
                self._trace_alarm_on = False
                self.root.config(highlightbackground=Theme.BG_VOID, highlightthickness=0)

    # ═══ FAKE BOOT LINUX ════════════════════════════════════════════════════

    def _fake_boot_desktop(self):
        # Canvas BootScreen — replaces 25s boot with 6s animation
        def on_boot_done():
            self._boot_state = 'DONE'
            self._boot_transition_main()
        BootScreen(self.root, on_boot_done)

    def _boot_animate(self, lines, i, callback=None):
        if i >= len(lines):
            self._boot_state = 'LOGIN'
            if callback:
                callback()
            return
        self._boot_txt.insert(tk.END, lines[i][0] + '\n')
        self._boot_txt.tag_add('b', 'end-2l', 'end-1l')
        self._boot_txt.tag_config('b', foreground=lines[i][1])
        self._boot_txt.see(tk.END)
        self.root.after(80 if lines[i][0] else 1, lambda: self._boot_animate(lines, i + 1, callback))

    def _boot_sound_key(self):
        try:
            import winsound
            winsound.Beep(2800, 2)
        except Exception:
            pass

    def _boot_login_prompt(self):
        t = self._boot_txt
        t.insert(tk.END, '\n\nhacker login: ')
        t.tag_add('b', 'end-1l', 'end-1l')
        t.tag_config('b', foreground='#0f0')
        t.see(tk.END)
        self._boot_login_mode = 'user'
        self._boot_user = ''
        self._boot_pass = ''
        self._boot_state = 'LOGIN'
        t.bind('<Key>', self._boot_handle_key)
        t.focus_set()
        t.config(insertbackground='#0f0', insertwidth=6)

    def _boot_handle_key(self, e):
        t = self._boot_txt
        # Beep on every printable key
        if e.char and e.char.isprintable():
            self._boot_sound_key()

        if e.keysym == 'Return':
            if self._boot_login_mode == 'user':
                if not self._boot_user.strip():
                    t.insert(tk.END, '\n')
                    t.see(tk.END)
                    t.insert(tk.END, 'hacker login: ')
                    t.see(tk.END)
                    self._boot_user = ''
                    return
                t.insert(tk.END, '\nPassword: ')
                t.see(tk.END)
                self._boot_login_mode = 'pass'
                self._boot_pass = ''
                return 'break'
            else:
                pwd = self._boot_pass.lower().strip()
                usr = self._boot_user.strip().lower()

                # Smart help/hint detection
                if pwd in ('help', 'hint', '?', 'aiuto'):
                    t.insert(tk.END, '\n')
                    self._boot_insert('[SYS] Tip: check the boot logs.\n', '#0a0')
                    self._boot_insert('[SYS] Search for "credentials" or "recovery" in the messages.\n', '#0a0')
                    if not self._boot_hint_shown:
                        self._boot_hint_shown = True
                        self._boot_insert('[SYS] (Hint: /tmp/recovery.txt)\n', '#ff0')
                    t.see(tk.END)
                    self.root.after(600, self._boot_login_prompt)
                    return 'break'

                # Valid credentials: user can use clue from boot logs
                valid = (usr in ('hacker', 'root', 'neo') and pwd == 'recovery') or \
                        (usr == 'root' and pwd == 'toor') or \
                        (usr == 'neo' and pwd == 'trinity')

                if valid:
                    self._boot_state = 'VERIFYING'
                    t.unbind('<Key>')
                    self._boot_verifying()
                else:
                    t.insert(tk.END, '\n')
                    self._boot_insert('Login incorrect\n', '#f44')
                    t.see(tk.END)
                    if random.random() < 0.3:
                        self._boot_insert('[SYS] Non ricordi? Controlla i log di boot.\n', '#880')
                    self.root.after(800, self._boot_login_prompt)
                return 'break'

        elif e.keysym == 'BackSpace':
            if self._boot_login_mode == 'user':
                if self._boot_user:
                    self._boot_user = self._boot_user[:-1]
                    t.delete('end-1c', 'end')
                    return 'break'
            else:
                if self._boot_pass:
                    self._boot_pass = self._boot_pass[:-1]
                    t.delete('end-1c', 'end')
                    return 'break'
        elif e.char and e.char.isprintable():
            if self._boot_login_mode == 'user':
                self._boot_user += e.char
                t.insert(tk.END, e.char)
                t.see(tk.END)
            else:
                self._boot_pass += e.char
                t.insert(tk.END, '*')
                t.see(tk.END)
            return 'break'

    def _boot_insert(self, text, color='#0f0'):
        t = self._boot_txt
        t.insert(tk.END, text)
        t.tag_add('b', 'end-2l', 'end-1l')
        t.tag_config('b', foreground=color)
        t.see(tk.END)

    def _boot_verifying(self):
        t = self._boot_txt
        t.insert(tk.END, '\n')
        self._boot_insert('Verifying credentials', '#0a0')
        self._boot_state = 'VERIFYING'

        def dot_step(n=0):
            if n >= 5:
                t.insert(tk.END, '\n\n')
                self._boot_kernel_panic()
                return
            t.insert(tk.END, ' .')
            t.see(tk.END)
            self._boot_sound_key()
            self.root.after(400, lambda: dot_step(n + 1))

        self.root.after(300, dot_step)

    def _boot_kernel_panic(self):
        t = self._boot_txt
        self._boot_state = 'PANIC'
        self._boot_insert('═' * 50 + '\n', '#f44')
        self._boot_insert('[ К E R N E L   P A N I C ]\n', '#f44')
        self._boot_insert('UNAUTHORIZED ACCESS DETECTED\n', '#f44')
        self._boot_insert('═' * 50 + '\n', '#f44')
        self._boot_insert('Dumping core...\n', '#f44')
        t.see(tk.END)

        # Screen flash red
        t.config(bg='#220000')
        self.root.after(200, lambda: t.config(bg='#000000'))

        # Glitch effect: rapid inserts
        for i in range(3):
            self.root.after(200 + i * 80, lambda: t.insert(tk.END, '  ## ' * 4 + '\n'))

        self.root.after(1200, self._boot_darius_interlude)

    def _boot_darius_interlude(self):
        t = self._boot_txt
        self._boot_state = 'REVEAL'
        t.delete('end-3l', 'end-1l')  # clean glitch lines
        t.insert(tk.END, '\n\n')
        self._boot_insert('╔═══════════════════════════════════════════════╗\n', '#0f0')
        self._boot_insert('║    EMERGENCY SYSTEM — DARIUS                   ║\n', '#0f0')
        self._boot_insert('║    "If you are reading this, I am dead."      ║\n', '#0f0')
        self._boot_insert('╚═══════════════════════════════════════════════╝\n', '#0f0')
        t.insert(tk.END, '\n')
        self._boot_insert('[SYS] Connection to Nexus server interrupted 14d ago...\n', '#4488ff')
        self._boot_insert('[SYS] Automatic email sent to: <unknown>\n', '#4488ff')
        self._boot_insert('[SEC] Legacy credentials found. Start with SCAN.\n', '#ffbb00')
        self._boot_insert('[NET] Network scan in progress...\n', '#00ddff')
        t.insert(tk.END, '\n')
        self._boot_insert('═══ HACKER EVOLUTION — Created by 404 Fun Not Found ═══\n', '#00ddff')
        t.see(tk.END)
        self._beep(660, 30)
        self.root.after(2000, self._boot_transition_main)

    def _boot_transition_main(self):
        self._boot_state = 'DONE'
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.root.update_idletasks()
        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)
        self.console_out(_('\nYOU HAVE 1 NEW EMAIL from Darius. Type EMAIL to read it.'), 'yellow')
        self.console_out(_('Type HELP for commands.'), 'dim')
        g.add_log(_('System online. Darius legacy active.'), 'ok')
        self._beep(660, 30)

    # ═══ TITLE BAR ══════════════════════════════════════════════════════════

    def setup_title(self):
        title = tk.Frame(self.main_frame, bg=Theme.BG_VOID)
        title.pack(fill=tk.X, pady=(2, 0))
        self._title_canvas = tk.Canvas(title, height=52, bg=Theme.BG_VOID,
                                        highlightthickness=0)
        self._title_canvas.pack(fill=tk.X)
        self._draw_title(self._title_canvas)

    def _nav_click(self, item):
        if item == 'START':
            if hasattr(self, 'h_newgame_wrapper'):
                self.h_newgame_wrapper()
        elif item == 'LOAD':
            self.load()
        elif item == 'DATA LOG':
            self.exec_cmd('email')
        elif item == 'OPTIONS':
            if hasattr(self, 'show_config'):
                self.show_config()
        elif item == 'QUIT':
            self.on_close()

    def _draw_title(self, c):
        c.delete('all')
        w = c.winfo_width()
        if w < 200:
            c.after(50, lambda: self._draw_title(c))
            return
        # Title left
        c.create_text(14, 18, text='HACKER EVOLUTION',
                      fill=Theme.CYAN, font=('Consolas', 18, 'bold'), anchor='w')
        c.create_text(14, 38, text='COVERT NETWORK INTRUSION SYSTEM',
                      fill=Theme.CYAN_MID, font=('Consolas', 8), anchor='w')
        # Navigation right
        nav_items = ['START', 'LOAD', 'DATA LOG', 'OPTIONS', 'QUIT']
        nav_x = w - 14
        nav_y = 20
        for item in reversed(nav_items):
            tw = len(item) * 9 + 20
            tid = c.create_text(nav_x, nav_y, text=item,
                                fill=Theme.CYAN_MID, font=('Consolas', 10, 'bold'),
                                anchor='e', tags='nav')
            c.tag_bind(tid, '<Button-1>', lambda e, i=item: self._nav_click(i))
            c.tag_bind(tid, '<Enter>', lambda e, t=tid: c.itemconfigure(t, fill=Theme.CYAN))
            c.tag_bind(tid, '<Leave>', lambda e, t=tid: c.itemconfigure(t, fill=Theme.CYAN_MID))
            nav_x -= tw
        # Glow bar
        for i in range(w):
            b = 0.25 + 0.75 * math.sin(i / 12 - math.pi / 2)
            b = max(0.03, b)
            r = int(3 * b)
            gv = int(30 + 60 * b)
            bl = int(60 + 120 * b)
            c.create_line(i, 49, i, 52, fill=f'#{r:02x}{gv:02x}{bl:02x}', tags='title')
        c.lower('title')

    # ═══ LAYOUT ═════════════════════════════════════════════════════════════

    def setup_layout(self):
        self.root.update_idletasks()
        avail = max(900, self.root.winfo_width())

        # ── Main body (3 columns) ──
        body = tk.Frame(self.main_frame, bg=Theme.BG_VOID)
        body.pack(fill=tk.BOTH, expand=True, padx=4, pady=(1, 1))

        # ── Left: Terminal Console ──
        left = tk.Frame(body, bg=Theme.BG_VOID)
        left.pack(side=tk.LEFT, fill=tk.BOTH)

        # Terminal header
        chdr = tk.Frame(left, bg=Theme.BG_CANVAS)
        chdr.pack(fill=tk.X)
        tk.Label(chdr, text='[ TERMINAL:0 ]', bg=Theme.BG_CANVAS, fg=Theme.CYAN,
                 font=('Consolas', 9, 'bold')).pack(side=tk.LEFT, padx=8, pady=3)
        tk.Label(chdr, text='F1=Help  Tab=Complete', bg=Theme.BG_CANVAS,
                 fg=Theme.TEXT_DIM, font=('Consolas', 8)).pack(side=tk.RIGHT, padx=8)

        # Terminal border (thin glow)
        glow_frame = tk.Frame(left, bg=Theme.BG_SURFACE, highlightthickness=1,
                              highlightbackground=Theme.CYAN_ULTRADIM)
        glow_frame.pack(fill=tk.BOTH, expand=True, pady=1)

        self.console = tk.Text(glow_frame, bg=Theme.BG_VOID, fg=Theme.CYAN,
                               font=('Consolas', 11), relief=tk.FLAT, padx=8, pady=5,
                               wrap=tk.WORD, state=tk.DISABLED, borderwidth=0,
                               insertbackground=Theme.CYAN, insertwidth=7,
                               insertofftime=300, insertontime=600)
        self.console.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        sbar = tk.Scrollbar(glow_frame, orient=tk.VERTICAL, command=self.console.yview,
                            bg=Theme.BG_CANVAS, troughcolor=Theme.BG_VOID,
                            activebackground=Theme.CYAN, width=10)
        self.console.configure(yscrollcommand=sbar.set, highlightthickness=0)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Input line
        inp = tk.Frame(left, bg=Theme.BG_CANVAS, height=32)
        inp.pack(fill=tk.X)
        self.prompt_label = tk.Label(inp, text='root@hud:~$ ', bg=Theme.BG_CANVAS,
                                     fg=Theme.CYAN, font=('Consolas', 12, 'bold'), padx=5)
        self.prompt_label.pack(side=tk.LEFT)
        self.cursor_label = tk.Label(inp, text='█', bg=Theme.BG_CANVAS,
                                     fg=Theme.CYAN, font=('Consolas', 12, 'bold'))
        self.cursor_label.pack(side=tk.LEFT, padx=(0, 2))
        self._blink_cursor()

        self.input_var = tk.StringVar()
        self.input = tk.Entry(inp, textvariable=self.input_var,
                              bg=Theme.BG_CANVAS, fg=Theme.CYAN,
                              insertbackground=Theme.CYAN,
                              font=('Consolas', 12), relief=tk.FLAT, bd=0,
                              highlightthickness=0, disabledbackground=Theme.BG_CANVAS)
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input.focus()
        self.input.bind('<Return>', self.on_cmd)
        self.input.bind('<Up>', lambda e: self.history(-1))
        self.input.bind('<Down>', lambda e: self.history(1))
        self.input.bind('<Key>', lambda e: (self._sound_keypress(),
                         self.root.after(5, self._input_glow)))
        self._input_glow_active = False
        self._input_glow()
        self.input.config(highlightthickness=0)

        # Progress bar frame (used by background task runner in commands.py)
        self.pf = tk.Frame(left, bg=Theme.BG_VOID)
        self.pv = tk.DoubleVar()
        self.pb = ttk.Progressbar(self.pf, variable=self.pv, length=300,
                                  mode='determinate', style='cyan.Horizontal.TProgressbar')
        self.pb.pack(pady=(5, 2))
        self.ps = tk.Label(self.pf, text='', bg=Theme.BG_VOID, fg=Theme.CYAN,
                           font=('Consolas', 10))
        self.ps.pack(pady=(0, 2))
        style = ttk.Style()
        style.configure('cyan.Horizontal.TProgressbar', background=Theme.CYAN, troughcolor=Theme.BG_SURFACE)


        # ── Center: Network Map ──
        center = tk.Frame(body, bg=Theme.BG_VOID)
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(4, 0))

        # Map header
        map_hdr = tk.Frame(center, bg=Theme.BG_CANVAS)
        map_hdr.pack(fill=tk.X)
        tk.Label(map_hdr, text='[ NETWORK MAP: KYBERNETIX MAIN_GRID ]',
                 bg=Theme.BG_CANVAS, fg=Theme.CYAN,
                 font=('Consolas', 9, 'bold')).pack(side=tk.LEFT, padx=8, pady=3)
        self._map_status = tk.Label(map_hdr, text='', bg=Theme.BG_CANVAS,
                                    fg=Theme.TEXT_DIM, font=('Consolas', 8))
        self._map_status.pack(side=tk.RIGHT, padx=8)

        self.map_canvas = tk.Canvas(center, bg=Theme.BG_VOID,
                                    highlightthickness=0)
        self.map_canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.map_canvas.bind('<Button-1>', self.map_click)
        self.map_canvas.bind('<Button-3>', self.map_right_click)
        self._map_renderer = NetworkMapRenderer(self.map_canvas)

        # ── Right: HUD Stack Canvas ──
        right_w = min(300, int(avail * 0.22))
        right_frame = tk.Frame(body, bg=Theme.BG_VOID, width=right_w)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(4, 0))
        right_frame.pack_propagate(False)

        self._right_canvas = tk.Canvas(right_frame, bg=Theme.BG_VOID,
                                       highlightthickness=0, width=right_w)
        self._right_canvas.pack(fill=tk.BOTH, expand=True)

        # ── Status bar ──
        self._status_bar = tk.Frame(self.main_frame, bg=Theme.BG_CANVAS, height=24)
        self._status_bar.pack(fill=tk.X, pady=(1, 0))
        self._status_labels = {}
        self._status_indicators = {}
        # Left: indicators
        indicators = [
            ('_money', 'CREDITS', '$0', Theme.GREEN),
            ('_ram', 'RAM', '--%', Theme.CYAN),
            ('_cpu', 'CPU', '--%', Theme.CYAN_MID),
            ('_fw', 'FW', '--', Theme.CYAN),
            ('_tools', 'TOOLS', '--', Theme.AMBER),
            ('_crypto', 'CRYPTO', '--', Theme.MAGENTA),
        ]
        for key, label, val, col in indicators:
            f = tk.Frame(self._status_bar, bg=Theme.BG_CANVAS)
            f.pack(side=tk.LEFT, padx=(4, 0))
            tk.Label(f, text=label, bg=Theme.BG_CANVAS, fg=Theme.TEXT_DIM,
                     font=('Consolas', 7)).pack(side=tk.LEFT)
            lb = tk.Label(f, text=val, bg=Theme.BG_CANVAS, fg=col,
                          font=('Consolas', 8, 'bold'))
            lb.pack(side=tk.LEFT, padx=(2, 0))
            self._status_indicators[key] = lb
        # Right: connection + trace
        conn_frame = tk.Frame(self._status_bar, bg=Theme.BG_CANVAS)
        conn_frame.pack(side=tk.RIGHT, padx=8)
        self._status_labels['_conn'] = tk.Label(
            conn_frame, text='DISCONNECTED', bg=Theme.BG_CANVAS, fg=Theme.MAGENTA,
            font=('Consolas', 8))
        self._status_labels['_conn'].pack(side=tk.LEFT, padx=(0, 8))
        self._status_labels['_trace_s'] = tk.Label(
            conn_frame, text='TRACE: 0%', bg=Theme.BG_CANVAS, fg=Theme.GREEN,
            font=('Consolas', 8, 'bold'))
        self._status_labels['_trace_s'].pack(side=tk.LEFT)

        # ── Draw right panel contents ──
        self._build_right_panel()

    def _build_right_panel(self):
        c = self._right_canvas
        cw = int(c.cget('width'))

        # Background grid dots
        for x in range(0, cw, 20):
            for y in range(0, 1200, 20):
                if (x + y) % 40 == 0:
                    c.create_oval(x - 1, y - 1, x + 2, y + 2,
                                  fill=Theme.CYAN_ULTRADIM, outline='', tags='bg')

        y = 4

        # ════════════════════════════════════════════════════════════════
        # 1. SYSTEM STATUS
        # ════════════════════════════════════════════════════════════════
        CanvasSectionHeader(c, 4, y, 'SYSTEM STATUS', cw - 8, Theme.CYAN_MID)
        y += 18
        self._status_word = c.create_text(14, y, text='SECURE',
                                          fill=Theme.GREEN,
                                          font=('Consolas', 11, 'bold'), anchor='w')
        y += 16
        # Progress bar
        bar_x, bar_y = 14, y
        bar_w = cw - 28
        bar_h = 10
        self._status_bar_rect = (bar_x, bar_y, bar_w, bar_h)
        c.create_rectangle(bar_x, bar_y, bar_x + bar_w, bar_y + bar_h,
                           fill=Theme.BG_VOID, outline=Theme.CYAN_ULTRADIM, width=1)
        self._status_bar_fill = c.create_rectangle(
            bar_x + 1, bar_y + 1, bar_x + 1, bar_y + bar_h - 1,
            fill=Theme.GREEN, outline='')
        self._status_pct = c.create_text(
            bar_x + bar_w - 2, bar_y + bar_h // 2,
            text='82%', fill=Theme.GREEN, font=('Consolas', 7, 'bold'), anchor='e')
        y += bar_h + 6
        self._status_info = c.create_text(
            14, y, text='Level 3 Bypass | Mask Active',
            fill=Theme.TEXT_DIM, font=('Consolas', 7), anchor='w')
        y += 16

        # ════════════════════════════════════════════════════════════════
        # 2. SCANNER
        # ════════════════════════════════════════════════════════════════
        CanvasSectionHeader(c, 4, y, 'SCANNER', cw - 8, Theme.CYAN_MID)
        y += 18
        self._scan_phase = 0.0
        self._scan_wave_items = []
        wave_center_y = y + 18
        n_wave = int(cw * 0.35)
        for i in range(n_wave):
            px = 8 + i * 2
            li = c.create_line(px, wave_center_y, px + 2, wave_center_y,
                               fill=Theme.CYAN_ULTRADIM, width=1, tags='scan')
            self._scan_wave_items.append(li)
        # Sweep bar
        self._scan_sweep = c.create_line(
            8, wave_center_y - 16, 8, wave_center_y + 16,
            fill=Theme.CYAN, width=2, tags='scan')
        y += 38
        c.create_text(14, y, text='Scanning Grid D1', fill=Theme.TEXT_DIM,
                      font=('Consolas', 8), anchor='w')
        self._scan_noise = c.create_text(cw - 8, y, text='Noise 12%', fill=Theme.CYAN,
                                         font=('Consolas', 8), anchor='e')
        y += 18

        # ════════════════════════════════════════════════════════════════
        # 3. ALERTS
        # ════════════════════════════════════════════════════════════════
        CanvasSectionHeader(c, 4, y, 'ALERTS', cw - 8, Theme.AMBER)
        y += 18
        self._alert_items = {}
        alerts_data = [
            ('trace',  'TRACE',     '0.0%',   Theme.RED),
            ('sentinel', 'SENTINEL', 'DORMANT', Theme.GREEN),
            ('probe',  'PROBE',     'NONE',    Theme.TEXT_DIM),
            ('counter', 'COUNTER',  '--',      Theme.AMBER),
        ]
        for key, label, val, col in alerts_data:
            c.create_text(14, y, text=f'{label}', fill=col,
                          font=('Consolas', 8, 'bold'), anchor='w')
            v = c.create_text(cw - 8, y, text=val, fill=col,
                              font=('Consolas', 8, 'bold'), anchor='e')
            self._alert_items[key] = v
            y += 14
        y += 2

        # ════════════════════════════════════════════════════════════════
        # 4. OBJECTIVES
        # ════════════════════════════════════════════════════════════════
        CanvasSectionHeader(c, 4, y, 'OBJECTIVES', cw - 8, Theme.CYAN_MID)
        y += 18
        self._obj_items = []
        for _ in range(4):
            t = c.create_text(14, y, text='', fill=Theme.TEXT_DIM,
                              font=('Consolas', 8), anchor='w', tags='obj')
            y += 13
            self._obj_items.append(t)
        y += 4

        # ════════════════════════════════════════════════════════════════
        # 5. SENTINEL AI
        # ════════════════════════════════════════════════════════════════
        self._sentinel = SentinelPanel(c, 4, y, cw - 8)
        y += SentinelPanel.HEIGHT + 6

        # ════════════════════════════════════════════════════════════════
        # 6. Action buttons
        # ════════════════════════════════════════════════════════════════
        ay = y + 2
        self._action_btns = []
        btn_w = (cw - 20) // 3
        for i, (txt, cmd) in enumerate([
            ('SAVE', self.save), ('LOAD', self.load), ('UPGRADE', self.show_upgrade),
        ]):
            x = 4 + i * (btn_w + 4)
            self._draw_button(x, ay, btn_w, 22, txt, cmd)

        c.lower('bg')

    def _draw_button(self, x, y, w, h, text, command):
        c = self._right_canvas
        tag = f'btn_{id(self)}_{text}'
        # Button bg
        c.create_rectangle(x, y, x + w, y + h,
                           fill=Theme.BG_SURFACE, outline=Theme.CYAN_ULTRADIM,
                           width=1, tags=tag)
        # Button text
        c.create_text(x + w // 2, y + h // 2, text=text,
                      fill=Theme.CYAN, font=('Consolas', 8, 'bold'), tags=tag)
        # Click handler
        rid = c.create_rectangle(x, y, x + w, y + h,
                                 fill='', outline='', tags=(tag, '_btn_click'))
        c.tag_bind(rid, '<Button-1>', lambda e, cmd=command: cmd())
        c.tag_bind(rid, '<Enter>', lambda e, xx=x, yy=y, ww=w, hh=h, tag=tag:
                   c.itemconfigure(tag, fill=Theme.BG_HEADER))
        c.tag_bind(rid, '<Leave>', lambda e, tag=tag:
                   c.itemconfigure(tag, fill=Theme.BG_SURFACE))

    def _input_glow(self):
        if self._input_glow_active:
            return
        self._input_glow_active = True
        self.input.config(bg=Theme.BG_CANVAS, highlightbackground=Theme.CYAN,
                          highlightthickness=1)
        self.root.after(150, lambda: self.input.config(highlightthickness=0)
                        if self._input_glow_active else None)
        self.root.after(200, lambda: setattr(self, '_input_glow_active', False))

    # ═══ MENU ═══════════════════════════════════════════════════════════════

    def setup_menu(self):
        mb = tk.Menu(self.root, bg=Theme.BG_HEADER, fg=Theme.CYAN_MID,
                     activebackground=Theme.BG_HEADER, activeforeground=Theme.TEXT)
        self.root.config(menu=mb)
        fm = tk.Menu(mb, tearoff=0, bg=Theme.BG_HEADER, fg=Theme.CYAN_MID,
                     activebackground=Theme.BG_HEADER, activeforeground=Theme.TEXT)
        mb.add_cascade(label='FILE', menu=fm)
        fm.add_command(label='NEW GAME', command=self.h_newgame_wrapper)
        fm.add_separator()
        fm.add_command(label='SAVE', command=self.save)
        fm.add_command(label='LOAD', command=self.load)
        fm.add_separator()
        fm.add_command(label='EXPORT...', command=self.export)
        fm.add_command(label='IMPORT...', command=self.import_)
        fm.add_separator()
        fm.add_command(label='SETTINGS', command=self.show_config)
        fm.add_separator()
        fm.add_command(label='QUIT', command=self.on_close)

    # ═══ BINDINGS ═══════════════════════════════════════════════════════════

    def setup_bindings(self):
        self.root.bind('<F1>', lambda e: self.console_out(
            'F2=Obj F3=Map F4=Next F5=Miss F6=Ach F7=News F8=Stats | HELP per comandi', 'yellow'))
        self.root.bind('<F2>', lambda e: self.show_objs())
        self.root.bind('<F3>', lambda e: self.update_map())
        self.root.bind('<F4>', lambda e: self.console_out(
            '[!] Livello successivo... digita NEXTLEVEL', 'yellow'))
        self.root.bind('<F5>', lambda e: self.show_missions())
        self.root.bind('<F6>', lambda e: self.show_achievements())
        self.root.bind('<F7>', lambda e: self.console_out(_('Recent news:'), 'yellow') or
                       [self.console_out(_fmt('  {}', n), 'dim') for n in g.news[:5]])
        self.root.bind('<F8>', lambda e: self.h_stats([], ''))
        self.input.bind('<Tab>', self._tab_complete)

    # ═══ CONSOLE ════════════════════════════════════════════════════════════

    def console_out(self, text, color='green'):
        self.console.config(state=tk.NORMAL)
        cols = {
            'green': Theme.GREEN, 'red': Theme.RED, 'yellow': Theme.AMBER,
            'cyan': Theme.CYAN, 'orange': Theme.AMBER, 'dim': Theme.TEXT_DIM,
            'white': Theme.TEXT, 'pink': Theme.MAGENTA, 'blue': Theme.CYAN_MID,
        }
        c = cols.get(color, Theme.CYAN)
        self.console.insert(tk.END, text + '\n')
        self.console.tag_add('c', 'end-2l', 'end-1l')
        self.console.tag_config('c', foreground=c)
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        if text and text.strip() and not getattr(self, '_boot_silent', False):
            self._beep(1800, 6)

    def console_clear(self):
        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)

    def console_rich(self, renderable):
        """Render a Rich renderable (Table, Panel, str) into the console."""
        render_to_widget(self.console, renderable)
        if not getattr(self, '_boot_silent', False):
            self._beep(1800, 6)

    def on_cmd(self, e):
        cmd = self.input_var.get()
        if cmd.strip():
            self.cmd_history.append(cmd)
            self.history_idx = len(self.cmd_history)
            self.input_var.set('')
            self.exec_cmd(cmd)
        self.input.focus()

    def history(self, d):
        if not self.cmd_history:
            return
        if d < 0:
            self.history_idx = max(0, self.history_idx - 1)
        else:
            self.history_idx = min(len(self.cmd_history), self.history_idx + 1)
        if self.history_idx >= len(self.cmd_history):
            self.input_var.set('')
        else:
            self.input_var.set(self.cmd_history[self.history_idx])

    # ═══ TAB COMPLETION ═════════════════════════════════════════════════════

    def _tab_complete(self, e):
        txt = self.input_var.get()
        parts = txt.split()
        if not txt:
            return
        cmds = [
            'help', 'scan', 'connect', 'crack', 'decrypt', 'login', 'ls', 'cat',
            'download', 'upload', 'delete', 'transfer', 'exec', 'bounce',
            'bounceinfo', 'bouncehelp', 'killtrace', 'deletelogs', 'scanports',
            'ping', 'traceroute', 'schematic', 'route', 'missions', 'newmission',
            'achievements', 'config', 'upgrade', 'nextlevel', 'money', 'servers',
            'clear', 'abort', 'sound', 'alias', 'unalias', 'crypto', 'buycrypto',
            'sellcrypto', 'combine', 'market', 'darknet', 'skills', 'stats', 'glitch',
            'newgame', 'intel', 'sellintel', 'story',
        ]
        if len(parts) == 1:
            matches = [c for c in cmds if c.startswith(parts[0])]
            if len(matches) == 1:
                self.input_var.set(matches[0] + ' ')
                self.input.icursor(tk.END)
            elif matches:
                self.console_out('  '.join(matches), 'dim')
        elif len(parts) >= 2 and parts[0].lower() in (
            'scan', 'connect', 'crack', 'decrypt', 'login', 'bounce', 'ping', 'traceroute',
        ):
            srvs = [s['name'] for s in g.servers if s['name'].startswith(parts[-1])]
            if len(srvs) == 1:
                self.input_var.set(' '.join(parts[:-1]) + ' ' + srvs[0] + ' ')
                self.input.icursor(tk.END)
            elif srvs:
                self.console_out('  '.join(srvs), 'dim')

    # ═══ COMMAND DISPATCH ═══════════════════════════════════════════════════

    def exec_cmd(self, line):
        parts = line.strip().split()
        if not parts:
            return
        cmd = parts[0].lower()
        args = parts[1:]
        self.console_out(_fmt('> {}', line), 'dim')
        self.g.add_log(_fmt('> {}', line), 'info')

        h_map = {
            'help': self.h_help, '?': self.h_help,
            'ls': self.h_ls, 'dir': self.h_ls,
            'cat': self.h_cat, 'delete': self.h_delete,
            'scan': self.h_scan,
            'connect': self.h_connect, 'ssh': self.h_connect,
            'logout': self.h_logout, 'disconnect': self.h_logout,
            'download': self.h_download, 'upload': self.h_upload,
            'exec': self.h_exec,
            'clear': self.h_clear, 'cls': self.h_clear,
            'crack': self.h_crack, 'decrypt': self.h_decrypt,
            'transfer': self.h_transfer, 'abort': self.h_abort,
            'config': self.h_config, 'upgrade': self.h_upgrade,
            'login': self.h_login, 'bounce': self.h_bounce,
            'bounceinfo': self.h_bounceinfo, 'bouncehelp': self.h_bouncehelp,
            'killtrace': self.h_killtrace, 'deletelogs': self.h_deletelogs,
            'nextlevel': self.h_nextlevel, 'money': self.h_money,
            'servers': self.h_servers, 'scanports': self.h_scanports,
            'newgame': self.h_newgame, 'reset': self.h_newgame,
            'email': self.h_email, 'switch': self.h_switch,
            'ping': self.h_ping, 'traceroute': self.h_traceroute,
            'schematic': self.h_schematic, 'route': self.h_route, 'missions': self.h_missions,
            'newmission': self.h_newmission, 'achievements': self.h_achievements,
            'sound': self.h_sound,
            'crypto': self.h_crypto, 'buycrypto': self.h_buycrypto,
            'sellcrypto': self.h_sellcrypto,
            'combine': self.h_combine, 'market': self.h_market,
            'skills': self.h_skills, 'alias': self.h_alias,
            'unalias': self.h_unalias, 'stats': self.h_stats,
            'view': self.h_view,
            'intel': self.h_intel, 'sellintel': self.h_sellintel,
            'story': self.h_story,
            'darknet': self.h_darknet,
            'debugstate': self.h_debugstate,
            'validatecontent': self.h_validatecontent,
        }
        if cmd not in h_map and cmd in g.aliases:
            self.exec_cmd(g.aliases[cmd])
            return
        h = h_map.get(cmd)
        if h:
            h(args, line)
            # Sentinel AI tick — reacts to every player command
            sentinel_result = g.sentinel_tick()
            if sentinel_result == 'sentinel_active':
                self._screen_shake(400, 5)
                self._sound_error()
        else:
            self.console_out(_fmt('Unknown command: {}. Type HELP.', cmd), 'red')

    # ═══ SCREEN SHAKE ═══════════════════════════════════════════════════════

    def _screen_shake(self, duration=300, intensity=3):
        if self._shake_active:
            return
        self._shake_active = True
        steps = duration // 30

        def tick(n=0):
            if n >= steps:
                self.main_frame.place_configure(relx=0, rely=0)
                self._shake_active = False
                return
            ox = random.uniform(-intensity, intensity)
            oy = random.uniform(-intensity, intensity)
            self.main_frame.place_configure(relx=ox / 2000, rely=oy / 2000)
            self.root.after(30, lambda: tick(n + 1))

        tick()

    def _animate_scanner(self):
        if not hasattr(self, '_scan_wave_items') or not self._scan_wave_items:
            return
        c = self._right_canvas
        if not c.winfo_exists():
            return
        w = int(c.cget('width'))
        n = len(self._scan_wave_items)
        if n < 2:
            return
        self._scan_phase = (self._scan_phase + 0.15) % (2 * math.pi)
        wave_center_y = None
        for i, li in enumerate(self._scan_wave_items):
            try:
                bbox = c.bbox(li)
                if bbox:
                    wave_center_y = bbox[1] + (bbox[3] - bbox[1]) / 2
                    break
            except Exception:
                pass
        if wave_center_y is None:
            return
        for i, li in enumerate(self._scan_wave_items):
            px = 8 + i * 2
            amp = 8 + 4 * math.sin(i * 0.3)
            wave_y = wave_center_y + amp * math.sin(i * 0.25 + self._scan_phase)
            c.coords(li, px, wave_y, px + 2, wave_y)
            bright = 0.2 + 0.8 * (0.5 + 0.5 * math.sin(i * 0.2 + self._scan_phase))
            col = Theme.rgba(Theme.CYAN, bright)
            c.itemconfigure(li, fill=col)
        # Sweep line
        sweep_pos = 8 + (self._scan_phase / (2 * math.pi)) * (n * 2)
        if hasattr(self, '_scan_sweep'):
            try:
                bbox2 = c.bbox(self._scan_sweep)
                if bbox2:
                    sy = bbox2[1]
                    sh = bbox2[3] - bbox2[1]
                    c.coords(self._scan_sweep, sweep_pos, sy, sweep_pos, sy + sh)
            except Exception:
                pass

    def _animate_sentinel(self):
        if hasattr(self, '_sentinel'):
            self._sentinel.animate()
        if hasattr(self, '_alert_overlay'):
            self._alert_overlay.animate()
        self._animate_scanner()
        self.root.after(500, self._animate_sentinel)

    def _update_prompt(self):
        if not hasattr(self, 'prompt_label'):
            return
        if g.current_server:
            self.prompt_label.config(text=f'root@{g.current_server["name"].split(".")[0]}:~$ ', fg=Theme.GREEN)
        else:
            self.prompt_label.config(text='root@hud:~$ ', fg=Theme.CYAN)

    def _impact_wave(self, cx, cy):
        for r in range(5, 80, 5):
            self.root.after(r * 5, lambda rr=r: (
                self.map_canvas.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                                            outline=Theme.CYAN, width=2, tags='impact'),
                self.root.after(120, lambda: self.map_canvas.delete('impact'))
            ) if self.map_canvas.winfo_exists() else None)
        self._map_renderer.emit_particles(cx, cy, Theme.CYAN, 30)
        self._screen_shake(200, 2)

    # ═══ MAP ════════════════════════════════════════════════════════════════

    def update_map(self):
        self._map_renderer.draw()
        self.bounce_anim = self._map_renderer._anim_frame

    def map_click(self, e):
        for s in g.servers:
            x, y = s['pos']
            if abs(e.x - x) < 20 and abs(e.y - y) < 20:
                self.console_out(_fmt('[MAP] {}  Ports: {}  Bounce: {}/3', s["name"], ", ".join(str(p) for p in s["ports"]), s["bounce_used"]), 'cyan')
                if s['scanned']:
                    self.console_out(_fmt('  Key: {}b  Money: ${}  Files: {}', s["key_bits"], s["money"], len(s["files"])), 'green')
                    st = 'DECRYPTED' if s['decrypted'] else 'ENCRYPTED'
                    for p in s['ports']:
                        st += f' | P{p}: {"OK" if s["cracked"].get(p) else "LOCK"}'
                    self.console_out(_fmt('  Status: {}', st), 'yellow')
                return

    def map_right_click(self, e):
        for s in g.servers:
            x, y = s['pos']
            if abs(e.x - x) < 25 and abs(e.y - y) < 25:
                m = tk.Menu(self.root, tearoff=0, bg=Theme.BG_HEADER, fg=Theme.CYAN_MID,
                            activebackground=Theme.BG_HEADER, activeforeground=Theme.TEXT)
                m.add_command(label=f'SCAN {s["name"]}',
                              command=lambda h=s["name"]: self.exec_cmd(f'scan {h}'))
                if s['scanned']:
                    if not s['decrypted']:
                        m.add_command(label=f'DECRYPT {s["name"]}',
                                      command=lambda h=s["name"]: self.exec_cmd(f'decrypt {h}'))
                    for p in s['ports']:
                        if not s['cracked'].get(p):
                            m.add_command(label=f'CRACK {s["name"]}:{p}',
                                          command=lambda h=s["name"], pp=p: self.exec_cmd(f'crack {h} {pp}'))
                if g.hacked(s):
                    m.add_command(label=f'BOUNCE {s["name"]}',
                                  command=lambda h=s["name"]: self.exec_cmd(f'bounce {h}'))
                    for p in s['ports']:
                        if s['cracked'].get(p) and s is not g.current_server:
                            m.add_command(label=f'🔌 CONNECT {s["name"]}:{p}',
                                          command=lambda h=s["name"], pp=p: self.exec_cmd(f'connect {h} {pp}'))
                m.add_separator()
                m.add_command(label=f'ℹ INFO {s["name"]}',
                              command=lambda h=s["name"]: self.exec_cmd(f'scan {h}'))
                m.post(e.x_root, e.y_root)
                return

    # ═══ PARTICLES ══════════════════════════════════════════════════════════

    def animate_particles(self):
        if not hasattr(self, '_particles'):
            self._particles = []
        c = self.hud.canvas
        w = c.winfo_width()
        h = c.winfo_height()
        if w > 10 and h > 10 and random.random() < 0.3 and len(self._particles) < 50:
            self._particles.append([random.randint(0, w), 0,
                                    random.uniform(0.5, 2), random.uniform(0, math.pi * 2)])
        c.delete('particle')
        for p in self._particles[:]:
            p[1] += p[2] * 0.3
            p[0] += math.sin(p[3]) * 0.3
            p[3] += 0.01
            if p[1] > h:
                self._particles.remove(p)
                continue
            b = random.choice(['33', '66', '99', 'bb'])
            c.create_text(p[0], p[1], text='·',
                          fill=f'#00{b}ff', font=('Consolas', int(p[2] * 5 + 3)), tags='particle')
        self.root.after(80, self.animate_particles)

    # ═══ REFRESH / RENDER ═══════════════════════════════════════════════════

    def refresh_all(self):
        c = self._right_canvas
        tr = g.trace_level
        tr_color = Theme.GREEN if tr < 50 else Theme.AMBER if tr < 80 else Theme.RED

        # ── SYSTEM STATUS ──
        if hasattr(self, '_status_word'):
            status = 'SECURE' if tr < 40 else 'STABLE' if tr < 70 else 'ALERT'
            c.itemconfigure(self._status_word, text=status,
                            fill=Theme.GREEN if tr < 50 else Theme.AMBER if tr < 80 else Theme.RED)
        if hasattr(self, '_status_bar_fill') and hasattr(self, '_status_bar_rect'):
            bx, by, bw, bh = self._status_bar_rect
            target_w = int((1 - tr / 100) * (bw - 2))
            target_w = max(0, min(bw - 2, target_w))
            c.coords(self._status_bar_fill, bx + 1, by + 1, bx + 1 + target_w, by + bh - 1)
            c.itemconfigure(self._status_bar_fill,
                            fill=Theme.GREEN if tr < 50 else Theme.AMBER if tr < 80 else Theme.RED)
        if hasattr(self, '_status_pct'):
            pct = 100 - tr
            c.itemconfigure(self._status_pct, text=f'{pct:.0f}%')
        if hasattr(self, '_status_info'):
            bypass = min(g.level, 10)
            info_parts = [f'Level {bypass} Bypass']
            if tr > 30:
                info_parts.append(f'Trace {tr:.0f}%')
            if g.current_server:
                info_parts.append(g.current_server['name'].split('.')[0])
            c.itemconfigure(self._status_info, text=' | '.join(info_parts))

        # ── SCANNER ── (animated wave phase updated in _animate_scanner)

        # ── ALERTS ──
        if hasattr(self, '_alert_items'):
            c.itemconfigure(self._alert_items['trace'],
                            text=f'{tr:.1f}%',
                            fill=tr_color)
            sentinel_state = 'ACTIVE' if tr > 80 else 'ANALYZING' if tr > 50 else 'DORMANT'
            sentinel_color = Theme.RED if tr > 80 else Theme.AMBER if tr > 50 else Theme.GREEN
            c.itemconfigure(self._alert_items['sentinel'],
                            text=sentinel_state, fill=sentinel_color)
            if tr > 50:
                c.itemconfigure(self._alert_items['probe'],
                                text='DETECTED', fill=Theme.AMBER)
            else:
                c.itemconfigure(self._alert_items['probe'],
                                text='NONE', fill=Theme.TEXT_DIM)
            if tr > 70:
                c.itemconfigure(self._alert_items['counter'],
                                text='ACTIVE', fill=Theme.RED)
            else:
                c.itemconfigure(self._alert_items['counter'],
                                text='STANDBY', fill=Theme.TEXT_DIM)

        # ── SENTINEL ──
        if hasattr(self, '_sentinel'):
            self._sentinel.set_state('ACTIVE' if tr > 80 else 'ANALYZING' if tr > 50 else 'IDLE')

        # ── OBJECTIVES ──
        self._update_objectives()

        # ── STATUS BAR ──
        if '_trace_s' in self._status_labels:
            self._status_labels['_trace_s'].config(
                text=f'TRACE: {tr:.0f}%', fg=tr_color)
        if g.current_server:
            self._status_labels['_conn'].config(
                text=f'CONN: {g.current_server["name"][:20]}', fg=Theme.GREEN)
        else:
            self._status_labels['_conn'].config(text='DISCONNECTED', fg=Theme.MAGENTA)
        # Compact indicators
        if hasattr(self, '_status_indicators'):
            self._status_indicators['_money'].config(
                text=f'${g.money:,}', fg=Theme.GREEN if g.money > 0 else Theme.TEXT_DIM)
            self._status_indicators['_ram'].config(
                text=f'{random.randint(40, 85)}%', fg=Theme.CYAN)
            self._status_indicators['_cpu'].config(
                text=f'{random.randint(10, 60)}%', fg=Theme.CYAN_MID)
            self._status_indicators['_fw'].config(
                text='OK', fg=Theme.GREEN if tr < 50 else Theme.AMBER)
            self._status_indicators['_tools'].config(
                text=str(g.level + len(g.bounce_chain)), fg=Theme.AMBER)
            crypto_val = getattr(g, 'crypto_balance', 0)
            self._status_indicators['_crypto'].config(
                text=f'${crypto_val}' if crypto_val else '--', fg=Theme.MAGENTA)

        # Console glow
        if hasattr(self, 'console'):
            parent = self.console.master
            if parent:
                if g.current_server:
                    parent.config(bg=Theme.CYAN_DIM if g.hacked(g.current_server) else Theme.CYAN_ULTRADIM)
                elif tr > 70:
                    pulse = int(40 + 40 * math.sin(time.time() * 4))
                    parent.config(bg=f'#{pulse:02x}0000')
                else:
                    parent.config(bg=Theme.BG_SURFACE)

        self.trace_alarm()
        self.check_achievements()
        g.check_missions()
        self.glitch()

    def _update_objectives(self):
        hacked = sum(1 for s in g.servers if g.hacked(s))
        mdone = sum(1 for m in g.missions if m['done'])
        objs = [
            f'BYPASS GRID FIREWALL',
            f'DATA EXTRACTION',
            f'ACCESS NODE ({hacked}/{len(g.servers)})',
        ]
        if g.trace_level > 50:
            objs.append('KILL TRACE - URGENT')
        else:
            objs.append('EXIT UNTRACED')
        for i, t in enumerate(self._obj_items):
            txt = objs[i] if i < len(objs) else ''
            self._right_canvas.itemconfigure(t, text=txt)

    def show_objs(self):
        done = sum(1 for s in g.servers if g.hacked(s))
        mdone = sum(1 for m in g.missions if m['done'])
        atotal = len(g.achievements)
        self.console_out('═' * 60, 'yellow')
        self.console_out(_('OBJECTIVES'), 'yellow')
        self.console_out('═' * 60, 'yellow')
        self.console_out(_fmt('  📊 Hacked servers: {}/{}', done, len(g.servers)), 'green')
        self.console_out(_fmt('  ⚠ Trace: {:.1f}%', g.trace_level), 'cyan')
        self.console_out(_fmt('  Money: ${:,}  |  Score: {}', g.money, g.score), 'yellow')
        self.console_out(_fmt('  Level: {}  |  Achievement: {}/{}', g.level, atotal, len(g.ACHIEVEMENTS)), 'white')
        if g.missions:
            self.console_out(_fmt('  Missions: {}/{} completed', mdone, len(g.missions)),
                             'green' if mdone == len(g.missions) else 'yellow')
        self.console_out(_fmt('  🔁 Bounce hop: {}', len(g.bounce_chain)), 'cyan')
        self.console_out('─' * 60, 'yellow')
        self.console_out(_('  F2=Objectives  F5=Missions  F6=Achievement  F7=News'), 'dim')
        self.console_out('═' * 60, 'yellow')

    # ═══ MISSIONS & ACHIEVEMENTS (thin console wrappers) ════════════════════

    def show_missions(self):
        if not g.missions:
            self.console_out(_('No active missions. Type NEWMISSION to generate.'), 'yellow')
            return
        self.console_out('═' * 60, 'cyan')
        self.console_out(_('ACTIVE MISSIONS'), 'yellow')
        self.console_out('─' * 60, 'cyan')
        for i, m in enumerate(g.missions):
            st = '✓' if m['done'] else '○'
            self.console_out(_fmt('  {} {:<45} ${}', st, m["desc"], m["reward"]), 'green' if m['done'] else 'yellow')
        self.console_out('─' * 60, 'cyan')
        self.console_out(_('Use NEWMISSION for new missions.'), 'dim')

    def h_newmission(self, a, r):
        g.gen_missions()
        self.console_out(_fmt('Generated {} new missions!', len(g.missions)), 'green')
        self.show_missions()

    def h_missions(self, a, r):
        self.show_missions()

    def show_achievements(self):
        self.console_out('═' * 60, 'cyan')
        self.console_out(_('ACHIEVEMENTS'), 'yellow')
        self.console_out('─' * 60, 'cyan')
        for a in g.ACHIEVEMENTS:
            unlocked = a[0] in g.achievements
            st = '🏆' if unlocked else '🔒'
            self.console_out(_fmt('  {} {:<20} {:<30} {}', st, a[1], a[2], "+" + str(a[3]) if unlocked else ""),
                             'green' if unlocked else 'dim')
        self.console_out('─' * 60, 'cyan')

    def h_achievements(self, a, r):
        self.show_achievements()

    def check_achievements(self):
        for aid in g.check_achievements():
            a = g.unlock_achievement(aid)
            if a:
                self.console_type(_fmt('🏆 Achievement unlocked: {} (+${})', a[1], a[3]), 'yellow', 20)
                self._sound_success()

    # ═══ GLITCH EFFECT ══════════════════════════════════════════════════════

    def glitch(self):
        if random.random() > 0.1 and g.trace_level < 50:
            return
        if random.random() > 0.3:
            return
        eff = random.choice(['shift', 'scanline', 'invert', 'noise', 'rain'])
        if eff == 'shift':
            self.main_frame.place_configure(relx=random.uniform(-0.008, 0.008),
                                            rely=random.uniform(-0.005, 0.005))
            self.root.after(80, lambda: self.main_frame.place_configure(relx=0, rely=0))
        elif eff == 'scanline' and hasattr(self, 'hud'):
            c = self.hud.canvas
            h = c.winfo_height()
            w = c.winfo_width()
            if h < 3 or w < 3:
                return
            for _ in range(random.randint(1, 3)):
                y = random.randint(0, h - 2)
                c.create_line(0, y, w, y, fill=Theme.CYAN_MID, width=random.randint(1, 3), tags='glitch')
                self.root.after(100, lambda: c.delete('glitch'))
        elif eff == 'rain' and hasattr(self, 'console'):
            old_bg = self.console.cget('bg')
            self.console.config(bg='#002244')
            self.root.after(100, lambda: self.console.config(bg=old_bg))

    # ═══ NOTIFICATIONS ══════════════════════════════════════════════════════

    def notify(self, text, color='cyan', duration=2500):
        w = tk.Toplevel(self.root)
        w.overrideredirect(True)
        w.attributes('-topmost', True)
        w.configure(bg=Theme.BG_HEADER)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - 420
        y = sh - 120
        w.geometry(f'400x50+{x}+{y}')
        lbl = tk.Label(w, text=text, bg=Theme.BG_HEADER, fg=color,
                       font=('Consolas', 10, 'bold'), wraplength=380)
        lbl.pack(expand=True, fill=tk.BOTH)
        self._beep(1000, 20)
        w.after(duration, w.destroy)

    # ═══ AMBIENT SOUND ══════════════════════════════════════════════════════

    def start_ambient(self):
        self._ambient_melody = [
            (55, 400), (0, 100), (65, 300), (0, 100), (73, 200),
            (0, 50), (65, 200), (0, 50), (0, 400),
        ]

        def run():
            while True:
                if not hasattr(self, '_ambient_running') or not self._ambient_running:
                    break
                time.sleep(random.uniform(4, 8))
                if self._sound and random.random() < 0.4:
                    try:
                        for freq, dur in self._ambient_melody:
                            if not self._ambient_running:
                                return
                            if freq > 0:
                                winsound.Beep(freq, dur)
                            time.sleep(dur / 1000)
                    except Exception:
                        pass

        self._ambient_running = True
        threading.Thread(target=run, daemon=True).start()

    # ═══ RANDOM SYSTEM EVENTS ═════════════════════════════════════════════════

    def start_random_events(self):
        """Background thread that injects random [SYSTEM] / [NET] / [SEC]
        log messages into the console periodically, creating the illusion
        of a living, breathing network."""

        def run():
            while True:
                if not hasattr(self, '_random_events_running') or not self._random_events_running:
                    break
                # Random interval: 20–60 seconds between events
                time.sleep(random.uniform(20, 60))
                if self._boot_state != 'DONE':
                    continue
                try:
                    ev = g.random_event()
                    if ev is None:
                        continue
                    text, color, _ = ev
                    self.console_out(text, color)
                    g.add_log(text, 'info')
                except Exception:
                    pass

        self._random_events_running = True
        threading.Thread(target=run, daemon=True).start()

    def stop_random_events(self):
        self._random_events_running = False

    # ═══ SAVE / LOAD ════════════════════════════════════════════════════════

    def save(self):
        if g.save():
            self.console_out(_('Game saved!'), 'green')

    def load(self):
        if g.load():
            self.refresh_all()
            self.update_map()
            self.console_out(_('Game loaded!'), 'green')
        else:
            self.console_out(_('No save found.'), 'red')

    def export(self):
        p = filedialog.asksaveasfilename(defaultextension='.json',
                                          filetypes=[('JSON', '*.json')],
                                          initialfile=f'he_save_{int(time.time())}.json')
        if p and g.save(p):
            self.console_out(_fmt('Exported: {}', p), 'green')

    def import_(self):
        p = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
        if p and g.load(p):
            self.refresh_all()
            self.update_map()
            self.console_out(_('Imported!'), 'green')
        elif p:
            self.console_out(_('Invalid file.'), 'red')

    def auto_save_loop(self):
        if hasattr(self, '_autosave_running') and not self._autosave_running:
            return
        self._autosave_running = True
        try:
            if g and g.save(AUTO_FILE):
                pass
        except Exception:
            pass
        g.crypto_tick()
        hb = g.hackback()
        if hb:
            self.console_out(_fmt('⚠ {}', hb), 'red')
            self._sound_error()
        self.root.after(30000, self.auto_save_loop)

    def restart(self):
        """Save game and restart the entire UI."""
        self.restart_requested = True
        self._autosave_running = False
        g.save(AUTO_FILE)
        self.root.withdraw()  # hide old window cleanly
        self.root.quit()      # stop mainloop -> main.py creates new app

    def on_close(self):
        self.restart_requested = False
        self._autosave_running = False
        self.stop_random_events()
        g.save(AUTO_FILE)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# ═══════════════════════════════════════════════════════════════════════════════
# Import command handlers and panel dialogs (they patch methods onto HackerApp)
# ═══════════════════════════════════════════════════════════════════════════════

from ui import hud as _  # ensure hud is importable (HUDBackground used in __init__)
from ui.commands import *  # noqa: F401, F403 — patches h_* methods onto HackerApp
from ui.panels import *    # noqa: F401, F403 — patches dialog methods onto HackerApp
from ui.hud import HUDBackground  # noqa: F401 — re-export for importers

from ui.lang import _, _fmt

# ── Register remaining commands defined in panels.py / app.py ──
from engine.command_registry import CommandMeta as _CM

_reg = HackerApp._commands_registry if hasattr(HackerApp, '_commands_registry') else None
if _reg is None:
    # Fallback: get the singleton from CommandRegistry
    from engine.command_registry import CommandRegistry as _CR
    _reg = _CR()

_reg.register(_CM(name='missions', handler=HackerApp.h_missions,
                  help_text='Show active missions', category='missions'))
_reg.register(_CM(name='newmission', handler=HackerApp.h_newmission,
                  help_text='Generate new missions', category='missions'))
_reg.register(_CM(name='achievements', handler=HackerApp.h_achievements,
                  help_text='Show unlocked achievements', category='missions'))
_reg.register(_CM(name='market', handler=HackerApp.h_market,
                  help_text='Black market shop', category='exploits'))
_reg.register(_CM(name='skills', handler=HackerApp.h_skills,
                  help_text='Skill tree', category='system'))
_reg.register(_CM(name='view', handler=HackerApp.h_view,
                  help_text='3D server view', category='system'))
_reg.register(_CM(name='switch', handler=HackerApp.h_switch,
                  help_text='Trigger endgame switch', category='story'))
_reg.register(_CM(name='glitch', handler=lambda s, a, r: None,
                  help_text='Glitch visual effect', category='system'))