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

from engine.config import Colors, SAVE_FILE, AUTO_FILE
from engine.game import g
from data import HARDWARE, STORY_MISSIONS, DARIUS_EMAILS
from ui.rich_bridge import render_to_widget


# ═══════════════════════════════════════════════════════════════════════════════
# GlowFrame
# ═══════════════════════════════════════════════════════════════════════════════

class GlowFrame(tk.Frame):
    def __init__(self, parent, **kw):
        tk.Frame.__init__(self, parent, **kw)
        self.config(bg=kw.get('bg', Colors.dark),
                    highlightbackground=Colors.border2, highlightthickness=1,
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
        self.root.configure(bg=Colors.darker)
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

        self.hud = HUDBackground(self.root, Colors.black)

        self.main_frame = tk.Frame(self.root, bg=Colors.bg)
        self.main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.setup_title()
        self.setup_layout()
        self.setup_menu()
        self.setup_bindings()
        self.animate_particles()
        self.update_map()
        self.refresh_all()

        self.restart_requested = False
        self._boot_silent = True
        self._boot_state = 'BOOTING'
        self.root.after(500, self._animate_seps)
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
            'green': '#00ff88', 'red': '#ff2244', 'yellow': '#ffbb00',
            'cyan': '#00ddff', 'orange': '#ff6600', 'dim': '#335577',
            'white': '#cceeff', 'pink': '#ff0066', 'blue': '#4488ff',
        }
        c = cols.get(color, Colors.green)
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
            'green': '#00ff88', 'red': '#ff2244', 'yellow': '#ffbb00',
            'cyan': '#00ddff', 'orange': '#ff6600', 'dim': '#335577',
            'white': '#cceeff', 'pink': '#ff0066', 'blue': '#4488ff',
        }
        c = cols.get(color, Colors.green)
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
                self.root.config(highlightbackground=Colors.black, highlightthickness=0)

    # ═══ FAKE BOOT LINUX ════════════════════════════════════════════════════

    def _fake_boot_desktop(self):
        self._boot_win = tk.Toplevel(self.root)
        w = self._boot_win
        w.title('Boot')
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w.geometry(f'{sw}x{sh}+0+0')
        w.overrideredirect(True)
        w.configure(bg='#000000')
        self._boot_state = 'BOOTING'
        self._boot_hint_shown = False
        # Tutorial boot lines — hints for the login below
        boot_lines = [
            ("[    0.000000] Linux version 6.8.0-kali1-amd64 (root@kali)", "#888"),
            ("[    0.000000] Command line: BOOT_IMAGE=/vmlinuz root=/dev/sda1 ro quiet", "#888"),
            ("[    0.250000] Initializing cgroup subsys cpuset", "#aaa"),
            ("[    0.510000] CPU: Intel Core i9-13900K (24 core, 32 threads)", "#aaa"),
            ("[    1.020000] PCI: Enabling device 0000:00:1f.2 (SATA controller)", "#aaa"),
            ("[    1.350000] tty0: enabled on port 0x3f8 (IRQ 4)", "#aaa"),
            ("[    1.680000] EXT4-fs (sda1): mounted filesystem with ordered data mode", "#0a0"),
            ("[    2.010000] Loading kernel modules: iptable_filter, ip_tables", "#aaa"),
            ("[    2.340000] NET: Registered protocol family 10 (IPv6)", "#aaa"),
            ("[    2.670000] systemd[1]: Starting Network Manager...", "#aaa"),
            ("[    3.000000] systemd[1]: Reached target Multi-User System", "#0a0"),
            # ── Tutorial hints ──
            ("[    3.200000] WARNING: Backup credentials in /tmp/recovery.txt", "#ff0"),
            ("[    3.500000] NOTICE: /tmp/recovery.txt: valid recovery key", "#0a0"),
            ("[    3.800000] SYS: Connection to Darius.OWC server interrupted (timeout)", "#888"),
            ("[    4.100000] SEC: Last access: hacker — 14d ago — IP: <unknown>", "#888"),
            ("[    4.400000] NET: Scanning... 2 hosts found: secure.corp, nexus.owc", "#888"),
            ("[    4.700000] SYS: Log file: /var/log/auth.log — suspicious attempts", "#888"),
            ("[    5.000000] systemd[1]: Starting getty on tty1...", "#aaa"),
            ("", ""),
            ("  ██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ ", "#0f0"),
            ("  ██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗", "#0f0"),
            ("  ███████║███████║██║     █████╔╝ █████╗  ██████╔╝", "#0f0"),
            ("  ██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗", "#0f0"),
            ("  ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║", "#0f0"),
            ("  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝", "#0f0"),
            ("", ""),
            ("Kali GNU/Linux Rolling 2024.1 tty1", "#0f0"),
        ]
        self._boot_txt = tk.Text(w, bg='#000000', fg='#00ff88', font=('Consolas', 12),
                                  relief=tk.FLAT, bd=0, insertbackground='#00ff88', insertwidth=6)
        self._boot_txt.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self._boot_txt.config(state=tk.NORMAL)
        self._boot_animate(boot_lines, 0, lambda: self._boot_login_prompt())

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
        if self._boot_win and self._boot_win.winfo_exists():
            self._boot_win.destroy()
        self._boot_state = 'DONE'
        # Clean console and show transition
        self.console.config(state=tk.NORMAL)
        self.console.delete('1.0', tk.END)
        self.console.config(state=tk.DISABLED)
        self.console_out(_('\n📧 YOU HAVE 1 NEW EMAIL from Darius. Type EMAIL to read it.'), 'yellow')
        self.console_out(_('Type HELP for commands.'), 'dim')
        g.add_log(_('System online. Darius legacy active.'), 'ok')
        self._beep(660, 30)

    # ═══ TITLE BAR ══════════════════════════════════════════════════════════

    def setup_title(self):
        title = tk.Frame(self.main_frame, bg=Colors.black)
        title.pack(fill=tk.X, pady=(3, 0))
        txt = tk.Label(title, text='◈ HACKER EVOLUTION ◈  404 Fun Not Found',
                       bg=Colors.black, fg=Colors.cyan, font=('Consolas', 18, 'bold'))
        txt.pack()
        self.pulse_label(txt)
        sub = tk.Label(title, text='└── Hacking simulator · exosyphen style ──┘',
                       bg=Colors.black, fg=Colors.dim, font=('Consolas', 9))
        sub.pack()
        gb = tk.Frame(self.main_frame, bg=Colors.bg, height=4)
        gb.pack(fill=tk.X)
        self._glow_bar(self.main_frame)

    def pulse_label(self, lbl, step=0):
        if not lbl.winfo_exists():
            return
        bright = 0.6 + 0.4 * math.sin(step / 20)
        r = int(20 * bright)
        gv = int(200 * bright)
        bv = int(255 * bright)
        if step > 0 and step % 120 < 3:
            glitch_off = random.randint(-2, 2)
            lbl.config(fg=f'#{r + glitch_off:02x}{gv:02x}{bv:02x}')
            if step % 120 == 0:
                self._beep(40, 30)
        else:
            lbl.config(fg=f'#{r:02x}{gv:02x}{bv:02x}')
        lbl.after(50, lambda: self.pulse_label(lbl, step + 1))

    # ═══ GLOW BAR ═══════════════════════════════════════════════════════════

    def _glow_bar(self, parent):
        c = tk.Canvas(parent, height=3, bg=Colors.bg, highlightthickness=0)
        c.pack(fill=tk.X)
        c.bind('<Configure>', lambda e: self._draw_glow_bar(c))
        return c

    def _draw_glow_bar(self, c):
        c.delete('all')
        w = c.winfo_width()
        if w < 10:
            return
        for i in range(w):
            b = 0.3 + 0.7 * math.sin(i / 10 - math.pi / 2)
            b = max(0.05, b)
            r = int(5 * b)
            gv = int(60 + 80 * b)
            bl = int(80 + 170 * b)
            c.create_line(i, 0, i, 3, fill=f'#{r:02x}{gv:02x}{bl:02x}', tags='g')
        c.lower('g')

    # ═══ ANIMATED SEPARATOR ═════════════════════════════════════════════════

    def _animated_sep(self, parent):
        c = tk.Canvas(parent, height=6, bg=Colors.bg, highlightthickness=0)
        c.pack(fill=tk.X)
        self._sep_canvases.append(c)
        return c

    def _animate_seps(self):
        t = self.root.tk.call('clock', 'milliseconds') // 200
        for c in self._sep_canvases:
            if c.winfo_exists():
                self._draw_sep(c, t)
        if random.random() < 0.08 and g.trace_level > 30:
            c = self.hud.canvas
            w = c.winfo_width()
            h = c.winfo_height()
            if w > 50:
                y = random.randint(0, h - 4)
                alpha = 0.1 + random.random() * 0.15
                c.create_rectangle(0, y, w, y + random.randint(1, 3),
                                   fill=f'#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}',
                                   outline='', tags='noiseband')
                self.root.after(100, lambda: c.delete('noiseband'))
        self.root.after(200, self._animate_seps)

    def _draw_sep(self, c, t):
        c.delete('all')
        w = c.winfo_width()
        if w < 10:
            return
        mid = 4
        seg = 20
        for i in range(0, w, seg):
            b = 0.3 + 0.7 * ((math.sin(i / 10 + t) + 1) / 2)
            r = int(10 + 30 * b)
            gv = int(40 + 140 * b)
            bl = int(80 + 160 * b)
            col = f'#{r:02x}{gv:02x}{bl:02x}'
            c.create_line(i, mid, i + seg // 2, mid, fill=col, width=2)
            dot = 0.3 + 0.7 * ((math.sin(i / 10 + t + 1) + 1) / 2)
            c.create_oval(i + seg // 2 - 1, mid - 1, i + seg // 2 + 1, mid + 1, fill=col, outline='')

    # ═══ LAYOUT ═════════════════════════════════════════════════════════════

    def setup_layout(self):
        self.root.update_idletasks()
        avail = max(800, self.root.winfo_width())
        pw = tk.PanedWindow(self.main_frame, bg=Colors.bg,
                            sashrelief=tk.RAISED, sashwidth=2, sashpad=0)
        pw.pack(fill=tk.BOTH, expand=True, padx=5, pady=3)
        left = tk.Frame(pw, bg=Colors.bg)
        pw.add(left, width=int(avail * 0.62))
        cf = tk.Frame(left, bg=Colors.bg)
        cf.pack(fill=tk.BOTH, expand=True)
        chdr = tk.Frame(cf, bg=Colors.dark)
        chdr.pack(fill=tk.X)
        tk.Label(chdr, text='▶ CONSOLE', bg=Colors.dark, fg=Colors.cyan,
                 font=('Consolas', 10, 'bold')).pack(side=tk.LEFT, padx=8, pady=2)
        tk.Label(chdr, text='[F1=Help]', bg=Colors.dark, fg=Colors.dim,
                 font=('Consolas', 8)).pack(side=tk.RIGHT, padx=8)
        dbl = tk.Frame(cf, bg=Colors.bg)
        dbl.pack(fill=tk.X)
        tk.Frame(dbl, bg=Colors.cyan2, height=2).pack(fill=tk.X)
        tk.Frame(dbl, bg=Colors.cyan4, height=1).pack(fill=tk.X)
        glow_frame = tk.Frame(cf, bg='#004466', highlightthickness=0)
        glow_frame.pack(fill=tk.BOTH, expand=True, padx=1)
        self.console = tk.Text(glow_frame, bg=Colors.darker, fg=Colors.cyan,
                                font=('Consolas', 11), relief=tk.FLAT, padx=8, pady=5,
                                height=18, wrap=tk.WORD, state=tk.DISABLED, borderwidth=0)
        self.console.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.console.configure(insertbackground=Colors.cyan, insertwidth=7,
                                insertofftime=300, insertontime=600)
        sbar = tk.Scrollbar(cf, orient=tk.VERTICAL, command=self.console.yview,
                            bg=Colors.dark, troughcolor=Colors.black,
                            activebackground=Colors.green, width=10)
        self.console.configure(yscrollcommand=sbar.set, highlightthickness=0)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.pack(fill=tk.BOTH, expand=True)
        inp = tk.Frame(cf, bg=Colors.dark, height=32)
        inp.pack(fill=tk.X)
        self.prompt_label = tk.Label(inp, text='root@hud:~$ ', bg=Colors.dark,
                                      fg=Colors.cyan, font=('Consolas', 12, 'bold'), padx=5)
        self.prompt_label.pack(side=tk.LEFT)
        self.cursor_label = tk.Label(inp, text='█', bg=Colors.dark, fg=Colors.cyan,
                                      font=('Consolas', 12, 'bold'))
        self.cursor_label.pack(side=tk.LEFT, padx=(0, 2))
        self._blink_cursor()
        self.input_var = tk.StringVar()
        self.input = tk.Entry(inp, textvariable=self.input_var,
                              bg=Colors.dark, fg=Colors.cyan, insertbackground=Colors.cyan,
                              font=('Consolas', 12), relief=tk.FLAT, bd=0,
                              highlightthickness=0, disabledbackground=Colors.dark)
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input.focus()
        self.input.bind('<Return>', self.on_cmd)
        self.input.bind('<Up>', lambda e: self.history(-1))
        self.input.bind('<Down>', lambda e: self.history(1))
        self.input.bind('<Key>', lambda e: (self._sound_keypress(), self.root.after(5, self._input_glow)))
        self._input_glow_active = False
        self._build_layout_rest(left, pw, avail)

    def _input_glow(self):
        if self._input_glow_active:
            return
        self._input_glow_active = True
        self.input.config(bg=Colors.dark, highlightbackground=Colors.cyan, highlightthickness=1)
        self.root.after(150, lambda: self.input.config(highlightthickness=0) if self._input_glow_active else None)
        self.root.after(200, lambda: setattr(self, '_input_glow_active', False))

    def _build_layout_rest(self, left, pw, avail):
        # Map
        mf = tk.Frame(left, bg=Colors.black, height=190)
        mf.pack(fill=tk.X)
        self.map_canvas = tk.Canvas(mf, bg=Colors.darker, highlightthickness=0, height=185)
        self.map_canvas.pack(fill=tk.BOTH, expand=True, padx=1, pady=2)
        self.map_canvas.bind('<Button-1>', self.map_click)
        self.map_canvas.bind('<Button-3>', self.map_right_click)

        # Right panel
        right = tk.Frame(pw, bg=Colors.bg)
        pw.add(right, width=int(avail * 0.35))

        # System Panel
        sf = tk.LabelFrame(right, text=' SYSTEM PANEL ', bg=Colors.bg,
                           fg=Colors.cyan, font=('Consolas', 10, 'bold'),
                           relief=tk.RIDGE, bd=2, padx=12, pady=8,
                           highlightbackground=Colors.border2, highlightthickness=2)
        sf.pack(fill=tk.X, pady=(0, 5))
        self.sys = {}
        for k, lbl, unit, clr in [
            ('money', _('💰 Money'), '', '#ffbb00'),
            ('trace', '⚠️ Trace', '%', '#ff2244'),
            ('score', '🏆 Score', '', '#00ff88'),
            ('level', '📊 Level', '', '#00ddff'),
            ('hacks', '💻 Hack', '', '#00ff88'),
            ('trace_cnt', '🕵️ Traced', '', '#ff6600'),
        ]:
            f = tk.Frame(sf, bg=Colors.bg)
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=lbl, bg=Colors.bg, fg=Colors.dim,
                     font=('Consolas', 9), anchor='w', width=14).pack(side=tk.LEFT)
            lb = tk.Label(f, text='-', bg=Colors.bg, fg=clr,
                          font=('Consolas', 11, 'bold'), anchor='e')
            lb.pack(side=tk.RIGHT)
            self.sys[k] = lb

        # Trace bar
        tf = tk.Frame(sf, bg=Colors.bg)
        tf.pack(fill=tk.X, pady=3)
        tk.Label(tf, text='[', bg=Colors.bg, fg=Colors.dim,
                 font=('Consolas', 8)).pack(side=tk.LEFT)
        self.trace_canvas = tk.Canvas(tf, bg=Colors.dark, highlightthickness=0, height=12, width=200)
        self.trace_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Label(tf, text=']', bg=Colors.bg, fg=Colors.dim,
                 font=('Consolas', 8)).pack(side=tk.LEFT)

        # Bounce
        bf = tk.Frame(sf, bg=Colors.bg)
        bf.pack(fill=tk.X, pady=2)
        tk.Label(bf, text='🔁 BOUNCE', bg=Colors.bg, fg=Colors.dim,
                 font=('Consolas', 9)).pack(side=tk.LEFT)
        self.bounce_lbl = tk.Label(bf, text='0 hop', bg=Colors.bg, fg='#ff0066',
                                   font=('Consolas', 11, 'bold'))
        self.bounce_lbl.pack(side=tk.RIGHT)

        # Hardware
        self._animated_sep(right)
        hw = tk.LabelFrame(right, text=' HARDWARE ', bg=Colors.bg,
                           fg=Colors.cyan, font=('Consolas', 9, 'bold'),
                           relief=tk.RIDGE, bd=2, highlightbackground=Colors.border2, highlightthickness=1)
        hw.pack(fill=tk.X, pady=(0, 5))
        self.hw_lbls = {}
        for h in HARDWARE:
            f = tk.Frame(hw, bg=Colors.bg)
            f.pack(fill=tk.X, pady=1)
            tk.Label(f, text=h[0], bg=Colors.bg, fg=Colors.dim,
                     font=('Consolas', 9), anchor='w', width=16).pack(side=tk.LEFT, padx=5)
            lb = tk.Label(f, text='-', bg=Colors.bg, fg=Colors.cyan,
                          font=('Consolas', 9, 'bold'), anchor='e')
            lb.pack(side=tk.RIGHT, padx=5)
            self.hw_lbls[h[1]] = lb

        # Progress bar
        self.pf = tk.Frame(right, bg=Colors.bg)
        self.pv = tk.DoubleVar()
        self.pb = ttk.Progressbar(self.pf, variable=self.pv, length=300,
                                   mode='determinate', style='cyan.Horizontal.TProgressbar')
        self.pb.pack(pady=(5, 0))
        self.ps = tk.Label(self.pf, text='', bg=Colors.bg, fg=Colors.cyan,
                           font=('Consolas', 10))
        self.ps.pack()
        style = ttk.Style()
        style.configure('cyan.Horizontal.TProgressbar', background='#00ddff', troughcolor='#0a1830')
        self.pf.pack_forget()

        # Messages
        self._animated_sep(right)
        mg = tk.LabelFrame(right, text=' MESSAGES ', bg=Colors.bg,
                           fg=Colors.cyan, font=('Consolas', 9, 'bold'),
                           relief=tk.RIDGE, bd=2, highlightbackground=Colors.border2, highlightthickness=1)
        mg.pack(fill=tk.BOTH, expand=True)
        self.msg = tk.Text(mg, bg=Colors.darker, fg=Colors.cyan,
                           font=('Consolas', 10), relief=tk.FLAT, height=6, state=tk.DISABLED)
        self.msg.pack(fill=tk.BOTH, expand=True, pady=2, padx=2)

        # Buttons
        btn = tk.Frame(right, bg=Colors.bg)
        btn.pack(fill=tk.X, pady=2)
        for t, c in [
            ('💾 Save', self.save),
            ('📂 Load', self.load),
            ('📤 Export', self.export),
            ('📥 Import', self.import_),
            ('🔧 Upgrade', self.show_upgrade),
            ('⚙ Config', self.show_config),
        ]:
            tk.Button(btn, text=t, command=c, bg=Colors.dark, fg=Colors.cyan,
                      activebackground='#1a3a6a', activeforeground=Colors.white,
                      font=('Consolas', 9), relief=tk.RAISED, bd=1, padx=6, pady=2,
                      cursor='hand2').pack(side=tk.LEFT, padx=1)

    # ═══ MENU ═══════════════════════════════════════════════════════════════

    def setup_menu(self):
        mb = tk.Menu(self.root, bg=Colors.dark, fg=Colors.cyan,
                     activebackground='#1a3a6a', activeforeground=Colors.white)
        self.root.config(menu=mb)
        fm = tk.Menu(mb, tearoff=0, bg=Colors.dark, fg=Colors.cyan,
                     activebackground='#1a3a6a', activeforeground=Colors.white)
        mb.add_cascade(label='File', menu=fm)
        fm.add_command(label='🆕 Nuova Partita', command=self.h_newgame_wrapper)
        fm.add_separator()
        fm.add_command(label='💾 Salva', command=self.save)
        fm.add_command(label='📂 Carica', command=self.load)
        fm.add_separator()
        fm.add_command(label='📤 Export...', command=self.export)
        fm.add_command(label='📥 Import...', command=self.import_)
        fm.add_separator()
        fm.add_command(label='⚙ Settings', command=self.show_config)
        fm.add_separator()
        fm.add_command(label='🚪 Esci', command=self.on_close)

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
            'green': '#00ff88', 'red': '#ff2244', 'yellow': '#ffbb00',
            'cyan': '#00ddff', 'orange': '#ff6600', 'dim': '#335577',
            'white': '#cceeff', 'pink': '#ff0066', 'blue': '#4488ff',
        }
        c = cols.get(color, Colors.green)
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

    def _update_prompt(self):
        if not hasattr(self, 'prompt_label'):
            return
        if g.current_server:
            self.prompt_label.config(text=f'root@{g.current_server["name"].split(".")[0]}:~$ ', fg=Colors.green)
        else:
            self.prompt_label.config(text='root@hud:~$ ', fg=Colors.cyan)

    def _impact_wave(self, cx, cy):
        for r in range(5, 80, 5):
            self.root.after(r * 5, lambda rr=r: self._draw_impact_ring(cx, cy, rr) if self.map_canvas.winfo_exists() else None)
        self._particle_burst(cx, cy, Colors.cyan, 30)
        self._screen_shake(200, 2)

    def _draw_impact_ring(self, cx, cy, r):
        self.map_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=Colors.cyan, width=2, tags='impact')
        self.root.after(120, lambda: self.map_canvas.delete('impact'))

    # ═══ PARTICLE BURST ═════════════════════════════════════════════════════

    def _particle_burst(self, cx, cy, color='#00ddff', count=25):
        pts = [[random.uniform(-50, 50), random.uniform(-50, 50), random.uniform(1, 4)] for _ in range(count)]

        def step(n=0):
            if n >= 20:
                return
            for p in pts:
                p[0] += p[2] * 1.5
                p[1] += p[2] * 1.5
                p[2] *= 0.9
                if n > 0:
                    self.map_canvas.create_oval(cx + p[0] - 2, cy + p[1] - 2,
                                                cx + p[0] + 2, cy + p[1] + 2,
                                                fill=color, outline='', tags='burst')
            self.root.after(40, lambda: (self.map_canvas.delete('burst'), step(n + 1)))

        step()

    # ═══ MAP ════════════════════════════════════════════════════════════════

    def update_map(self):
        self.map_canvas.delete('all')
        w = self.map_canvas.winfo_width() or 600
        h = self.map_canvas.winfo_height() or 185
        n = len(g.servers)
        if n == 0:
            return
        cx, cy = w // 2, h // 2
        radius = min(w, h) * 0.32

        # Radar grid
        step_ = max(1, int(radius * 0.25))
        for rng in range(step_, int(radius) + 1, step_):
            self.map_canvas.create_oval(cx - rng, cy - rng, cx + rng, cy + rng,
                                        outline=Colors.grid, width=1, tags='map')
        self.map_canvas.create_line(cx - radius, cy, cx + radius, cy, fill=Colors.grid, width=1, tags='map')
        self.map_canvas.create_line(cx, cy - radius, cx, cy + radius, fill=Colors.grid, width=1, tags='map')
        self.map_canvas.create_line(cx - radius, cy - radius, cx + radius, cy + radius, fill=Colors.grid, width=1, tags='map')
        self.map_canvas.create_line(cx + radius, cy - radius, cx - radius, cy + radius, fill=Colors.grid, width=1, tags='map')
        self.map_canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=Colors.cyan3, outline='', tags='map')

        # Node positions
        for i, s in enumerate(g.servers):
            a = 2 * math.pi * i / n - math.pi / 2
            x = cx + radius * math.cos(a)
            y = cy + radius * math.sin(a)
            s['pos'] = (x, y)

        # Radar sweep
        radar_angle = self.bounce_anim * 0.02
        rx = cx + radius * math.cos(radar_angle)
        ry = cy + radius * math.sin(radar_angle)
        for ri in range(20, 0, -1):
            a2 = radar_angle - 0.03 * ri
            alpha = 0.15 * (1 - ri / 20)
            rrx = cx + radius * 0.3 * math.cos(a2)
            rry = cy + radius * 0.3 * math.sin(a2)
            self.map_canvas.create_line(cx, cy, rrx, rry,
                                        fill=f'#{int(255 * alpha):02x}{int(255 * alpha):02x}{int(255 * alpha):02x}',
                                        width=ri // 4 + 1, tags='mapradar')
        self.map_canvas.create_line(cx, cy, rx, ry, fill=Colors.cyan, width=2, tags='mapradar')
        self.root.after(500, lambda: self.map_canvas.delete('mapradar'))

        # Connection lines
        now_t = time.time()
        for i, s1 in enumerate(g.servers):
            x1, y1 = s1['pos']
            for j in range(i + 1, n):
                x2, y2 = g.servers[j]['pos']
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy)
                steps = max(1, int(dist / 8))
                for s_ in range(steps):
                    t1, t2 = s_ / steps, (s_ + 1) / steps
                    bright = 0.15 + 0.2 * math.sin(t1 * math.pi)
                    bv = int(255 * bright)
                    gv = int(180 * bright)
                    self.map_canvas.create_line(x1 + dx * t1, y1 + dy * t1, x1 + dx * t2, y1 + dy * t2,
                                                fill=f'#{gv:02x}{gv:02x}{bv:02x}', width=1, tags='map')
                if (i + j + int(now_t * 2)) % 3 == 0:
                    tt = (now_t * 0.5 + (i * 7 + j * 13) * 0.01) % 1
                    px, py = x1 + dx * tt, y1 + dy * tt
                    sz = 1 + int(0.5 + 0.5 * math.sin(tt * math.pi))
                    self.map_canvas.create_oval(px - sz, py - sz, px + sz, py + sz,
                                                fill=Colors.cyan, outline='', tags='map')

        # Bounce lines
        for bi in range(1, len(g.bounce_chain)):
            h1 = g.bounce_chain[bi - 1]
            h2 = g.bounce_chain[bi]
            p1 = next((s for s in g.servers if s['name'] == h1), None)
            p2 = next((s for s in g.servers if s['name'] == h2), None)
            if p1 and p2:
                x1, y1 = p1['pos']
                x2, y2 = p2['pos']
                bright = 0.5 + 0.3 * math.sin(self.bounce_anim / 8 + bi * 1.5)
                gv = int(180 * bright)
                bv = int(255 * bright)
                col = f'#{gv:02x}{gv:02x}{bv:02x}'
                self.map_canvas.create_line(x1, y1, x2, y2, fill=Colors.cyan4, width=7, tags='map')
                self.map_canvas.create_line(x1, y1, x2, y2, fill=col, width=4, tags='map')
                self.map_canvas.create_line(x1, y1, x2, y2, fill=Colors.cyan, width=2, tags='map')
                t = (self.bounce_anim / 30) % 1
                px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                pulse = 0.5 + 0.5 * math.sin(self.bounce_anim / 5)
                sz = 2 + int(pulse * 2)
                self.map_canvas.create_oval(px - sz, py - sz, px + sz, py + sz,
                                            fill=Colors.cyan, outline=Colors.white, width=1, tags='map')
                for tt in range(3):
                    tt_ = (t - 0.1 * (tt + 1)) % 1
                    tpx, tpy = x1 + (x2 - x1) * tt_, y1 + (y2 - y1) * tt_
                    tb = 0.3 - 0.1 * tt
                    self.map_canvas.create_oval(tpx - 2, tpy - 2, tpx + 2, tpy + 2,
                                                fill=f'#{int(100 * tb):02x}{int(100 * tb):02x}{int(255 * tb):02x}',
                                                outline='', tags='map')

        # Nodes
        now = time.time()
        for s in g.servers:
            x, y = s['pos']
            is_hacked = g.hacked(s)
            if is_hacked:
                col, fill = Colors.green, Colors.cyan4
                icon = '✓'
            elif s['decrypted']:
                col, fill = Colors.yellow, Colors.dark
                icon = '◉'
            elif s['scanned']:
                col, fill = Colors.orange, Colors.dark
                icon = '◌'
            else:
                col, fill = Colors.cyan3, Colors.darker
                icon = '○'
            in_bounce = s['name'] in g.bounce_chain
            is_connected = s is g.current_server
            r = 9 if not in_bounce else 13
            glow_r = 18 if in_bounce else 14
            if is_connected:
                r, glow_r = 15, 22
            rh = int(col[1:3], 16)
            gh = int(col[3:5], 16)
            bh = int(col[5:7], 16)
            for layer in range(3, 0, -1):
                lr = glow_r * layer / 3
                lc = f'#{rh * layer // 3:02x}{gh * layer // 3:02x}{bh * layer // 3:02x}'
                self.map_canvas.create_oval(x - lr, y - lr, x + lr, y + lr,
                                            outline='', fill=lc, tags='map')
            if is_hacked:
                p = 0.5 + 0.5 * math.sin(now * 3)
                pr = glow_r + 4 + int(p * 6)
                pc = f'#{int(80 + 175 * p):02x}{int(150 + 105 * p):02x}{int(255):02x}'
                self.map_canvas.create_oval(x - pr, y - pr, x + pr, y + pr,
                                            outline=pc, width=2, tags='map')
            if is_connected:
                cr = glow_r + 8
                self.map_canvas.create_oval(x - cr, y - cr, x + cr, y + cr,
                                            outline=Colors.cyan, width=1, dash=(3, 3), tags='map')
            self.map_canvas.create_oval(x - r, y - r, x + r, y + r,
                                        outline=col, fill=fill, width=2, tags='map')
            if is_hacked or s['decrypted']:
                hi = r * 0.4
                self.map_canvas.create_oval(x - hi, y - hi, x + hi, y + hi,
                                            outline='', fill=Colors.cyan if is_hacked else Colors.yellow, tags='map')
            desc_lower = s['desc'].lower()
            if 'bank' in desc_lower or 'atm' in desc_lower:
                icon = '$'
            elif 'military' in desc_lower or 'satellite' in desc_lower:
                icon = '⚠'
            elif 'gsm' in desc_lower or 'tower' in desc_lower:
                icon = '📡'
            elif 'corporate' in desc_lower or 'mainframe' in desc_lower:
                icon = '🏢'
            elif 'car' in desc_lower or 'traffic' in desc_lower:
                icon = '🚦'
            elif 'office' in desc_lower:
                icon = '💻'
            if s.get('is_gov'):
                icon = '🏛️'
            self.map_canvas.create_text(x + 1, y - r - 9, text=s['name'][:28],
                                        fill='#000000', font=('Consolas', 8, 'bold'), anchor='s', tags='map')
            self.map_canvas.create_text(x, y - r - 10, text=s['name'][:28],
                                        fill=col, font=('Consolas', 8, 'bold'), anchor='s', tags='map')
            self.map_canvas.create_text(x, y - r - 24, text=icon,
                                        fill=col, font=('Consolas', 9), anchor='s', tags='map')
            if s['scanned']:
                self.map_canvas.create_text(x + 1, y + r + 6, text='/'.join(str(p) for p in s['ports']),
                                            fill='#000000', font=('Consolas', 7), anchor='n', tags='map')
                self.map_canvas.create_text(x, y + r + 5, text='/'.join(str(p) for p in s['ports']),
                                            fill=Colors.cyan3, font=('Consolas', 7), anchor='n', tags='map')
            if is_connected:
                self.map_canvas.create_text(x, y + r + 16, text='← CONNECTED',
                                            fill=Colors.cyan, font=('Consolas', 7, 'bold'), anchor='n', tags='map')
        self.bounce_anim += 1

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
                m = tk.Menu(self.root, tearoff=0, bg=Colors.dark, fg=Colors.cyan,
                            activebackground='#1a3a6a', activeforeground=Colors.white)
                m.add_command(label=f'🔍 SCAN {s["name"]}',
                              command=lambda h=s["name"]: self.exec_cmd(f'scan {h}'))
                if s['scanned']:
                    if not s['decrypted']:
                        m.add_command(label=f'🔓 DECRYPT {s["name"]}',
                                      command=lambda h=s["name"]: self.exec_cmd(f'decrypt {h}'))
                    for p in s['ports']:
                        if not s['cracked'].get(p):
                            m.add_command(label=f'🔨 CRACK {s["name"]}:{p}',
                                          command=lambda h=s["name"], pp=p: self.exec_cmd(f'crack {h} {pp}'))
                if g.hacked(s):
                    m.add_command(label=f'🔗 BOUNCE {s["name"]}',
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
        self.sys['money'].config(text=f'${g.money:,}')
        tr = g.trace_level
        tc = '#00ff88' if tr < 50 else '#ffbb00' if tr < 80 else '#ff2244'
        if tr > 70 and hasattr(self, '_trace_wobble') and self._trace_wobble:
            off = random.randint(-1, 1)
            self.sys['trace'].config(text=f'{tr:.1f}%', fg=tc, padx=10 + off, pady=2 + off)
        else:
            self.sys['trace'].config(text=f'{tr:.1f}%', fg=tc, padx=10, pady=2)
        self._trace_wobble = tr > 70
        self.sys['score'].config(text=str(g.score))
        self.sys['level'].config(text=str(g.level))
        self.sys['hacks'].config(text=str(g.hack_count))
        self.sys['trace_cnt'].config(text=str(g.trace_count))
        self.bounce_lbl.config(text=f'{len(g.bounce_chain)} hop ({g.trace_mult()}x)')

        # Trace bar VU meter
        self.trace_canvas.delete('all')
        tw = self.trace_canvas.winfo_width() or 200
        segments = 20
        seg_w = max(4, tw // segments - 2)
        fill_seg = int(segments * tr / 100)
        for i in range(segments):
            sx = i * (seg_w + 2)
            sy = 0
            c = '#00ff88' if i < segments * 0.5 else '#ffbb00' if i < segments * 0.8 else '#ff2244'
            if i < fill_seg:
                self.trace_canvas.create_rectangle(sx, sy, sx + seg_w, 12, fill=c, outline=Colors.dark, width=1, tags='tbar')
            else:
                self.trace_canvas.create_rectangle(sx, sy, sx + seg_w, 12, fill=Colors.darker, outline=Colors.dark, width=1, tags='tbar')
        pulse = 0.5 + 0.5 * math.sin(time.time() * 8) if tr > 70 else 0
        glow = int(255 * (0.3 + pulse * 0.7)) if tr > 70 else 80
        self.trace_canvas.create_text(tw // 2, 6, text=f'TRACE {tr:.0f}%',
                                      fill=f'#{glow:02x}{glow:02x}{glow:02x}', font=('Consolas', 9, 'bold'), tags='tbar')

        for h in HARDWARE:
            lvl = g.hw_lvl(h[1])
            clr = '#00ff88' if lvl >= h[5] else '#ffbb00' if lvl > 0 else Colors.dim
            self.hw_lbls[h[1]].config(text=f'{lvl}/{h[5]}', fg=clr)

        if hasattr(self, 'console'):
            parent = self.console.master
            if parent:
                if g.current_server:
                    parent.config(bg='#006633' if g.hacked(g.current_server) else '#005566')
                elif tr > 70:
                    parent.config(bg=f'#{int(80 + 80 * math.sin(time.time() * 4)):02x}0000')
                else:
                    parent.config(bg='#004466')
        self.render_msg()
        self.render_news()
        self.trace_alarm()
        self.check_achievements()
        g.check_missions()
        self.glitch()

    def render_msg(self):
        self.msg.config(state=tk.NORMAL)
        self.msg.delete('1.0', tk.END)
        for m in g.log[:8]:
            c = {'ok': '#00ff88', 'fail': '#ff2244', 'warn': '#ffbb00', 'info': '#4488ff'}.get(m[1], '#00ff88')
            self.msg.insert(tk.END, m[0] + '\n')
        self.msg.see(tk.END)
        self.msg.config(state=tk.DISABLED)

    def render_news(self):
        self.msg.config(state=tk.NORMAL)
        self.msg.delete('1.0', tk.END)
        for n in g.news[:6]:
            self.msg.insert(tk.END, n + '\n')
        self.msg.see(tk.END)
        self.msg.config(state=tk.DISABLED)

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
            w = c.winfo_width()
            for _ in range(random.randint(1, 3)):
                y = random.randint(0, c.winfo_height() - 2)
                c.create_line(0, y, w, y, fill=Colors.cyan, width=random.randint(1, 3), tags='glitch')
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
        w.configure(bg=Colors.black)
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = sw - 420
        y = sh - 120
        w.geometry(f'400x50+{x}+{y}')
        lbl = tk.Label(w, text=text, bg=Colors.black, fg=color,
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