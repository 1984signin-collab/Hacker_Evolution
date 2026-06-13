#!/usr/bin/env python3
# HACKER EVOLUTION — Dialog panels (gov portal, upgrade, market, skills, switch, 3D view)
# These are patched onto HackerApp at import time.

import math
import random
import time
import tkinter as tk
from tkinter import ttk

from engine.config import Colors
from ui.theme import Theme
from engine.game import g
from data import HARDWARE, DARIUS_EMAILS, STORY_MISSIONS
from ui.lang import LANGUAGES, set_lang, get_lang, _, _fmt


# ═══════════════════════════════════════════════════════════════════════════════
# Gov Login Portal
# ═══════════════════════════════════════════════════════════════════════════════

def _gov_login_portal(self, server):
    w = tk.Toplevel(self.root)
    w.title(_fmt('Portal Login — {}', server["name"]))
    w.geometry('600x520+400+150')
    w.configure(bg='#f0f0f0')
    w.resizable(False, False)
    hdr = tk.Frame(w, bg='#1a237e', height=80)
    hdr.pack(fill=tk.X)
    tk.Label(hdr, text=_('🇺🇸  UNITED STATES GOVERNMENT'), bg='#1a237e', fg='white',
             font=('Segoe UI', 14, 'bold')).pack(pady=(15, 0))
    tk.Label(hdr, text=_('SECURE ACCESS PORTAL  |  Classification Level: TOP SECRET'),
             bg='#1a237e', fg='#90caf9', font=('Segoe UI', 9)).pack()
    warn = tk.Frame(w, bg='#b71c1c', height=25)
    warn.pack(fill=tk.X)
    tk.Label(warn, text=_('⚠  WARNING: This system is for authorized use only. All access is monitored and logged.  ⚠'),
             bg='#b71c1c', fg='white', font=('Segoe UI', 8, 'bold')).pack()
    body = tk.Frame(w, bg='white', padx=40, pady=30)
    body.pack(fill=tk.BOTH, expand=True)
    tk.Label(body, text=_('SECURE LOGIN'), bg='white', fg='#1a237e',
             font=('Segoe UI', 16, 'bold')).pack(anchor='w')
    tk.Label(body, text=_fmt('Server: {}', server["name"]), bg='white', fg='#666',
             font=('Segoe UI', 9)).pack(anchor='w')
    tk.Label(body, text='', bg='white').pack(pady=5)
    tk.Label(body, text=_('Username:'), bg='white', fg='#333',
             font=('Segoe UI', 10)).pack(anchor='w')
    un = tk.Entry(body, bg='#fafafa', fg='#333', font=('Consolas', 11),
                  relief=tk.SUNKEN, bd=1, width=40)
    un.pack(fill=tk.X, pady=(0, 10))
    tk.Label(body, text=_('Password:'), bg='white', fg='#333',
             font=('Segoe UI', 10)).pack(anchor='w')
    pw = tk.Entry(body, bg='#fafafa', fg='#333', font=('Consolas', 11),
                  relief=tk.SUNKEN, bd=1, show='•', width=40)
    pw.pack(fill=tk.X, pady=(0, 15))
    badge = tk.Frame(body, bg='#e8eaf6', relief=tk.GROOVE, bd=1)
    badge.pack(fill=tk.X, pady=(0, 10))
    tk.Label(badge, text=_fmt('🔒  Connection: TLS 1.3  |  Session: {}  |  PKI: DoD CA-5', random.choice(
        ['AES-256-GCM', 'Chacha20-Poly1305'])),
             bg='#e8eaf6', fg='#333', font=('Segoe UI', 8)).pack(pady=3)
    btn_frame = tk.Frame(body, bg='white')
    btn_frame.pack(fill=tk.X)
    err_lbl = tk.Label(body, text='', bg='white', fg='red', font=('Segoe UI', 9))
    err_lbl.pack()

    def do_login():
        u = un.get()
        p = pw.get()
        if not u or not p:
            err_lbl.config(text=_('✗  Enter username and password.'))
            return
        if len(p) < 6:
            err_lbl.config(text=_('✗  Password too short.'))
            return
        if u.lower() == 'admin' and p == 'classified':
            w.destroy()
            self._gov_dashboard(server)
        elif u.lower() == 'root' and p.startswith('toor'):
            w.destroy()
            self._gov_dashboard(server)
        else:
            err_lbl.config(text=_('✗  Access denied. Invalid credentials.'))
            self._sound_error()

    tk.Button(btn_frame, text=_('  SIGN IN  '), command=do_login,
              bg='#1a237e', fg='white', font=('Segoe UI', 10, 'bold'),
              relief=tk.RAISED, bd=2, activebackground='#283593',
              activeforeground='white', padx=20, pady=4, cursor='hand2').pack(side=tk.LEFT)
    tk.Button(btn_frame, text=_('Cancel'), command=w.destroy,
              bg='#ddd', fg='#333', font=('Segoe UI', 10),
              relief=tk.FLAT, bd=0, padx=10).pack(side=tk.LEFT, padx=10)


