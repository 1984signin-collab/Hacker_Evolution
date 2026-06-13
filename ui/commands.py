#!/usr/bin/env python3
# HACKER EVOLUTION — Command handlers (Phase 2: Command System)
# These are patched onto HackerApp at import time.
# Commands are registered in the CommandRegistry for auto-generated HELP.

import random
import threading
import time
import tkinter as tk
from tkinter import messagebox

from engine.config import Colors
from engine.command_registry import CommandRegistry, CommandMeta
from engine.game import g
from data import HARDWARE, STORY_MISSIONS, DARIUS_EMAILS, EXPLOITS
from ui.rich_bridge import render_to_widget, make_table, make_panel
from ui.lang import _, _fmt

# ── Command Registry ──
_registry = CommandRegistry()


def _register(name, handler, help_text, usage='', aliases=None,
              min_level=0, admin_only=False, category='general'):
    """Shortcut to register a command in the registry."""
    _registry.register(CommandMeta(
        name=name, handler=handler, help_text=help_text,
        usage=usage, aliases=aliases or [],
        min_level=min_level, admin_only=admin_only, category=category,
    ))


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _connected(self):
    if not g.current_server:
        self.console_out(_('Not connected to a server.'), 'red')
        return False
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# h_help
# ═══════════════════════════════════════════════════════════════════════════════

def h_help(self, a, r):
    """Auto-generated HELP from the CommandRegistry (Phase 2)."""
    from rich.table import Table
    cmds = _registry.list_commands(
        player_level=g.level,
        include_admin=True,
    )
    if not cmds:
        self.console_out(_('No commands registered.'), 'red')
        return

    # Group by category
    cats = {}
    for cmd in cmds:
        cats.setdefault(cmd.category, []).append(cmd)

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column('Cmd')
    table.add_column('Desc')
    for cat in sorted(cats):
        table.add_row(f'[{cat.upper()}]', '', style='bold yellow')
        for cmd in cats[cat]:
            label = cmd.name.upper()
            if cmd.aliases:
                label += '/' + '/'.join(a.upper() for a in cmd.aliases)
            if cmd.usage:
                label += f' {cmd.usage}'
            desc = cmd.help_text[:65] if cmd.help_text else ''
            table.add_row(f'[bold cyan]{label}[/]', f'[dim]{desc}[/]')

    panel = make_panel(table, title=_('[bold yellow]AVAILABLE COMMANDS[/]'))
    self.console_rich(panel)


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 5: h_debugstate / h_validatecontent
# ═══════════════════════════════════════════════════════════════════════════════

def h_debugstate(self, a, r):
    """DEBUGSTATE — mostra lo stato interno di tutte le FSM e servizi.
    
    Utile per modder, debugging e test. Mostra stato di:
      - Sentinel FSM
      - Event Bus subscribers
      - Command Registry
      - Servizi (Economy, Network, Trace, Mission)
    """
    from rich.table import Table
    from rich.panel import Panel

    # Sentinel FSM
    sentinel = g.sentinel_svc
    s_table = Table(show_header=False, box=None, padding=(0, 1))
    s_table.add_column('Key')
    s_table.add_column('Value')
    s_table.add_row('State', f'[bold]{sentinel.state.value}[/]')
    s_table.add_row('Timer', str(sentinel._fsm.timer))
    s_table.add_row('Cooldown', str(sentinel.cooldown))
    s_table.add_row('Strikes', str(sentinel.strikes))
    s_table.add_row('Ports Closed', str(sentinel._fsm.ports_closed))
    s_panel = make_panel(s_table, title=_('[bold magenta]SENTINEL FSM[/]'))
    self.console_rich(s_panel)

    # Event Bus (subscriber count)
    bus = g._bus
    bus_table = Table(show_header=False, box=None, padding=(0, 1))
    bus_table.add_column('Key')
    bus_table.add_column('Value')
    for key, handlers in bus._subscribers.items():
        bus_table.add_row(key, f'{len(handlers)} handlers')
    bus_panel = make_panel(bus_table, title=_('[bold cyan]EVENT BUS[/]'))
    self.console_rich(bus_panel)

    # Command Registry
    reg_table = Table(show_header=False, box=None, padding=(0, 1))
    reg_table.add_column('Key')
    reg_table.add_column('Value')
    d = _registry.to_dict()
    reg_table.add_row('Commands', str(len(d.get('commands', []))))
    reg_table.add_row('Aliases', str(len(d.get('aliases', {}))))
    cats = ', '.join(c for c in _registry.categories())
    reg_table.add_row('Categories', cats)
    reg_panel = make_panel(reg_table, title=_('[bold yellow]COMMAND REGISTRY[/]'))
    self.console_rich(reg_panel)

    # Services
    svc_table = Table(show_header=False, box=None, padding=(0, 1))
    svc_table.add_column('Service')
    svc_table.add_column('Status')
    svc_table.add_row('Economy', f'${g.money:,.0f}')
    svc_table.add_row('Trace', f'{g.trace_level:.1f}%')
    svc_table.add_row('Network', f'{len(g.servers)} servers')
    svc_table.add_row('Missions', f'{len(g.missions)} active')
    svc_panel = make_panel(svc_table, title=_('[bold green]SERVICES[/]'))
    self.console_rich(svc_panel)

    # Game state summary
    game_table = Table(show_header=False, box=None, padding=(0, 1))
    game_table.add_column('Key')
    game_table.add_column('Value')
    game_table.add_row('Version', 'v1.0 Phase 5 (Hardened)')
    game_table.add_row('Level', str(g.level))
    game_table.add_row('Score', str(g.score))
    game_table.add_row('Money', f'${g.money:,.0f}')
    game_table.add_row('Server', g.current_server['name'] if g.current_server else 'None')
    game_table.add_row('Hack Count', str(g.hack_count))
    game_table.add_row('Exploits', ', '.join(g.exploits) if g.exploits else 'None')
    game_table.add_row('Trace', f'{g.trace_level:.1f}%')
    game_table.add_row('Sentinel', sentinel.state.value)
    game_panel = make_panel(game_table, title=_('[bold white]GAME STATE[/]'))
    self.console_rich(game_panel)


def h_validatecontent(self, a, r):
    """VALIDATECONTENT — esegue il ContentValidator su tutti i contenuti.
    
    Ricarica e valida tutti i JSON di data/ a runtime.
    Utile per modder che vogliono verificare i loro file modificati.
    """
    from engine.validation import ContentValidator
    from data import _load_json, _load_json_dir, _data_dir

    v = ContentValidator(silent=True)

    # Server pool
    import os
    pool_path = os.path.join(_data_dir, 'servers.json')
    try:
        pool = _load_json('servers.json')
        v.validate_server_pool(pool)
    except Exception as e:
        v.error(f'servers.json: {e}')

    # Hardware
    try:
        hw = _load_json('hardware.json')
        v.validate_hardware(hw)
    except Exception as e:
        v.error(f'hardware.json: {e}')

    # Exploits
    try:
        ex = _load_json('exploits.json')
        v.validate_exploits(ex)
    except Exception as e:
        v.error(f'exploits.json: {e}')

    # Gov intel
    try:
        gov = _load_json('gov_intel.json')
        v.validate_gov_intel(gov)
    except Exception as e:
        v.error(f'gov_intel.json: {e}')

    # Missions
    try:
        missions = _load_json_dir('missions')
        v.validate_story_missions(missions)
    except Exception as e:
        v.error(f'missions/: {e}')

    # Emails
    try:
        emails = _load_json_dir('emails')
        v.validate_emails(emails)
    except Exception as e:
        v.error(f'emails/: {e}')

    # Report
    has_errors = v.report()
    if has_errors:
        count = len(v.errors)
        self.notify(f'⚠ VALIDATION: {count} errors', 'red')
    else:
        self.notify('✅ VALIDATION: All content valid!', 'green')