# ═══════════════════════════════════════════════════════════════════════════════
# Gov Dashboard
# ═══════════════════════════════════════════════════════════════════════════════

def _gov_dashboard(self, server):
    w = tk.Toplevel(self.root)
    title = _fmt('CLASSIFIED — {}', server["name"])
    w.title(title)
    w.geometry('720x540+350+130')
    w.configure(bg='#f5f5f5')
    w.resizable(False, False)
    hdr = tk.Frame(w, bg='#1a237e', height=70)
    hdr.pack(fill=tk.X)
    dept = random.choice(['DEFENSE', 'HOMELAND SECURITY', 'JUSTICE', 'STATE'])
    tk.Label(hdr, text=_fmt('🇺🇸  DEPARTMENT OF {}', _(dept)),
             bg='#1a237e', fg='white', font=('Segoe UI', 13, 'bold')).pack(pady=(12, 0))
    tk.Label(hdr, text=_fmt('TOP SECRET // {} // {}', random.choice(["SI","TK","NOFORN","SCI"]), server["name"]),
             bg='#1a237e', fg='#ffeb3b', font=('Segoe UI', 8, 'bold')).pack()
    body = tk.Frame(w, bg='white', padx=25, pady=20)
    body.pack(fill=tk.BOTH, expand=True)
    tk.Label(body, text=_fmt('📁  {}', server["intel_id"]), bg='white', fg='#1a237e',
             font=('Segoe UI', 15, 'bold')).pack(anchor='w')
    tk.Label(body, text=_(server['intel_desc']), bg='white', fg='#666',
             font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 10))
    sep = tk.Frame(body, bg='#ccc', height=1)
    sep.pack(fill=tk.X)
    det = tk.Frame(body, bg='#fafafa', relief=tk.GROOVE, bd=1, padx=15, pady=10)
    det.pack(fill=tk.X, pady=10)
    tk.Label(det, text=_fmt('Classification: TOP SECRET // {}', random.choice(["HCS","SI","TK","FVEY"])),
             bg='#fafafa', fg='#c62828', font=('Segoe UI', 9, 'bold')).pack(anchor='w')
    tk.Label(det, text=_fmt('Intelligence Date: {}-{:02d}-{:02d}', random.randint(2022,2026), random.randint(1,12), random.randint(1,28)),
             bg='#fafafa', fg='#333', font=('Segoe UI', 9)).pack(anchor='w')
    tk.Label(det, text=_fmt('Source: {}', random.choice(["SIGINT","HUMINT","GEOINT","OSINT","MASINT"])),
             bg='#fafafa', fg='#333', font=('Segoe UI', 9)).pack(anchor='w')
    tk.Label(det, text=_fmt('Market Value: ${:,}', server["intel_value"]),
             bg='#fafafa', fg='#2e7d32', font=('Segoe UI', 9, 'bold')).pack(anchor='w')
    sep2 = tk.Frame(body, bg='#ccc', height=1)
    sep2.pack(fill=tk.X, pady=5)
    act = tk.Frame(body, bg='white')
    act.pack(fill=tk.X)
    already_stolen = any(ii.get('server_name') == server['name'] for ii in g.gov_intel)
    if not already_stolen:
        tk.Button(act, text=_('⬇  EXTRACT INTELLIGENCE  ⬇'),
                  command=lambda: self._steal_intel(server, w),
                  bg='#1b5e20', fg='white', font=('Segoe UI', 11, 'bold'),
                  relief=tk.RAISED, bd=2, padx=15, pady=6, cursor='hand2').pack(pady=10)
    else:
        tk.Label(act, text=_('✓  Intel already extracted.'), bg='white', fg='#2e7d32',
                 font=('Segoe UI', 11, 'bold')).pack(pady=10)
    tk.Label(act, text=_('CLOSE to return to terminal'), bg='white', fg='#999',
             font=('Segoe UI', 8)).pack()
    tk.Button(w, text=_('CLOSE PORT'), command=w.destroy,
              bg='#c62828', fg='white', font=('Segoe UI', 9, 'bold'),
              relief=tk.RAISED, bd=2, padx=20).pack(pady=(0, 8))


def _steal_intel(self, server, window):
    if any(ii.get('server_name') == server['name'] for ii in g.gov_intel):
        self.console_out(_('Intel already extracted from this server.'), 'yellow')
        return
    g.gov_intel.append({
        'server_name': server['name'],
        'name': server['intel_id'],
        'desc': server['intel_desc'],
        'value': server['intel_value'],
    })
    server['intel_stolen'] = True
    g.stats['intel_stolen'] = g.stats.get('intel_stolen', 0) + 1
    self.console_out(_fmt('[+] INTELLIGENCE EXTRACTED: {} (value ${:,})', server["intel_id"], server["intel_value"]), 'green')
    self.console_out(_('    Sell on black market with SELLINTEL <id>'), 'yellow')
    self._sound_success()
    g.add_news('Intel {i} stolen from {h}!', i=server['intel_id'], h=server['name'])
    if g.add_trace(15):
        self.console_out(_('TRACED!'), 'red')
    self._screen_shake(400, 4)
    self.refresh_all()
    window.destroy()


# ═══════════════════════════════════════════════════════════════════════════════
# Hardware Upgrade
# ═══════════════════════════════════════════════════════════════════════════════

def show_upgrade(self):
    w = tk.Toplevel(self.root)
    w.title(_('🔧 Hardware Upgrade'))
    w.geometry('550x420+400+200')
    w.configure(bg=Colors.black)
    w.resizable(False, False)
    tk.Label(w, text=_('╔══ UPGRADE HARDWARE ══╗'), bg=Colors.black,
             fg=Colors.cyan, font=('Consolas', 14, 'bold')).pack(pady=(15, 10))

    for h in HARDWARE:
        name, htype, desc, base, mult, maxl = h
        f = tk.Frame(w, bg=Colors.bg, relief=tk.RIDGE, bd=1,
                     highlightbackground=Colors.border, highlightthickness=1)
        f.pack(fill=tk.X, padx=25, pady=4)
        lvl = g.hw_lvl(htype)
        cost = int(base * mult ** lvl) if lvl < maxl else 0
        info = f'{_(name):<20}'
        tk.Label(f, text=info, bg=Colors.bg, fg=Colors.cyan,
                 font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=10)
        tk.Label(f, text=_fmt('LVL {}/{}', lvl, maxl), bg=Colors.bg,
                 fg=Theme.GREEN if lvl >= maxl else Theme.AMBER,
                 font=('Consolas', 10)).pack(side=tk.LEFT)
        if lvl < maxl:
            tk.Label(f, text=f'${cost:,}', bg=Colors.bg, fg=Theme.AMBER,
                     font=('Consolas', 10, 'bold')).pack(side=tk.RIGHT, padx=5)
            btn = tk.Button(f, text=_('⬆ UP'), command=lambda t=htype, c=cost: self._do_upgrade(t, c, w),
                            bg=Colors.dark, fg=Colors.cyan, activebackground=Theme.BG_HEADER,
                            activeforeground=Theme.TEXT, font=('Consolas', 9, 'bold'),
                            relief=tk.RAISED, bd=2, padx=12, pady=2, cursor='hand2')
            btn.pack(side=tk.RIGHT, padx=5)
            if g.money < cost:
                btn.config(state=tk.DISABLED, fg=Colors.dim)
        else:
            tk.Label(f, text=_('MAX ✓'), bg=Colors.bg, fg=Theme.GREEN,
                     font=('Consolas', 10, 'bold')).pack(side=tk.RIGHT, padx=10)
        tk.Label(w, text=_(desc), bg=Colors.black, fg=Colors.dim,
                 font=('Consolas', 8)).pack(anchor='w', padx=35)
    tk.Button(w, text=_('Close'), command=w.destroy, bg=Colors.dark,
              fg=Colors.cyan, font=('Consolas', 10), cursor='hand2').pack(pady=12)


def _do_upgrade(self, t, c, w):
    if g.money < c:
        return
    g.money -= c
    g.hardware[t] = g.hw_lvl(t) + 1
    g.add_log(_fmt('Upgrade: {} -> LVL {}', t, g.hardware[t]), 'ok')
    self.console_out(_fmt('[+] {} upgraded to LVL {}!', t, g.hardware[t]), 'green')
    w.destroy()
    self.show_upgrade()
    self.refresh_all()


# ═══════════════════════════════════════════════════════════════════════════════
# Black Market
# ═══════════════════════════════════════════════════════════════════════════════