# ═══════════════════════════════════════════════════════════════════════════════
# h_servers / h_money / h_ls / h_cat / h_delete
# ═══════════════════════════════════════════════════════════════════════════════

def h_servers(self, a, r):
    rows = []
    for s in g.servers:
        st = '[green]HACKED[/]' if g.hacked(s) else '[yellow]SCANNED[/]' if s['scanned'] else '[dim]UNKNOWN[/]'
        gov = '[red]GOV[/]' if s.get('is_gov') else ''
        vis = '[cyan]*[/]' if s.get('visible') else '[dim] [/]'
        name = f'[cyan]{s["name"]}[/]' if s.get('visible') else f'[dim]{s["name"]}[/]'
        rows.append([vis, st, gov, name, f'[dim]{s["desc"]}[/]'])
    table = make_table(
        title=_('[bold yellow]SERVERS ({len(g.servers)})[/]'),
        headers=[_('Net'), _('Status'), _('Type'), _('Name'), _('Description')],
        rows=rows,
    )
    self.console_rich(table)
    reachable = g.reachable_servers()
    if reachable:
        self.console_rich(
            _fmt('[dim]Reachable: {}[/]', ', '.join(s['name'] for s in reachable))
        )
    entry = g.entry_servers
    if entry:
        self.console_rich(
            _fmt('[dim]Entry points: {}[/]', ', '.join(s['name'] for s in entry))
        )


def h_money(self, a, r):
    self.console_out(_fmt('Money: ${:,}', g.money), 'yellow')


def h_ls(self, a, r):
    if self._connected():
        s = g.current_server
        self.console_out(_fmt('\n── {}:{} ──', s["name"], g.current_port), 'cyan')
        for f in s['files']:
            self.console_out(f'  {f["name"]:<35} {max(1, len(f["content"]) // 100)} blk')
    else:
        self.console_out(_fmt('── LOCAL ({}/{} blocks) ──', g.used_mem(), g.memory()), 'cyan')
        for f in g.local_files:
            self.console_out(f'  {f["name"]:<35} {max(1, len(f["content"]) // 100)} blk')


def h_cat(self, a, r):
    if not a:
        self.console_out(_('Use: CAT <file>'), 'red')
        return
    fname = a[0]
    if self._connected():
        for f in g.current_server['files']:
            if f['name'] == fname:
                self.console_out(_fmt('\n{}', f["content"]), 'white')
                return
    for f in g.local_files:
        if f['name'] == fname:
            self.console_out(_fmt('\n{}', f["content"]), 'white')
            return
    self.console_out(_fmt('File not found: {}', fname), 'red')


def h_delete(self, a, r):
    if not a:
        self.console_out(_('Use: DELETE <file>'), 'red')
        return
    fname = a[0]
    if self._connected():
        for i, f in enumerate(g.current_server['files']):
            if f['name'] == fname:
                g.current_server['files'].pop(i)
                if g.add_trace(1):
                    self.console_out(_('TRACED!'), 'red')
                self.console_out(_fmt('{} deleted.', fname), 'green')
                self.refresh_all()
                return
    for i, f in enumerate(g.local_files):
        if f['name'] == fname:
            g.local_files.pop(i)
            self.console_out(_fmt('{} deleted.', fname), 'green')
            self.refresh_all()
            return
    self.console_out(_fmt('File not found: {}', fname), 'red')


# ═══════════════════════════════════════════════════════════════════════════════
# h_scan / h_scanports
# ═══════════════════════════════════════════════════════════════════════════════