def h_market(self, a, r):
    if not g.black_market_items:
        g.gen_black_market()
    w = tk.Toplevel(self.root)
    w.title(_('🕶 Black Market'))
    w.geometry('560x500+400+150')
    w.configure(bg=Colors.black)
    w.resizable(False, False)
    tk.Label(w, text=_('╔══ BLACK MARKET ══╗'), bg=Colors.black,
             fg=Colors.pink, font=('Consolas', 13, 'bold')).pack(pady=(10, 5))
    tk.Label(w, text=_fmt('💰 ${:,}', g.money), bg=Colors.black,
             fg=Colors.yellow, font=('Consolas', 11)).pack()
    n = ttk.Notebook(w)
    n.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Buy tab
    buyf = tk.Frame(n, bg=Colors.bg)
    n.add(buyf, text=_('  BUY  '))
    f = tk.Frame(buyf, bg=Colors.bg)
    f.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    for i, item in enumerate(g.black_market_items):
        fi = tk.Frame(f, bg=Colors.dark, relief=tk.RIDGE, bd=1,
                      highlightbackground=Colors.pink, highlightthickness=1)
        fi.pack(fill=tk.X, pady=3)
        tk.Label(fi, text=_(item['name']), bg=Colors.dark, fg=Colors.cyan,
                 font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=8)
        tk.Label(fi, text=f'${item["cost"]:,}', bg=Colors.dark, fg=Colors.yellow,
                 font=('Consolas', 10)).pack(side=tk.RIGHT, padx=5)
        btn = tk.Button(fi, text=_('BUY'), command=lambda it=item: self._buy_market(it, w),
                        bg=Colors.dark, fg=Colors.pink, activebackground='#660033',
                        font=('Consolas', 9, 'bold'), relief=tk.RAISED, bd=1, padx=8)
        btn.pack(side=tk.RIGHT, padx=3)
        if g.money < item['cost']:
            btn.config(state=tk.DISABLED, fg=Colors.dim)
        tk.Label(f, text=_(item['desc']), bg=Colors.bg, fg=Colors.dim,
                 font=('Consolas', 8)).pack(anchor='w', padx=10)

    # Sell tab (intel)
    sellf = tk.Frame(n, bg=Colors.bg)
    n.add(sellf, text=_('  SELL  '))
    sf = tk.Frame(sellf, bg=Colors.bg)
    sf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    if g.gov_intel:
        for i, ii in enumerate(g.gov_intel):
            sfi = tk.Frame(sf, bg=Colors.dark, relief=tk.RIDGE, bd=1,
                           highlightbackground=Colors.cyan3, highlightthickness=1)
            sfi.pack(fill=tk.X, pady=3)
            tk.Label(sfi, text=_fmt('[{}] {}', i, _(ii["name"])), bg=Colors.dark, fg=Colors.green,
                     font=('Consolas', 10, 'bold')).pack(side=tk.LEFT, padx=8)
            payout = int(ii['value'] * (0.7 + random.random() * 0.3))
            tk.Label(sfi, text=f'~${payout:,}', bg=Colors.dark, fg=Colors.yellow,
                     font=('Consolas', 10)).pack(side=tk.RIGHT, padx=5)
            tk.Button(sfi, text=_('SELL'),
                      command=lambda idx=i, ww=w: (self.h_sellintel([str(idx)], ''), ww.destroy(), self.h_market([], '')),
                      bg=Colors.dark, fg=Colors.yellow, activebackground='#443300',
                      font=('Consolas', 9, 'bold'), relief=tk.RAISED, bd=1, padx=8).pack(side=tk.RIGHT, padx=3)
    else:
        tk.Label(sf, text=_('No intelligence to sell.'), bg=Colors.bg,
                 fg=Colors.dim, font=('Consolas', 10)).pack(pady=20)
        tk.Label(sf, text=_('Hack government servers to steal intel.'),
                 bg=Colors.bg, fg=Colors.dim, font=('Consolas', 8)).pack()
    tk.Button(w, text=_('Close'), command=w.destroy, bg=Colors.dark,
              fg=Colors.cyan, font=('Consolas', 10)).pack(pady=8)


def _buy_market(self, item, w):
    if g.money < item['cost']:
        return
    g.money -= item['cost']
    if item['type'] == 'exploit':
        g.local_files.append({'name': f'zero_day_{int(time.time())}.exploit',
                              'content': '# Zero-day exploit\n# Use: EXEC <name> <host>'})
    elif item['type'] == 'fake_ip':
        g.add_log(_('Fake IP active - trace reduced'), 'ok')
    elif item['type'] == 'scanner':
        g.local_files.append({'name': f'scanner_{int(time.time())}.bin',
                              'content': '# Advanced scanner'})
    elif item['type'] == 'decrypt_tool':
        g.local_files.append({'name': f'decrypt_{int(time.time())}.bin',
                              'content': '# Decrypt tool\n# Use for instant decryption'})
    elif item['type'] == 'worm':
        g.local_files.append({'name': f'worm_{int(time.time())}.worm',
                              'content': '# Auto-spreading worm\n# Run on a server for automatic hack'})
    elif item['type'] == 'burner_phone':
        g.local_files.append({'name': f'gsm_burner_{int(time.time())}.bin',
                              'content': '# GSM Burner Phone\n# Use for anonymous action (-30% trace)'})
        g.stats['burners'] = g.stats.get('burners', 0) + 1
        self.console_out(_('[GSM] Burner phone purchased. Use it for covert ops.'), 'yellow')
    self.console_out(_fmt('[+] Purchased: {}', item["name"]), 'green')
    self._sound_success()
    g.gen_black_market()
    w.destroy()
    self.h_market([], '')


# ═══════════════════════════════════════════════════════════════════════════════
# Skill Tree
# ═══════════════════════════════════════════════════════════════════════════════

def h_skills(self, a, r):
    w = tk.Toplevel(self.root)
    w.title(_('🧠 Skill Tree'))
    w.geometry('550x450+400+200')
    w.configure(bg=Colors.black)
    w.resizable(False, False)
    tk.Label(w, text=_('╔══ SKILL TREE ══╗'), bg=Colors.black,
             fg=Colors.cyan, font=('Consolas', 13, 'bold')).pack(pady=(10, 5))
    tk.Label(w, text=_fmt('Available points: {}', g.skill_points), bg=Colors.black,
             fg=Colors.yellow, font=('Consolas', 11)).pack()
    for sk, desc in [('stealth', _('-10% trace per action per level')),
                     ('brute', _('+20% crack speed per level')),
                     ('phish', _('Unlock phishing attack')),
                     ('crypto_bonus', _('+30% crypto profit per level')),
                     ('trace_reduce', _('-5% trace taken per level'))]:
        lvl = g.skills.get(sk, 0)
        cost = g.skill_cost(sk)
        fi = tk.Frame(w, bg=Colors.dark, relief=tk.RIDGE, bd=1,
                      highlightbackground=Colors.border, highlightthickness=1)
        fi.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(fi, text=sk.upper(), bg=Colors.dark, fg=Colors.cyan,
                 font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=8)
        tk.Label(fi, text=_fmt('LVL {}', lvl), bg=Colors.dark, fg=Colors.green,
                 font=('Consolas', 10)).pack(side=tk.LEFT, padx=5)
        tk.Label(fi, text=desc, bg=Colors.dark, fg=Colors.dim,
                 font=('Consolas', 8)).pack(side=tk.LEFT, padx=5)
        if cost is not None and g.skill_points >= cost:
            btn = tk.Button(fi, text=f'⬆ {cost}pt', command=lambda s=sk, c=cost, ww=w: self._buy_skill(s, c, ww),
                            bg=Colors.dark, fg=Colors.cyan, font=('Consolas', 9, 'bold'),
                            relief=tk.RAISED, bd=1, padx=6)
            btn.pack(side=tk.RIGHT, padx=5)
        elif cost is None:
            tk.Label(fi, text=_('MAX ✓'), bg=Colors.dark, fg=Colors.green,
                     font=('Consolas', 9)).pack(side=tk.RIGHT, padx=5)
        else:
            tk.Label(fi, text=f'{cost}pt', bg=Colors.dark, fg=Colors.dim,
                     font=('Consolas', 9)).pack(side=tk.RIGHT, padx=5)
    tk.Button(w, text=_('Close'), command=w.destroy, bg=Colors.dark,
              fg=Colors.cyan, font=('Consolas', 10)).pack(pady=8)


def _buy_skill(self, s, c, w):
    if g.skill_points < c:
        return
    g.skill_points -= c
    g.skills[s] = g.skills.get(s, 0) + 1
    self.console_out(_fmt('[+] Skill {} upgraded!', s.upper()), 'green')
    self._sound_success()
    w.destroy()
    self.h_skills([], '')


# ═══════════════════════════════════════════════════════════════════════════════
# Switch (Narrative Endgame)
# ═══════════════════════════════════════════════════════════════════════════════