def h_scan(self, a, r):
    if not a:
        self.console_out(_('Use: SCAN <host>'), 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if s:
        s['scanned'] = True
        # Rivela i vicini nel grafo di rete
        g.reveal_neighbors(s)
        self.console_out_type(_fmt('\n[+] Server FOUND: {}', s["name"]), 'green', 12)
        self.console_out_type(_fmt('    Ports: {}', ", ".join(str(p) for p in s["ports"])), 'cyan', 12)
        self.console_out_type(_fmt('    Key: {} bits', s["key_bits"]), 'yellow', 12)
        self.console_out_type(_fmt('    Status: {}', 'ENCRYPTED' if not s['decrypted'] else 'DECRYPTED'), 'orange', 12)
        # Mostra i vicini
        neighbors = [n['name'] for n in s.get('links', [])]
        if neighbors:
            visible_n = [n for n in s.get('links', []) if n.get('visible')]
            self.console_out_type(
                _fmt('    🌐 Neighbors ({}): {}', len(visible_n), ', '.join(n['name'] for n in visible_n)),
                'cyan', 12,
            )
        # Trace rimane invariato
        if g.add_trace(1):
            self.console_out(_('TRACED!'), 'red')
        self.update_map()
    else:
        self.console_out(_fmt('[-] Host not found: {}', host), 'red')
        self._sound_error()
    self.refresh_all()


def h_scanports(self, a, r):
    if not a:
        self.console_out(_('Use: SCANPORTS <host>'), 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown host: {}', host), 'red')
        return
    s['scanned'] = True
    self.console_out(_fmt('Scanning ports on {}...', host), 'yellow')
    def run():
        for p in s['ports']:
            if not self.root.winfo_exists():
                return
            time.sleep(0.3)
            filtered = random.random() < 0.15
            self.root.after(0, lambda pp=p, f=filtered: self.console_out(
                _fmt('  Port {}: {}', pp, _('FILTERED') if f else _('OPEN')), 'orange' if f else 'green'))
        self.root.after(0, lambda: (self.update_map(), self.refresh_all()))
    threading.Thread(target=run, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════════════
# h_route — Network graph topology
# ═══════════════════════════════════════════════════════════════════════════════

def h_route(self, a, r):
    """Show the network graph: visible servers and their connections."""
    self.console_out('═' * 60, 'cyan')
    self.console_out(_('🌐 NETWORK TOPOLOGY'), 'yellow')
    self.console_out('═' * 60, 'cyan')
    visible = [s for s in g.servers if s.get('visible')]
    if not visible:
        self.console_out(_('No network map available yet. Scan an entry server first.'), 'dim')
        return
    for sv in visible:
        # Stato del server
        if g.hacked(sv):
            icon = '✓'
            color = 'green'
        elif sv.get('cracked'):
            icon = '◉'
            color = 'yellow'
        elif sv.get('scanned'):
            icon = '◌'
            color = 'orange'
        else:
            icon = '○'
            color = 'dim'
        entry = ' [ENTRY]' if sv.get('entry_point') else ''
        conn = ' [CONNECTED]' if sv is g.current_server else ''
        self.console_out(
            _fmt('  [{color}]{icon} {name}{entry}{conn}[/]'),
            color, 12,
        )
        # Vicini visibili
        vis_neighbors = [n for n in sv.get('links', []) if n.get('visible')]
        if vis_neighbors:
            self.console_out(
                _fmt('      → {}', ', '.join(n['name'] for n in vis_neighbors)),
                'cyan', 12,
            )
    self.console_out('═' * 60, 'cyan')
    self.console_out(_fmt('Visible: {}  |  Total: {}', len(visible), len(g.servers)), 'dim')
    if g.current_server:
        reachable = [n['name'] for n in g.reachable_servers()]
        self.console_out(
            _fmt('From [{}]: reachable → {}', g.current_server['name'],
                 ', '.join(reachable) if reachable else _('none')),
            'green', 12,
        )
    else:
        entry_names = ', '.join(e['name'] for e in g.entry_servers)
        self.console_out(
            _fmt('Entry points (connect first): {}', entry_names),
            'green', 12,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# h_connect / h_logout
# ═══════════════════════════════════════════════════════════════════════════════

def h_connect(self, a, r):
    if not a:
        self.console_out(_('Use: CONNECT <host> [port]'), 'red')
        return
    host = a[0].lower()
    port = int(a[1]) if len(a) > 1 else 80
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    if not s['scanned']:
        self.console_out(_fmt('Scan {} first', host), 'red')
        return
    if not s['decrypted']:
        self.console_out(_fmt('Decrypt {} first', host), 'red')
        return
    if not s['cracked'].get(port):
        self.console_out(_fmt('Crack {}:{} first', host, port), 'red')
        return
    # Verifica raggiungibilità nel grafo
    if not g.is_reachable(s):
        if g.current_server:
            reachable = [n['name'] for n in g.reachable_servers()]
            self.console_out(
                _fmt('{} is not reachable from {}. Neighbors: {}',
                     host,
                     g.current_server['name'],
                     ', '.join(reachable) if reachable else _('none (try SCAN first)')),
                'red',
            )
        else:
            entry_names = ', '.join(e['name'] for e in g.entry_servers)
            self.console_out(
                _fmt('{} is not reachable. Entry points: {}', host, entry_names),
                'red',
            )
        self._sound_error()
        return
    g.current_server = s
    g.current_port = port
    s['visited'] = True
    # Rivela i vicini quando ti connetti
    g.reveal_neighbors(s)
    self.console_out_type(_fmt('[+] Connected to {}:{}', host, port), 'green', 12)
    neighbors = [n['name'] for n in s.get('links', [])]
    if neighbors:
        self.console_out_type(_fmt('    🌐 Links: {}', ', '.join(neighbors)), 'cyan', 12)
    self._sound_connect()
    if g.add_trace(1):
        self.console_out(_('TRACED!'), 'red')
    self._update_prompt()
    self.refresh_all()
    if s.get('is_gov'):
        self.root.after(200, lambda: self._gov_login_portal(s))


def h_logout(self, a, r):
    if g.current_server:
        self.console_out_type(_fmt('Disconnected from {}', g.current_server['name']), 'yellow', 12)
        g.current_server = None
        g.current_port = None
        self._update_prompt()
        self.refresh_all()
    else:
        self.console_out(_('Not connected.'), 'red')


# ═══════════════════════════════════════════════════════════════════════════════
# h_crack / h_decrypt / h_login
# ═══════════════════════════════════════════════════════════════════════════════

def h_crack(self, a, r):
    if len(a) < 1:
        self.console_out(_('Use: CRACK <host> [port]'), 'red')
        return
    host = a[0].lower()
    port = int(a[1]) if len(a) > 1 else 80
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    if not s['scanned']:
        self.console_out(_fmt('Scan {} first', host), 'red')
        return
    if port not in s['ports']:
        self.console_out(_fmt('Port {} not found', port), 'red')
        return
    pwd_len = random.randint(8, min(32, 8 + s['key_bits'] // 16))
    self.console_out_type(f'Brute force su {host}:{port}... ({pwd_len} chars)', 'yellow', 10)
    self._progress('crack', pwd_len * 100, host, port)


def h_decrypt(self, a, r):
    if not a:
        self.console_out(_('Use: DECRYPT <host>'), 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    if not s['scanned']:
        self.console_out(_fmt('Scan {} first', host), 'red')
        return
    if s['decrypted']:
        self.console_out(_fmt('{} already decrypted.', host), 'yellow')
        return
    self.console_out_type(_fmt('Decrypting key {} bits...', s['key_bits']), 'yellow', 10)
    self._progress('decrypt', s['key_bits'], host, None)


def h_login(self, a, r):
    if len(a) < 2:
        self.console_out(_('Use: LOGIN <host> <password>'), 'red')
        return
    host = a[0].lower()
    pwd = a[1]
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    known_pwds = {'mywordismypassword': 49, 'admin123': 999, 'root!': 21, 'letmein': 25}
    if pwd in known_pwds:
        port = known_pwds[pwd]
        if port in s['ports']:
            s['cracked'][port] = True
            self.console_out_type(_fmt('[+] Access to {}:{}', host, port), 'green', 12)
            if g.add_trace(1):
                self.console_out(_('TRACED!'), 'red')
            g.check_story_missions('login')
            self.refresh_all()
            return
    self.console_out(_('Wrong password.'), 'red')


# ═══════════════════════════════════════════════════════════════════════════════
# h_download / h_upload / h_exec / h_transfer / h_abort / h_clear
# ═══════════════════════════════════════════════════════════════════════════════

def h_download(self, a, r):
    if not a:
        self.console_out(_('Use: DOWNLOAD <file>'), 'red')
        return
    if not self._connected():
        return
    fname = a[0]
    for f in g.current_server['files']:
        if f['name'] == fname:
            if g.can_download(dict(f)):
                g.local_files.append(dict(f))
                g.stats['download_count'] = g.stats.get('download_count', 0) + 1
                self.console_out_type(f'Download: {fname} ({len(g.local_files)}/{g.memory()})', 'green', 10)
                if g.add_trace(2):
                    self.console_out(_('TRACED!'), 'red')
                g.check_story_missions('download')
                # Fix: 'host' was undefined in original — use current server name
                sname = g.current_server['name'].lower()
                if 'gsm' in sname or 'tower' in sname:
                    g.check_story_missions('gsm')
            else:
                self.console_out(_('Memory full!'), 'red')
            self.refresh_all()
            return
    self.console_out(_fmt('File not found: {}', fname), 'red')


def h_upload(self, a, r):
    if not a:
        self.console_out(_('Use: UPLOAD <file>'), 'red')
        return
    if not self._connected():
        return
    fname = a[0]
    for f in g.local_files:
        if f['name'] == fname:
            g.current_server['files'].append(dict(f))
            self.console_out_type(f'Upload: {fname}', 'green', 10)
            if g.add_trace(2):
                self.console_out(_('TRACED!'), 'red')
            g.check_story_missions('upload')
            self.refresh_all()
            return
    self.console_out(_fmt('File not found locally: {}', fname), 'red')


def h_exec(self, a, r):
    if len(a) < 2:
        self.console_out(_('Use: EXEC <exploit> <host>'), 'red')
        return
    exploit = a[0]
    host = a[1].lower()
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    for f in g.local_files:
        if f['name'] == exploit and 'exploit' in exploit:
            parts = exploit.replace('.exploit', '').split('_')
            tp = int(parts[-1]) if parts[-1].isdigit() else 0
            if tp and tp in s['ports']:
                s['cracked'][tp] = True
            elif not tp:
                s['cracked'][s['ports'][0]] = True
            else:
                self.console_out(_('Invalid port.'), 'red')
                return
            g.hack_count += 1
            self.console_out_type(f'[+] Exploit {exploit} eseguito su {host}!', 'green', 12)
            self._sound_success()
            g.add_news(_('Exploit {e} deployed on {h}'), e=exploit, h=host)
            if g.add_trace(5):
                self.console_out(_('TRACED!'), 'red')
            self.refresh_all()
            return
    self.console_out(_('Exploit not found.'), 'red')


def h_transfer(self, a, r):
    if not a:
        self.console_out(_('Use: TRANSFER <amount>'), 'red')
        return
    if not self._connected():
        return
    try:
        amt = int(a[0])
    except ValueError:
        self.console_out(_('Invalid amount.'), 'red')
        return
    s = g.current_server
    if s['money'] < amt:
        self.console_out(_fmt('Server only has ${}', s["money"]), 'red')
        return
    self.console_out_type(f'Trasferimento ${amt}...', 'yellow', 10)
    self._progress('transfer', amt, None, None)


def h_abort(self, a, r):
    self.action_cancel = True
    self.console_out(_('Cancelled.'), 'yellow')


def h_clear(self, a, r):
    self.console_clear()


# ═══════════════════════════════════════════════════════════════════════════════
# h_config / h_upgrade
# ═══════════════════════════════════════════════════════════════════════════════

def h_config(self, a, r):
    rows = []
    for h in HARDWARE:
        lvl = g.hw_lvl(h[1])
        vals = {
            'firewall': f'{g.trace_mult()}x trace',
            'modem': f'{g.transfer_speed()}x',
            'cpu': f'{g.crack_speed()}x',
            'memory': f'{g.memory()} blk',
            'neural': f'{2 ** lvl}x all' if lvl else 'not owned',
        }
        bar = '█' * lvl + '░' * (h[5] - lvl)
        color = 'green' if lvl == h[5] else 'yellow' if lvl > h[5] // 2 else 'dim'
        rows.append([
            f'[{color}]{h[0]:<18}[/]',
            f'[bold cyan]LVL {lvl}/{h[5]}[/]',
            f'[dim]{bar}[/]',
            f'[dim]{vals.get(h[1], "-")}[/]',
        ])
    table = make_table(
        title=_('[bold yellow]HARDWARE CONFIG[/]'),
        headers=['Component', 'Level', 'Progress', 'Effect'],
        rows=rows,
    )
    self.console_rich(table)
    mem_label = _('Memory:')
    trace_label = _('Trace:')
    money_label = _('Money:')
    stats = f'  [bold cyan]{mem_label}[/] {g.used_mem()}/{g.memory()} blk  [bold yellow]{trace_label}[/] {g.trace_level:.1f}%  [bold green]{money_label}[/] ${g.money:,}'
    self.console_rich(stats)


def h_upgrade(self, a, r):
    self.show_upgrade()


# ═══════════════════════════════════════════════════════════════════════════════
# h_nextlevel / h_newgame
# ═══════════════════════════════════════════════════════════════════════════════

def h_nextlevel(self, a, r):
    self.console_out(_('Moving to next level...'), 'yellow')
    g.level += 1
    from engine.game import generate_servers
    g.servers = generate_servers(8 + min(g.level, 4))
    g.current_server = None
    g.current_port = None
    g.bounce_chain = []
    g.skill_points += 1
    g.gen_missions()
    g.add_news(_('Level {lvl} unlocked — new targets available'), lvl=g.level)
    g.add_log(_fmt('Level {} started!', g.level), 'ok')
    self.console_out(_fmt('═══ LEVEL {} ═══', g.level), 'green')
    self.console_out(_fmt('Generated {} missions.', len(g.missions)), 'dim')
    for e in g.narrative_unread:
        if e['lvl'] <= g.level:
            g.narrative_unread.remove(e)
            self.console_out(_fmt('📧 NEW EMAIL: {} (type EMAIL)', e["sub"]), 'yellow')
            self.notify(f'📧 {e["sub"]}', 'cyan')
            break
    for sm in STORY_MISSIONS:
        if sm['lvl'] == g.level and not g.story_progress.get(sm['id']):
            self.console_out(_fmt('📜 STORY UNLOCKED: {} (type STORY)', sm["name"]), 'yellow')
            self.notify(_fmt('📜 {} unlocked!', sm['name']), 'yellow')
    self.update_map()
    self.refresh_all()


def h_newgame_wrapper(self):
    self.h_newgame([], 'newgame')


def h_newgame(self, a, r):
    if messagebox.askyesno('Nuova Partita', 'Ricominciare? Tutti i progressi andranno persi.'):
        g.reset(first=False)
        self.console_clear()
        self.console_out(_('═══ NEW GAME ═══'), 'green')
        self.console_out(_('Type HELP for commands.'), 'dim')
        self.update_map()
        self.refresh_all()
        g.add_log(_('New game started.'), 'ok')


# ═══════════════════════════════════════════════════════════════════════════════
# h_bounce / h_bounceinfo / h_bouncehelp
# ═══════════════════════════════════════════════════════════════════════════════

def h_bounce(self, a, r):
    if not a:
        self.console_out(_('Use: BOUNCE <host>'), 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    if g.current_server:
        self.console_out(_('Disconnect first.'), 'red')
        return
    if not g.hacked(s):
        self.console_out(_fmt('{} not hacked.', host), 'red')
        return
    if s['bounce_used'] >= 3:
        self.console_out(_fmt('{} has no bounces left.', host), 'red')
        return
    if host in g.bounce_chain:
        g.bounce_chain.remove(host)
        s['bounce_used'] -= 1
        self.console_out(_fmt('{} removed from bounce.', host), 'yellow')
    else:
        g.bounce_chain.append(host)
        s['bounce_used'] += 1
        g.stats['bounces'] += 1
        self.console_out(_fmt('{} added to bounce. ({} hop)', host, len(g.bounce_chain)), 'green')
        g.check_story_missions('bounce')
    self.update_map()


def h_bounceinfo(self, a, r):
    if not g.bounce_chain:
        self.console_out(_('Empty chain.'), 'yellow')
        return
    self.console_out(_fmt('Chain ({} hop):', len(g.bounce_chain)), 'cyan')
    for i, h in enumerate(g.bounce_chain):
        self.console_out(_fmt('  {}. {}', i + 1, h), 'green')
    self.console_out(_fmt('Trace multiplier: {}x', g.trace_mult()), 'yellow')


def h_bouncehelp(self, a, r):
    self.console_out('═' * 60, 'cyan')
    self.console_out(_('BOUNCE HELP'), 'yellow')
    self.console_out('═' * 60, 'cyan')
    for l in [
        _('Bounced links increase trace time.'),
        _('Use BOUNCE <host> to add hacked servers.'),
        _('Trace time = base × (hop+1) × firewall bonus'),
        _('Max 3 bounces per server.'),
        _('You cannot modify bounce while connected.'),
    ]:
        self.console_out(_fmt('  {}', l), 'green')


# ═══════════════════════════════════════════════════════════════════════════════
# h_killtrace / h_deletelogs
# ═══════════════════════════════════════════════════════════════════════════════

def h_killtrace(self, a, r):
    if g.money < 500:
        self.console_out(_('Need $500.'), 'red')
        return
    g.money -= 500
    g.trace_level = max(0, g.trace_level - 10)
    g.trace_count += 1
    self.console_out(_fmt('Trace reduced to {:.1f}% (-$500)', g.trace_level), 'green')
    self.refresh_all()


def h_deletelogs(self, a, r):
    if not self._connected():
        return
    red = min(15, g.trace_level)
    g.trace_level = max(0, g.trace_level - red)
    self.console_out(_fmt('Logs deleted. Trace: {:.1f}%', g.trace_level), 'green')
    self.refresh_all()


# ═══════════════════════════════════════════════════════════════════════════════
# _progress (background task runner for crack/decrypt/transfer)
# ═══════════════════════════════════════════════════════════════════════════════

def _progress(self, action, total, host, port):
    if self.action_active:
        return
    self.action_active = True
    self.action_cancel = False
    self.pf.pack(fill=tk.X, pady=3)
    self.ps.config(text=f'{action}... 0%')
    self.pv.set(0)
    if not hasattr(self, '_hex_lbl'):
        self._hex_lbl = tk.Label(self.pf, text='', bg=Colors.bg,
                                 fg='#224466', font=('Consolas', 8))
        self._hex_lbl.pack()
    speed = g.crack_speed() if action in ('crack', 'decrypt') else g.transfer_speed()
    trace_p = {'crack': 15, 'decrypt': 5, 'transfer': 3}.get(action, 5)
    mult = g.trace_mult()

    def run():
        steps = max(20, min(100, total // 5))
        for i in range(steps + 1):
            if self.action_cancel:
                break
            pct = int(100 * i / steps)
            self.pv.set(pct)
            self.ps.config(text=f'{action}... {pct}%')
            hex_line = ' '.join(f'{random.randint(0, 255):02x}' for _ in range(16))
            self._hex_lbl.config(
                text=hex_line,
                fg=f'#{int(30 + 40 * i / steps):02x}{int(60 + 80 * i / steps):02x}{int(100 + 100 * i / steps):02x}',
            )
            self.root.update()
            time.sleep(max(0.03, (total / steps / 1000) / max(1, speed)))
        if self.action_cancel:
            self.action_active = False
            self.pf.pack_forget()
            return

        if action == 'crack' and host:
            s = g.server(host)
            if s and port in s['ports']:
                s['cracked'][port] = True
                g.hack_count += 1
                g.stats['hacks'] += 1
                if all(s['cracked'].get(p, False) for p in s['ports']) and s['decrypted']:
                    g.stats['servers_hacked'] += 1
                self.console_out(_fmt('[+] Password CRACKED on {}:{}!', host, port), 'green')
                self._sound_success()
                g.add_news(_('Server breached! {h}:{p} compromised.'), h=host, p=port)
                g.add_log(_fmt('Crack: {}:{}', host, port), 'ok')
                g.check_story_missions('crack')
                cx, cy = s.get('pos', (100, 100))
                self.root.after(10, lambda cx=cx, cy=cy: self._impact_wave(cx, cy))
        elif action == 'decrypt' and host:
            s = g.server(host)
            if s:
                s['decrypted'] = True
            self.console_out(_fmt('[+] Key DECRYPTED on {}!', host), 'green')
            self._sound_success()
            g.add_news(_('Key decrypted for {h}'), h=host)
            g.add_log(_fmt('Decrypt: {}', host), 'ok')
        elif action == 'transfer' and g.current_server:
            amt = total
            g.current_server['money'] -= amt
            g.money += amt
            g.score += amt // 10
            g.total_earned += amt
            g.stats['transfers'] += 1
            g.stats['money_stolen'] += amt
            g.check_story_missions('transfer')
            self.console_out(_fmt('[+] Transferred ${}', amt), 'green')
            self._sound_success()
            g.add_news(_('Funds transferred: ${a} from {h}'), a=amt, h=g.current_server['name'])
            g.add_log(_fmt('Transfer: ${}', amt), 'ok')

        if self._hex_lbl:
            self._hex_lbl.config(text='')
        if g.add_trace(trace_p / max(1, mult)):
            self.console_out(_('⚠️ TRACE 100%! GAME OVER!'), 'red')
            g.add_log(_('GAME OVER - Trace 100%'), 'fail')

        self.action_active = False
        self.pf.pack_forget()
        self.refresh_all()

    threading.Thread(target=run, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════════════
# h_sound / h_ping / h_traceroute / h_schematic
# ═══════════════════════════════════════════════════════════════════════════════

def h_sound(self, a, r):
    self._sound = not self._sound
    self.console_out(_fmt('Sound: {}', "ON" if self._sound else "OFF"), 'green' if self._sound else 'red')


def h_ping(self, a, r):
    if not a:
        self.console_out(_('Use: PING <host>'), 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    self.console_out(_fmt('PING {}...', host), 'yellow')
    def run():
        for _ in range(4):
            if not self.root.winfo_exists():
                return
            ms = random.randint(5, 120)
            ttl = random.randint(32, 255)
            time.sleep(0.4)
            self.root.after(0, lambda m=ms, t=ttl: self.console_out(
                _fmt('  Reply from {}: bytes=64 time={}ms TTL={}', host, m, t), 'green'))
        self.root.after(0, lambda: self.console_out(_('  --- statistics ---'), 'cyan'))
        self.root.after(0, lambda: self.console_out(
            _('  Packets: sent=4 received=4 lost=0'), 'green'))
    threading.Thread(target=run, daemon=True).start()


def h_traceroute(self, a, r):
    if not a:
        self.console_out(_('Use: TRACEROUTE <host>'), 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(_fmt('Unknown: {}', host), 'red')
        return
    self.console_out(_fmt('Traceroute to {}...', host), 'yellow')
    def run():
        hops = random.randint(3, 8)
        for i in range(1, hops + 1):
            if not self.root.winfo_exists():
                return
            ip = f'{random.randint(10, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}'
            ms = random.randint(1, 80)
            time.sleep(0.2)
            self.root.after(0, lambda h=i, a=ip, m=ms: self.console_out(_fmt('  {:2}  {:<15} {}ms', h, a, m), 'green'))
        self.root.after(0, lambda: self.console_out(_fmt('  {:2}  {}  *', hops + 1, host), 'cyan'))
    threading.Thread(target=run, daemon=True).start()


def h_schematic(self, a, r):
    self.console_out('═' * 60, 'cyan')
    self.console_out(_('SCHEMATIC — Network Grid'), 'yellow')
    self.console_out('═' * 60, 'cyan')
    for s in g.servers:
        st = '✓' if g.hacked(s) else '◉' if s['decrypted'] else '◌' if s['scanned'] else '○'
        ports = ' '.join(f'P{p}:{"OK" if s["cracked"].get(p) else "--"}' for p in s['ports'])
        self.console_type(f'  [{st}] {s["name"]:40} {ports}', 'green', 10)
    self.console_out('')


# ═══════════════════════════════════════════════════════════════════════════════
# Crypto commands
# ═══════════════════════════════════════════════════════════════════════════════

def h_crypto(self, a, r):
    self.console_out('═' * 60, 'cyan')
    self.console_out(_('CRYPTOCURRENCIES'), 'yellow')
    self.console_out('─' * 60, 'cyan')
    for c in g.crypto:
        val = g.crypto[c]['qty'] * g.crypto[c]['price']
        self.console_out(_fmt('  {:>4}  ${:>6,}  QTY: {:.4f}  VAL: ${:,.0f}', c.upper(), g.crypto[c]["price"], g.crypto[c]["qty"], val), 'cyan')
    total = sum(g.crypto[c]['qty'] * g.crypto[c]['price'] for c in g.crypto)
    self.console_out(_fmt('  Total crypto wallet: ${:,.0f}', total), 'yellow')
    self.console_out(_('  Use: BUYCRYPTO <coin> <amount>  |  SELLCRYPTO <coin> <amount>'), 'dim')
    self.console_out(_('  Coins: BTC, ETH, XMR'), 'dim')


def h_buycrypto(self, a, r):
    if len(a) < 2:
        self.console_out(_('Use: BUYCRYPTO <coin> <amount>'), 'red')
        return
    coin = a[0].lower()
    try:
        amt = float(a[1])
    except ValueError:
        self.console_out(_('Invalid amount.'), 'red')
        return
    if coin not in g.crypto:
        self.console_out(_('Invalid coin. BTC, ETH, XMR'), 'red')
        return
    cost = amt * g.crypto[coin]['price']
    if g.money < cost:
        self.console_out(_fmt('Need ${:,.0f}', cost), 'red')
        return
    g.money -= cost
    g.crypto[coin]['qty'] += amt
    self.console_out(_fmt('Bought {:.4f} {} for ${:,.0f}', amt, coin.upper(), cost), 'green')
    g.add_news(_('Crypto purchase: {a:.2f} {c}'), a=amt, c=coin.upper())


def h_sellcrypto(self, a, r):
    if len(a) < 2:
        self.console_out(_('Use: SELLCRYPTO <coin> <amount>'), 'red')
        return
    coin = a[0].lower()
    try:
        amt = float(a[1])
    except ValueError:
        self.console_out(_('Invalid amount.'), 'red')
        return
    if coin not in g.crypto:
        self.console_out(_('Invalid coin. BTC, ETH, XMR'), 'red')
        return
    if g.crypto[coin]['qty'] < amt:
        self.console_out(_fmt('You only have {:.4f} {}', g.crypto[coin]["qty"], coin.upper()), 'red')
        return
    g.crypto[coin]['qty'] -= amt
    gain = amt * g.crypto[coin]['price']
    g.money += int(gain)
    g.total_earned += int(gain)
    self.console_out(_fmt('Sold {:.4f} {} for ${:,}', amt, coin.upper(), int(gain)), 'green')


# ═══════════════════════════════════════════════════════════════════════════════
# h_combine (virus factory)
# ═══════════════════════════════════════════════════════════════════════════════

def h_combine(self, a, r):
    if len(a) < 2:
        self.console_out(_('Use: COMBINE <file1> <file2>'), 'red')
        return
    f1 = next((f for f in g.local_files if f['name'] == a[0]), None)
    f2 = next((f for f in g.local_files if f['name'] == a[1]), None)
    if not f1 or not f2:
        self.console_out(_('File not found.'), 'red')
        return
    pairs = [
        ('exploit', 'bin', 'worm'),
        ('bin', 'exploit', 'worm'),
        ('exploit', 'exploit', 'mega_exploit'),
        ('bin', 'bin', 'payload'),
    ]
    for p in pairs:
        if (p[0] in f1['name'] and p[1] in f2['name']) or (p[1] in f1['name'] and p[0] in f2['name']):
            new_name = f'combined_{p[2]}_{int(time.time())}.{p[2]}'
            new_content = f'# {p[2]} created from {f1["name"]} + {f2["name"]}\n# Combined tool: {p[2].upper()}'
            if g.used_mem() + 1 > g.memory():
                self.console_out(_('Memory full!'), 'red')
                return
            g.local_files.append({'name': new_name, 'content': new_content})
            if f1 in g.local_files:
                g.local_files.remove(f1)
            if f2 in g.local_files:
                g.local_files.remove(f2)
            self.console_out(_fmt('[+] Created {} from {} + {}!', new_name, f1["name"], f2["name"]), 'green')
            g.check_story_missions('combine')
            self._sound_success()
            self.refresh_all()
            return
    self.console_out(_('No valid combination. Try exploit + bin.'), 'red')


# ═══════════════════════════════════════════════════════════════════════════════
# h_story / h_intel / h_sellintel
# ═══════════════════════════════════════════════════════════════════════════════

def h_story(self, a, r):
    rows = []
    for i, sm in enumerate(STORY_MISSIONS):
        done = g.story_progress.get(sm['id'], False)
        unlocked = g.level >= sm['lvl']
        current = i == g.story_active
        if done:
            icon = '✅'
            color = 'green'
            status = _fmt('[green]{}[/]', _('COMPLETED'))
        elif current:
            icon = '▶'
            color = 'yellow'
            status = _fmt('[bold yellow]{}[/]', _('ACTIVE'))
        elif unlocked:
            icon = '○'
            color = 'dim'
            status = _fmt('[dim]{}[/]', _('AVAILABLE'))
        else:
            icon = '🔒'
            color = 'dim'
            status = _fmt('[dim]{}[/]', _('LOCKED'))
        name = f'[{color}]{icon} [{sm["lvl"]}] {sm["name"]}[/]'
        desc = f'[dim]{sm["desc"][:65]}[/]'
        reward = f'[yellow]${sm["reward"]:,}[/]'
        rows.append([name, desc, status, reward])
        if current:
            rows.append([f'[yellow]   🎯 {sm["obj"]}[/]', '', '', ''])
    table = make_table(
        title=_('[bold yellow]HACKER LEGEND MISSIONS[/]'),
        headers=[_('Mission'), _('Description'), _('Status'), _('Reward')],
        rows=rows,
    )
    self.console_rich(table)
    complete = sum(1 for v in g.story_progress.values() if v)
    self.console_rich(_fmt('[bold green]Completed:[/] {}/{}', complete, len(STORY_MISSIONS)))


def h_intel(self, a, r):
    if not g.gov_intel:
        self.console_out(_('No stolen intelligence.'), 'dim')
        return
    self.console_out('═' * 40, 'cyan')
    self.console_out(_('📁 STOLEN INTELLIGENCE'), 'yellow')
    self.console_out('═' * 40, 'cyan')
    for i, ii in enumerate(g.gov_intel):
        self.console_out(_fmt('  [{}] {} — ${:,}', i, ii["name"], ii["value"]), 'green')
        self.console_out(_fmt('       {}', ii["desc"]), 'dim')
    self.console_out(_('Use SELLINTEL <id> to sell on the black market.'), 'yellow')


def h_sellintel(self, a, r):
    if not a:
        self.console_out(_('Use: SELLINTEL <id>  (see INTEL for list)'), 'red')
        return
    try:
        idx = int(a[0])
    except ValueError:
        self.console_out(_('Invalid ID.'), 'red')
        return
    if idx < 0 or idx >= len(g.gov_intel):
        self.console_out(_fmt('ID {} not found. Use INTEL for list.', idx), 'red')
        return
    ii = g.gov_intel.pop(idx)
    payout = int(ii['value'] * (0.7 + random.random() * 0.3))
    g.money += payout
    g.score += payout // 10
    g.total_earned += payout
    self.console_out(_fmt('[+] Intelligence sold: {} for ${:,}', ii["name"], payout), 'green')
    g.check_story_missions('sell_intel')
    self._sound_success()
    g.add_news(_('Intel {i} sold on black market (+${p})'), i=ii['name'], p=payout)
    self.refresh_all()


# ═══════════════════════════════════════════════════════════════════════════════
# h_alias / h_unalias
# ═══════════════════════════════════════════════════════════════════════════════

def h_alias(self, a, r):
    if len(a) < 2:
        if g.aliases:
            self.console_out(_('Active aliases:'), 'yellow')
            for al in g.aliases:
                self.console_out(_fmt('  {} → {}', al, g.aliases[al]), 'cyan')
        else:
            self.console_out(_('No aliases.'), 'dim')
        return
    g.aliases[a[0]] = ' '.join(a[1:])
    self.console_out(_fmt('Alias: {} → {}', a[0], " ".join(a[1:])), 'green')


def h_unalias(self, a, r):
    if not a:
        self.console_out(_('Use: UNALIAS <name>'), 'red')
        return
    if a[0] in g.aliases:
        del g.aliases[a[0]]
        self.console_out(_fmt('Alias {} removed.', a[0]), 'yellow')


# ═══════════════════════════════════════════════════════════════════════════════
# h_stats
# ═══════════════════════════════════════════════════════════════════════════════

def h_stats(self, a, r):
    self.console_out('═' * 60, 'cyan')
    self.console_out(_('DETAILED STATISTICS'), 'yellow')
    self.console_out('─' * 60, 'cyan')
    s = g.stats
    hacked = sum(1 for sv in g.servers if g.hacked(sv))
    self.console_out(_fmt('  Hacked servers:     {}/{}', hacked, len(g.servers)), 'green')
    self.console_out(_fmt('  Hack attempts:    {}', s["hacks"]), 'cyan')
    self.console_out(_fmt('  Transfers:        {}', s["transfers"]), 'yellow')
    self.console_out(_fmt('  Money stolen:         ${:,}', s["money_stolen"]), 'white')
    self.console_out(_fmt('  Bounces used:         {}', s["bounces"]), 'pink')
    self.console_out(_fmt('  Missions completed:  {}', s["missions_done"]), 'green')
    self.console_out(_fmt('  Max trace:        {:.1f}%', g.max_trace),
                     'red' if g.max_trace > 80 else 'yellow')
    self.console_out(_fmt('  Level:              {}', g.level), 'cyan')
    self.console_out(_fmt('  Total money:         ${:,}', g.money), 'yellow')
    self.console_out(_fmt('  Score:                {:,}', g.score), 'green')
    self.console_out(_('  Play time:          --'), 'dim')
    self.console_out('─' * 60, 'cyan')


# ═══════════════════════════════════════════════════════════════════════════════
# h_email
# ═══════════════════════════════════════════════════════════════════════════════

def h_email(self, a, r):
    emails = [e for e in DARIUS_EMAILS if e['lvl'] <= g.level]
    if not emails:
        self.console_out(_('No emails from Darius.'), 'dim')
        return
    self.console_out('═' * 60, 'cyan')
    self.console_out(_('📧 EMAIL — Darius'), 'yellow')
    self.console_out('═' * 60, 'cyan')
    for e in emails:
        self.console_out(_fmt('  Subject: {}', e["sub"]), 'cyan')
        self.console_out(_fmt('  (Level {})', e["lvl"]), 'dim')
        self.console_out('─' * 40, 'dim')
        for line in e['body'].split('\n'):
            self.console_out(_fmt('  {}', line), 'white')
        self.console_out('')


# ═══════════════════════════════════════════════════════════════════════════════
# h_darknet — Darknet exploit shop
# ═══════════════════════════════════════════════════════════════════════════════

def h_darknet(self, a, r):
    """Open the Darknet shop to buy named exploits and tools."""
    w = tk.Toplevel(self.root)
    w.title(_('🕶 Darknet — Exploit Shop'))
    w.geometry('650x520+380+150')
    w.configure(bg=Colors.black)
    w.resizable(False, False)

    header = tk.Frame(w, bg=Colors.dark)
    header.pack(fill=tk.X)
    tk.Label(header, text=_('╔══ DARKNET EXPLOITS ══╗'), bg=Colors.dark,
             fg=Colors.pink, font=('Consolas', 14, 'bold')).pack(pady=(10, 2))
    tk.Label(header, text=_fmt('💰 ${:,}   |   Owned: {} exploits', g.money, len(g.exploits)),
             bg=Colors.dark, fg=Colors.yellow, font=('Consolas', 11)).pack(pady=(0, 8))

    canvas = tk.Canvas(w, bg=Colors.bg, highlightthickness=0)
    scrollbar = tk.Scrollbar(w, orient=tk.VERTICAL, command=canvas.yview,
                             bg=Colors.dark, troughcolor=Colors.black)
    scroll_frame = tk.Frame(canvas, bg=Colors.bg)

    scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    # Populate exploit list
    for ex in EXPLOITS:
        owned = ex['id'] in g.exploits
        affordable = g.money >= ex['cost']
        level_ok = g.level >= ex.get('level', 1)

        frame = tk.Frame(scroll_frame, bg=Colors.dark, relief=tk.RIDGE, bd=1,
                         highlightbackground=Colors.pink if not owned else Colors.green,
                         highlightthickness=1)
        frame.pack(fill=tk.X, padx=10, pady=3)

        # Name + level requirement
        name_color = Colors.dim if owned else Colors.cyan
        tk.Label(frame, text=ex['name'], bg=Colors.dark, fg=name_color,
                 font=('Consolas', 11, 'bold')).pack(side=tk.LEFT, padx=8, pady=4)

        # Level badge
        lvl_tag = f'LVL {ex["level"]}'
        lvl_color = Colors.green if level_ok else Colors.red
        tk.Label(frame, text=lvl_tag, bg=Colors.dark, fg=lvl_color,
                 font=('Consolas', 8)).pack(side=tk.LEFT, padx=4)

        # Price or OWNED
        if owned:
            tk.Label(frame, text=_('OWNED ✓'), bg=Colors.dark, fg=Colors.green,
                     font=('Consolas', 10, 'bold')).pack(side=tk.RIGHT, padx=8)
        else:
            tk.Label(frame, text=f'${ex["cost"]:,}', bg=Colors.dark, fg=Colors.yellow,
                     font=('Consolas', 10, 'bold')).pack(side=tk.RIGHT, padx=5)

            buy_btn = tk.Button(frame, text=_('BUY'),
                                bg=Colors.dark, fg=Colors.pink,
                                activebackground='#660033',
                                font=('Consolas', 9, 'bold'),
                                relief=tk.RAISED, bd=1, padx=8)
            buy_btn.pack(side=tk.RIGHT, padx=3)

            if affordable and level_ok:
                buy_btn.config(command=lambda eid=ex['id']: self._buy_darknet(eid, w))
            else:
                reason = _('Need LVL {}') if not level_ok else _('Need ${}')
                buy_btn.config(state=tk.DISABLED, fg=Colors.dim,
                               text=reason.format(ex['level'] if not level_ok else ex['cost']))

        # Description
        tk.Label(scroll_frame, text=_(ex['desc']), bg=Colors.bg, fg=Colors.dim,
                 font=('Consolas', 8)).pack(anchor='w', padx=18)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    btn_frame = tk.Frame(w, bg=Colors.black)
    btn_frame.pack(fill=tk.X, pady=5)
    tk.Button(btn_frame, text=_('🔄 Refresh'), command=lambda: (w.destroy(), self.h_darknet([], '')),
              bg=Colors.dark, fg=Colors.cyan, font=('Consolas', 9),
              relief=tk.RAISED, bd=1, padx=10, cursor='hand2').pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text=_('Close'), command=w.destroy,
              bg=Colors.dark, fg=Colors.cyan, font=('Consolas', 10),
              relief=tk.RAISED, bd=2, padx=15, pady=3, cursor='hand2').pack(side=tk.RIGHT, padx=10)


def _buy_darknet(self, eid, w):
    """Purchase an exploit from the Darknet."""
    ex = g.buy_exploit(eid)
    if ex is None:
        self.console_out(_('Cannot purchase: insufficient funds or already owned.'), 'red')
        self._sound_error()
        return
    # Add the file to local storage if it has content
    if 'content' in ex:
        g.local_files.append({'name': ex['name'], 'content': ex['content']})
    self.console_out(_fmt('[+] DOWNLOADED: {} from Darknet!', ex['name']), 'green')
    self.console_out(_fmt('    {}', _(ex['desc'])), 'dim')
    g.add_log(_fmt('Darknet purchase: {} (${})', ex['name'], ex['cost']), 'ok')
    g.check_achievements()
    self._sound_success()
    self.refresh_all()
    w.destroy()
    self.h_darknet([], '')


# ═══════════════════════════════════════════════════════════════════════════════
# Patch methods onto HackerApp
# ═══════════════════════════════════════════════════════════════════════════════

from ui.app import HackerApp

from ui.lang import _, _fmt
HackerApp._connected = _connected
HackerApp._progress = _progress
HackerApp.h_help = h_help
HackerApp.h_servers = h_servers
HackerApp.h_money = h_money
HackerApp.h_ls = h_ls
HackerApp.h_cat = h_cat
HackerApp.h_delete = h_delete
HackerApp.h_scan = h_scan
HackerApp.h_scanports = h_scanports
HackerApp.h_connect = h_connect
HackerApp.h_logout = h_logout
HackerApp.h_crack = h_crack
HackerApp.h_decrypt = h_decrypt
HackerApp.h_login = h_login
HackerApp.h_download = h_download
HackerApp.h_upload = h_upload
HackerApp.h_exec = h_exec
HackerApp.h_transfer = h_transfer
HackerApp.h_abort = h_abort
HackerApp.h_clear = h_clear
HackerApp.h_config = h_config
HackerApp.h_upgrade = h_upgrade
HackerApp.h_nextlevel = h_nextlevel
HackerApp.h_newgame = h_newgame
HackerApp.h_newgame_wrapper = h_newgame_wrapper
HackerApp.h_bounce = h_bounce
HackerApp.h_bounceinfo = h_bounceinfo
HackerApp.h_bouncehelp = h_bouncehelp
HackerApp.h_killtrace = h_killtrace
HackerApp.h_deletelogs = h_deletelogs
HackerApp.h_sound = h_sound
HackerApp.h_ping = h_ping
HackerApp.h_traceroute = h_traceroute
HackerApp.h_schematic = h_schematic
HackerApp.h_route = h_route
HackerApp.h_crypto = h_crypto
HackerApp.h_buycrypto = h_buycrypto
HackerApp.h_sellcrypto = h_sellcrypto
HackerApp.h_combine = h_combine
HackerApp.h_story = h_story
HackerApp.h_intel = h_intel
HackerApp.h_sellintel = h_sellintel
HackerApp.h_alias = h_alias
HackerApp.h_unalias = h_unalias
HackerApp.h_stats = h_stats
HackerApp.h_email = h_email
HackerApp.h_darknet = h_darknet
HackerApp._buy_darknet = _buy_darknet
# Patch new Phase 5 commands
HackerApp.h_debugstate = h_debugstate
HackerApp.h_validatecontent = h_validatecontent


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Command Registration — register all commands in the CommandRegistry
# ═══════════════════════════════════════════════════════════════════════════════

def _register_commands():
    """Register all commands defined in this file (and callable from app.py)."""
    _register('help', h_help, 'Show this help', aliases=['?'], category='general')
    _register('scan', h_scan, 'Scan a target server', 'host', category='network')
    _register('connect', h_connect, 'Connect to a server', 'host [port]', aliases=['ssh'], category='network')
    _register('logout', h_logout, 'Disconnect from current server', aliases=['disconnect'], category='network')
    _register('crack', h_crack, 'Brute force crack a port', 'host [port]', category='network')
    _register('decrypt', h_decrypt, 'Decrypt server key', 'host', category='network')
    _register('login', h_login, 'Login with known password', 'host pwd', category='network')
    _register('ls', h_ls, 'List local or current server files', aliases=['dir'], category='files')
    _register('cat', h_cat, 'Show file contents', 'file', category='files')
    _register('download', h_download, 'Download file from current server', 'file', category='files')
    _register('upload', h_upload, 'Upload local file to current server', 'file', category='files')
    _register('delete', h_delete, 'Delete a file', 'file', category='files')
    _register('transfer', h_transfer, 'Transfer money from current server', 'amount', category='money')
    _register('money', h_money, 'Show current balance', category='money')
    _register('crypto', h_crypto, 'Show crypto market', category='money')
    _register('buycrypto', h_buycrypto, 'Buy cryptocurrency', 'type amount', category='money')
    _register('sellcrypto', h_sellcrypto, 'Sell cryptocurrency', 'type amount', category='money')
    _register('exec', h_exec, 'Run exploit on current server', 'exploit host', category='exploits')
    _register('darknet', h_darknet, 'Darknet exploit shop', category='exploits')
    _register('bounce', h_bounce, 'Toggle bounce on a server', 'host', category='network')
    _register('bounceinfo', h_bounceinfo, 'Show bounce chain status', category='network')
    _register('bouncehelp', h_bouncehelp, 'Bounce explanation', category='network')
    _register('killtrace', h_killtrace, 'Pay $500 to reduce trace', category='trace')
    _register('deletelogs', h_deletelogs, 'Delete server logs', category='trace')
    _register('config', h_config, 'Show hardware configuration', category='system')
    _register('upgrade', h_upgrade, 'Hardware upgrade menu', category='system')
    _register('nextlevel', h_nextlevel, 'Level up (if enough score)', category='system')
    _register('servers', h_servers, 'List all servers on the network', category='network')
    _register('scanports', h_scanports, 'Detailed port scan', 'host', category='network')
    _register('ping', h_ping, 'Ping a server', 'host', category='network')
    _register('traceroute', h_traceroute, 'Trace route to a server', 'host', category='network')
    _register('schematic', h_schematic, 'Show network grid', category='network')
    _register('route', h_route, 'Show network topology', category='network')
    _register('abort', h_abort, 'Abort current operation', category='system')
    _register('clear', h_clear, 'Clear the console', aliases=['cls'], category='system')
    _register('newgame', h_newgame, 'Start a new game', aliases=['reset'], category='system')
    _register('sound', h_sound, 'Toggle sound effects', category='system')
    _register('stats', h_stats, 'Show player stats', category='system')
    _register('alias', h_alias, 'Create a command alias', 'name cmd', category='general')
    _register('unalias', h_unalias, 'Remove a command alias', 'name', category='general')
    _register('email', h_email, 'Read Darius emails', category='story')
    _register('story', h_story, 'Hacker legend missions', category='story')
    _register('combine', h_combine, 'Combine files (virus factory)', 'file1 file2', category='files')
    _register('intel', h_intel, 'Show stolen government intel', category='story')
    _register('sellintel', h_sellintel, 'Sell intel on black market', 'id', category='story')
    # Phase 5 commands (defined in this file)
    _register('debugstate', h_debugstate, 'Show internal FSM/service state', category='system')
    _register('validatecontent', h_validatecontent, 'Validate all modded content', category='system')


_register_commands()