def h_switch(self, a, r):
    if g.story_active < len(STORY_MISSIONS):
        self.console_out(_('You must complete all legend missions first.'), 'red')
        self.console_out(_fmt('Completed: {}/{}', sum(1 for v in g.story_progress.values() if v), len(STORY_MISSIONS)), 'yellow')
        return
    if g.narrative_switch_used:
        self.console_out(_('You already made a choice.'), 'yellow')
        return
    w = tk.Toplevel(self.root)
    w.title(_('NEXUS Core — Switch'))
    sw = self.root.winfo_screenwidth()
    sh = self.root.winfo_screenheight()
    w.geometry(f'{int(sw * 0.5)}x{int(sh * 0.5)}+{int(sw * 0.25)}+{int(sh * 0.25)}')
    w.configure(bg='#000000')
    tk.Label(w, text=_('╔══ NEXUS CORE MAINFRAME ══╗'), bg='#000',
             fg='#0ff', font=('Consolas', 14, 'bold')).pack(pady=15)
    tk.Label(w, text=_('OVERWATCH — GLOBAL SURVEILLANCE SYSTEM'), bg='#000',
             fg='#f44', font=('Consolas', 10, 'bold')).pack()
    tk.Label(w, text='', bg='#000').pack()
    frame = tk.Frame(w, bg='#000')
    frame.pack(fill=tk.BOTH, expand=True, padx=30)
    txt = tk.Text(frame, bg='#0a0a0a', fg='#aaa', font=('Consolas', 10),
                  relief=tk.FLAT, wrap=tk.WORD)
    txt.pack(fill=tk.BOTH, expand=True)
    txt.insert(tk.END, '\n'.join([
        '  === DATABASE NEXUS CORPORATION ===',
        '',
        '  Illegal Transactions:          12,847',
        '  Governments Involved:          34',
        '  People Under Surveillance:     2.4 billion',
        '  Covered-up Murders:            7',
        '  Manipulated Elections:         12',
        '  NSA Contracts:                 8',
        '  Value of Stolen Data:          $4.2 trillion',
        '',
        '  ─────────────────────────────────────────────',
        '',
        _('  YOU HAVE ACCESS TO THE MAIN SWITCH.'),
        _('  ONE CHOICE. NO TURNING BACK.'),
        '',
    ]))
    txt.config(state=tk.DISABLED)
    btnf = tk.Frame(frame, bg='#000')
    btnf.pack(pady=20)
    tk.Button(btnf, text=_('🔓  RELEASE EVERYTHING TO THE PUBLIC'), font=('Consolas', 12, 'bold'),
              bg='#0a0', fg='#fff', padx=20, pady=10, cursor='hand2',
              command=lambda: self._do_switch('public', w)).pack(side=tk.LEFT, padx=10)
    tk.Button(btnf, text=_('🔒  DELETE EVERYTHING FOREVER'), font=('Consolas', 12, 'bold'),
              bg='#a00', fg='#fff', padx=20, pady=10, cursor='hand2',
              command=lambda: self._do_switch('private', w)).pack(side=tk.LEFT, padx=10)


def _do_switch(self, choice, w):
    g.narrative_switch_used = True
    w.destroy()
    if choice == 'public':
        self.console_out('')
        self.console_type('═══════════════════════════════════════════════════════════════', 'red', 10)
        self.console_type(_('  NEXUS CORPORATION DATABASE MADE PUBLIC'), 'red', 10)
        self.console_type(_('  2.4 billion profiles. 12,847 illegal transactions.'), 'red', 10)
        self.console_type(_('  34 governments. 7 murders. 12 manipulated elections.'), 'red', 10)
        self.console_type(_('  EVERYTHING ONLINE. EVERYTHING VISIBLE. FOREVER.'), 'red', 10)
        self.console_type('═══════════════════════════════════════════════════════════════', 'red', 10)
        g.money += 100000
        g.score += 500000
        self.notify(_('🔓 DATABASE PUBLISHED! +$100,000'), 'red')
    else:
        self.console_out('')
        self.console_type('═══════════════════════════════════════════════════════════════', 'dim', 10)
        self.console_type(_('  NEXUS CORPORATION DATABASE DELETED'), 'dim', 10)
        self.console_type(_('  Every trace. Every proof. Every name.'), 'dim', 10)
        self.console_type(_('  The truth buried with Darius. Forever.'), 'dim', 10)
        self.console_type(_('  No one will ever know what happened.'), 'dim', 10)
        self.console_type('═══════════════════════════════════════════════════════════════', 'dim', 10)
        g.money += 25000
        g.score += 100000
        self.notify(_('🔒 DATABASE DESTROYED. The truth is silent.'), 'dim')
    g.add_log(_fmt('Narrative ending: {}', choice), 'ok')
    self.refresh_all()


# ═══════════════════════════════════════════════════════════════════════════════
# 3D Server View
# ═══════════════════════════════════════════════════════════════════════════════

def h_view(self, a, r):
    if not self._connected():
        return
    s = g.current_server
    w = tk.Toplevel(self.root)
    w.title(_fmt('3D View — {}', s["name"]))
    w.geometry('350x350+500+200')
    w.configure(bg=Colors.black)
    w.resizable(False, False)
    cv = tk.Canvas(w, bg=Colors.darker, highlightthickness=0, width=300, height=300)
    cv.pack(pady=10)
    self._cube_angle = 0

    def draw_cube():
        if not w.winfo_exists():
            return
        cv.delete('all')
        a = self._cube_angle
        s_ = 70
        cx, cy = 150, 150
        pts = [(math.cos(a + i * 2.094) * s_, math.sin(a + i * 2.094) * s_) for i in range(8)]
        for i in range(8):
            for j in range(i + 1, 8):
                d = ((pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2) ** 0.5
                if 80 < d < 120:
                    b = 0.3 + 0.7 * (1 - d / 120)
                    col = f'#{int(100 * b):02x}{int(200 * b):02x}{int(255 * b):02x}'
                    cv.create_line(cx + pts[i][0], cy + pts[i][1], cx + pts[j][0], cy + pts[j][1], fill=col, width=2)
        for p in pts:
            cv.create_oval(cx + p[0] - 4, cy + p[1] - 4, cx + p[0] + 4, cy + p[1] + 4, fill=Colors.cyan, outline='')
        self._cube_angle += 0.05
        w.after(50, draw_cube)

    draw_cube()
    tk.Label(w, text=s['name'], bg=Colors.black, fg=Colors.cyan,
             font=('Consolas', 9)).pack()
    tk.Label(w, text=_fmt('Connected on port {}', g.current_port), bg=Colors.black,
             fg=Colors.dim, font=('Consolas', 8)).pack()
    tk.Button(w, text=_('Close'), command=w.destroy, bg=Colors.dark,
              fg=Colors.cyan, font=('Consolas', 9)).pack(pady=5)


# ═══════════════════════════════════════════════════════════════════════════════
# Settings / Config Dialog
# ═══════════════════════════════════════════════════════════════════════════════

def show_config(self):
    w = tk.Toplevel(self.root)
    w.title(_('⚙ Settings'))
    w.geometry('420x420+450+250')
    w.configure(bg=Colors.black)
    w.resizable(False, False)

    tk.Label(w, text=_('╔══ CONFIGURATION ══╗'), bg=Colors.black,
             fg=Colors.cyan, font=('Consolas', 14, 'bold')).pack(pady=(15, 10))

    # ── Sound ──
    sf = tk.Frame(w, bg=Colors.bg, relief=tk.RIDGE, bd=1,
                  highlightbackground=Colors.border, highlightthickness=1)
    sf.pack(fill=tk.X, padx=25, pady=5)
    tk.Label(sf, text=_('🔊 Sound'), bg=Colors.bg, fg=Colors.cyan,
             font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=15, pady=8)

    self._sound_var = tk.BooleanVar(value=self._sound)
    sound_btn = tk.Button(sf, text='',
                          bg=Colors.dark, font=('Consolas', 10, 'bold'),
                          relief=tk.RAISED, bd=2, padx=15, pady=2, cursor='hand2')

    def toggle_sound():
        self._sound = not self._sound
        self._sound_var.set(self._sound)
        sound_btn.config(text=_('ON') if self._sound else _('OFF'),
                         fg=Colors.green if self._sound else Colors.red,
                         bg='#003322' if self._sound else '#330000')

    sound_btn.config(text=_('ON') if self._sound else _('OFF'),
                     fg=Colors.green if self._sound else Colors.red,
                     bg='#003322' if self._sound else '#330000',
                     command=toggle_sound)
    sound_btn.pack(side=tk.RIGHT, padx=15, pady=8)

    # ── Trace Alarm ──
    tf = tk.Frame(w, bg=Colors.bg, relief=tk.RIDGE, bd=1,
                  highlightbackground=Colors.border, highlightthickness=1)
    tf.pack(fill=tk.X, padx=25, pady=5)
    tk.Label(tf, text=_('🔔 Trace Alarm'), bg=Colors.bg, fg=Colors.cyan,
             font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=15, pady=8)

    self._alarm_var = tk.BooleanVar(value=not getattr(self, '_trace_alarm_off', False))
    alarm_btn = tk.Button(tf, text='',
                          bg=Colors.dark, font=('Consolas', 10, 'bold'),
                          relief=tk.RAISED, bd=2, padx=15, pady=2, cursor='hand2')

    def toggle_alarm():
        self._trace_alarm_on = not self._trace_alarm_on
        self._alarm_var.set(self._trace_alarm_on)
        alarm_btn.config(text=_('ON') if self._trace_alarm_on else _('OFF'),
                         fg=Colors.green if self._trace_alarm_on else Colors.red,
                         bg='#003322' if self._trace_alarm_on else '#330000')

    # init state
    if not hasattr(self, '_trace_alarm_on'):
        self._trace_alarm_on = True
    alarm_btn.config(text=_('ON') if self._trace_alarm_on else _('OFF'),
                     fg=Colors.green if self._trace_alarm_on else Colors.red,
                     bg='#003322' if self._trace_alarm_on else '#330000',
                     command=toggle_alarm)
    alarm_btn.pack(side=tk.RIGHT, padx=15, pady=8)

    # ── Language ──
    lf = tk.Frame(w, bg=Colors.bg, relief=tk.RIDGE, bd=1,
                  highlightbackground=Colors.border, highlightthickness=1)
    lf.pack(fill=tk.X, padx=25, pady=5)
    tk.Label(lf, text=_('🌐 Language'), bg=Colors.bg, fg=Colors.cyan,
             font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=15, pady=8)

    _langs = LANGUAGES()
    lang_var = tk.StringVar(value=_langs.get(get_lang(), get_lang()))
    lang_names = [_langs[code] for code in _langs]
    lang_codes = list(_langs.keys())

    def on_lang_change(*_):
        new_lang = lang_var.get()
        code = lang_codes[lang_names.index(new_lang)]
        set_lang(code)
        w.destroy()
        self.console_out(_fmt('Language set to {}. Restarting...', new_lang), 'green')
        self.root.after(500, self.restart)

    lang_menu = tk.OptionMenu(lf, lang_var, *lang_names, command=on_lang_change)
    lang_menu.config(bg=Colors.dark, fg=Colors.cyan, font=('Consolas', 10),
                     activebackground='#1a3a6a', activeforeground=Colors.white,
                     relief=tk.RAISED, bd=1, padx=10, cursor='hand2')
    lang_menu['menu'].config(bg=Colors.dark, fg=Colors.cyan, font=('Consolas', 10))
    lang_menu.pack(side=tk.RIGHT, padx=15, pady=8)

    # ── Description ──
    desc = tk.Frame(w, bg=Colors.black)
    desc.pack(fill=tk.X, padx=25, pady=(15, 5))
    tk.Label(desc, text=_('Settings are saved automatically.'),
             bg=Colors.black, fg=Colors.dim, font=('Consolas', 9)).pack(anchor='w')
    tk.Label(desc, text=_('Use SOUND command in terminal to toggle quickly.'),
             bg=Colors.black, fg=Colors.dim, font=('Consolas', 9)).pack(anchor='w')
    tk.Label(desc, text=_('Language changes require a restart.'),
             bg=Colors.black, fg=Colors.dim, font=('Consolas', 9)).pack(anchor='w')

    # ── Close button ──
    tk.Button(w, text=_('  CLOSE  '), command=w.destroy,
              bg=Colors.dark, fg=Colors.cyan, font=('Consolas', 10, 'bold'),
              relief=tk.RAISED, bd=2, padx=20, pady=4, cursor='hand2').pack(pady=(10, 15))


# ═══════════════════════════════════════════════════════════════════════════════
# Patch methods onto HackerApp
# ═══════════════════════════════════════════════════════════════════════════════

from ui.app import HackerApp

HackerApp._gov_login_portal = _gov_login_portal
HackerApp._gov_dashboard = _gov_dashboard
HackerApp._steal_intel = _steal_intel
HackerApp.show_upgrade = show_upgrade
HackerApp._do_upgrade = _do_upgrade
HackerApp.h_market = h_market
HackerApp._buy_market = _buy_market
HackerApp.h_skills = h_skills
HackerApp._buy_skill = _buy_skill
HackerApp.h_switch = h_switch
HackerApp._do_switch = _do_switch
HackerApp.h_view = h_view
HackerApp.show_config = show_config
