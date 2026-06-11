#!/usr/bin/env python3
# HACKER EVOLUTION — Command handlers
# These are patched onto HackerApp at import time.

import random
import threading
import time
import tkinter as tk
from tkinter import messagebox

from engine.config import Colors
from engine.game import g
from data import HARDWARE, STORY_MISSIONS, DARIUS_EMAILS
from ui.rich_bridge import render_to_widget, make_table, make_panel


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _connected(self):
    if not g.current_server:
        self.console_out('Non connesso a un server.', 'red')
        return False
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# h_help
# ═══════════════════════════════════════════════════════════════════════════════

def h_help(self, a, r):
    from rich.table import Table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column('Cmd')
    table.add_column('Desc')
    for c, d in [
        ('HELP/?', 'Aiuto'),
        ('SCAN <host>', 'Trova server'),
        ('CONNECT <host> [port]', 'Connettiti'),
        ('LOGOUT', 'Disconnetti'),
        ('CRACK <host> [port]', 'Forza password'),
        ('DECRYPT <host>', 'Decifra chiave'),
        ('LOGIN <host> <pwd>', 'Accedi con password'),
        ('LS/DIR', 'Lista file'),
        ('CAT <file>', 'Mostra file'),
        ('DOWNLOAD <file>', 'Scarica'),
        ('UPLOAD <file>', 'Carica'),
        ('DELETE <file>', 'Cancella'),
        ('TRANSFER <n>', 'Trasferisci soldi'),
        ('EXEC <e> <h>', 'Esegui exploit'),
        ('BOUNCE <host>', 'Aggiungi/rimuovi bounce'),
        ('BOUNCEINFO', 'Catena bounce'),
        ('BOUNCEHELP', 'Aiuto bounce'),
        ('KILLTRACE', '-10% trace ($500)'),
        ('DELETELOGS', 'Cancella log server'),
        ('CONFIG', 'Mostra hardware'),
        ('UPGRADE', 'Menu upgrade'),
        ('NEXTLEVEL', 'Prossimo livello'),
        ('MONEY', 'Soldi'),
        ('SERVERS', 'Tutti i server'),
        ('SCANPORTS <host>', 'Scansiona porte'),
        ('PING <host>', 'Test connessione'),
        ('TRACEROUTE <host>', 'Traccia percorso'),
        ('SCHEMATIC', 'Reticolo rete'),
        ('MISSIONS', 'Missioni attive'),
        ('NEWMISSION', 'Genera missioni'),
        ('ACHIEVEMENTS', 'Trofei sbloccati'),
        ('CRYPTO', 'Mercato crypto'),
        ('BUYCRYPTO <c> <n>', 'Compra crypto'),
        ('SELLCRYPTO <c> <n>', 'Vende crypto'),
        ('INTEL', 'Lista intelligence rubate'),
        ('SELLINTEL <id>', 'Vendi intel al mercato nero'),
        ('MARKET', 'Mercato nero'),
        ('STORY', 'Missioni leggende hacker'),
        ('EMAIL', 'Leggi email Darius'),
        ('SWITCH', 'Interruttore finale (solo endgame)'),
        ('COMBINE <f1> <f2>', 'Fabbrica virus'),
        ('SKILLS', 'Skill tree'),
        ('ALIAS <n> <c>', 'Crea alias'),
        ('UNALIAS <n>', 'Rimuovi alias'),
        ('VIEW', 'Vista 3D server'),
        ('STATS', 'Statistiche'),
        ('GLITCH', 'Effetto glitch'),
        ('SOUND', 'Toggle suono'),
        ('NEWGAME', 'Nuova partita'),
    ]:
        table.add_row(f'[bold cyan]{c}[/]', f'[dim]{d}[/]')
    panel = make_panel(table, title='[bold yellow]COMANDI DISPONIBILI[/]')
    self.console_rich(panel)


# ═══════════════════════════════════════════════════════════════════════════════
# h_servers / h_money / h_ls / h_cat / h_delete
# ═══════════════════════════════════════════════════════════════════════════════

def h_servers(self, a, r):
    rows = []
    for s in g.servers:
        st = '[green]HACKED[/]' if g.hacked(s) else '[yellow]SCANNED[/]' if s['scanned'] else '[dim]UNKNOWN[/]'
        gov = '[red]GOV[/]' if s.get('is_gov') else ''
        rows.append([st, gov, f'[cyan]{s["name"]}[/]', f'[dim]{s["desc"]}[/]'])
    table = make_table(
        title=f'[bold yellow]SERVER ({len(g.servers)})[/]',
        headers=['Status', 'Type', 'Name', 'Description'],
        rows=rows,
    )
    self.console_rich(table)


def h_money(self, a, r):
    self.console_out(f'Soldi: ${g.money:,}', 'yellow')


def h_ls(self, a, r):
    if self._connected():
        s = g.current_server
        self.console_out(f'\n── {s["name"]}:{g.current_port} ──', 'cyan')
        for f in s['files']:
            self.console_out(f'  {f["name"]:<35} {max(1, len(f["content"]) // 100)} blk')
    else:
        self.console_out(f'── LOCALE ({g.used_mem()}/{g.memory()} blocks) ──', 'cyan')
        for f in g.local_files:
            self.console_out(f'  {f["name"]:<35} {max(1, len(f["content"]) // 100)} blk')


def h_cat(self, a, r):
    if not a:
        self.console_out('Usa: CAT <file>', 'red')
        return
    fname = a[0]
    if self._connected():
        for f in g.current_server['files']:
            if f['name'] == fname:
                self.console_out(f'\n{f["content"]}', 'white')
                return
    for f in g.local_files:
        if f['name'] == fname:
            self.console_out(f'\n{f["content"]}', 'white')
            return
    self.console_out(f'File non trovato: {fname}', 'red')


def h_delete(self, a, r):
    if not a:
        self.console_out('Usa: DELETE <file>', 'red')
        return
    fname = a[0]
    if self._connected():
        for i, f in enumerate(g.current_server['files']):
            if f['name'] == fname:
                g.current_server['files'].pop(i)
                if g.add_trace(1):
                    self.console_out('TRACED!', 'red')
                self.console_out(f'{fname} eliminato.', 'green')
                self.refresh_all()
                return
    for i, f in enumerate(g.local_files):
        if f['name'] == fname:
            g.local_files.pop(i)
            self.console_out(f'{fname} eliminato.', 'green')
            self.refresh_all()
            return
    self.console_out(f'File non trovato: {fname}', 'red')


# ═══════════════════════════════════════════════════════════════════════════════
# h_scan / h_scanports
# ═══════════════════════════════════════════════════════════════════════════════

def h_scan(self, a, r):
    if not a:
        self.console_out('Usa: SCAN <host>', 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if s:
        s['scanned'] = True
        self.console_out_type(f'\n[+] Server TROVATO: {s["name"]}', 'green', 12)
        self.console_out_type(f'    Porte: {", ".join(str(p) for p in s["ports"])}', 'cyan', 12)
        self.console_out_type(f'    Chiave: {s["key_bits"]} bits', 'yellow', 12)
        self.console_out_type(f'    Stato: {"CIFRATO" if not s["decrypted"] else "DECIFRATO"}', 'orange', 12)
        if g.add_trace(1):
            self.console_out('TRACED!', 'red')
        self.update_map()
    else:
        self.console_out(f'[-] Host non trovato: {host}', 'red')
        self._sound_error()
    self.refresh_all()


def h_scanports(self, a, r):
    if not a:
        self.console_out('Usa: SCANPORTS <host>', 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(f'Host sconosciuto: {host}', 'red')
        return
    s['scanned'] = True
    self.console_out(f'Scansione porte su {host}...', 'yellow')
    def run():
        for p in s['ports']:
            if not self.root.winfo_exists():
                return
            time.sleep(0.3)
            filtered = random.random() < 0.15
            self.root.after(0, lambda pp=p, f=filtered: self.console_out(
                f'  Porta {pp}: {"FILTRATA" if f else "APERTA"}', 'orange' if f else 'green'))
        self.root.after(0, lambda: (self.update_map(), self.refresh_all()))
    threading.Thread(target=run, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════════════
# h_connect / h_logout
# ═══════════════════════════════════════════════════════════════════════════════

def h_connect(self, a, r):
    if not a:
        self.console_out('Usa: CONNECT <host> [port]', 'red')
        return
    host = a[0].lower()
    port = int(a[1]) if len(a) > 1 else 80
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
        return
    if not s['scanned']:
        self.console_out(f'Scansiona prima {host}', 'red')
        return
    if not s['decrypted']:
        self.console_out(f'Decifra prima {host}', 'red')
        return
    if not s['cracked'].get(port):
        self.console_out(f'Cracka prima {host}:{port}', 'red')
        return
    g.current_server = s
    g.current_port = port
    s['visited'] = True
    self.console_out_type(f'[+] Connesso a {host}:{port}', 'green', 12)
    self._sound_connect()
    if g.add_trace(1):
        self.console_out('TRACED!', 'red')
    self._update_prompt()
    self.refresh_all()
    if s.get('is_gov'):
        self.root.after(200, lambda: self._gov_login_portal(s))


def h_logout(self, a, r):
    if g.current_server:
        self.console_out_type(f'Disconnesso da {g.current_server["name"]}', 'yellow', 12)
        g.current_server = None
        g.current_port = None
        self._update_prompt()
        self.refresh_all()
    else:
        self.console_out('Non connesso.', 'red')


# ═══════════════════════════════════════════════════════════════════════════════
# h_crack / h_decrypt / h_login
# ═══════════════════════════════════════════════════════════════════════════════

def h_crack(self, a, r):
    if len(a) < 1:
        self.console_out('Usa: CRACK <host> [port]', 'red')
        return
    host = a[0].lower()
    port = int(a[1]) if len(a) > 1 else 80
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
        return
    if not s['scanned']:
        self.console_out(f'Scansiona prima {host}', 'red')
        return
    if port not in s['ports']:
        self.console_out(f'Porta {port} non trovata', 'red')
        return
    pwd_len = random.randint(8, min(32, 8 + s['key_bits'] // 16))
    self.console_out_type(f'Brute force su {host}:{port}... ({pwd_len} chars)', 'yellow', 10)
    self._progress('crack', pwd_len * 100, host, port)


def h_decrypt(self, a, r):
    if not a:
        self.console_out('Usa: DECRYPT <host>', 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
        return
    if not s['scanned']:
        self.console_out(f'Scansiona prima {host}', 'red')
        return
    if s['decrypted']:
        self.console_out(f'{host} già decifrato.', 'yellow')
        return
    self.console_out_type(f'Decifratura chiave {s["key_bits"]} bits...', 'yellow', 10)
    self._progress('decrypt', s['key_bits'], host, None)


def h_login(self, a, r):
    if len(a) < 2:
        self.console_out('Usa: LOGIN <host> <password>', 'red')
        return
    host = a[0].lower()
    pwd = a[1]
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
        return
    known_pwds = {'mywordismypassword': 49, 'admin123': 999, 'root!': 21, 'letmein': 25}
    if pwd in known_pwds:
        port = known_pwds[pwd]
        if port in s['ports']:
            s['cracked'][port] = True
            self.console_out_type(f'[+] Accesso a {host}:{port}', 'green', 12)
            if g.add_trace(1):
                self.console_out('TRACED!', 'red')
            g.check_story_missions('login')
            self.refresh_all()
            return
    self.console_out('Password errata.', 'red')


# ═══════════════════════════════════════════════════════════════════════════════
# h_download / h_upload / h_exec / h_transfer / h_abort / h_clear
# ═══════════════════════════════════════════════════════════════════════════════

def h_download(self, a, r):
    if not a:
        self.console_out('Usa: DOWNLOAD <file>', 'red')
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
                    self.console_out('TRACED!', 'red')
                g.check_story_missions('download')
                # Fix: 'host' was undefined in original — use current server name
                sname = g.current_server['name'].lower()
                if 'gsm' in sname or 'tower' in sname:
                    g.check_story_missions('gsm')
            else:
                self.console_out('Memoria piena!', 'red')
            self.refresh_all()
            return
    self.console_out(f'File non trovato: {fname}', 'red')


def h_upload(self, a, r):
    if not a:
        self.console_out('Usa: UPLOAD <file>', 'red')
        return
    if not self._connected():
        return
    fname = a[0]
    for f in g.local_files:
        if f['name'] == fname:
            g.current_server['files'].append(dict(f))
            self.console_out_type(f'Upload: {fname}', 'green', 10)
            if g.add_trace(2):
                self.console_out('TRACED!', 'red')
            g.check_story_missions('upload')
            self.refresh_all()
            return
    self.console_out(f'File non trovato in locale: {fname}', 'red')


def h_exec(self, a, r):
    if len(a) < 2:
        self.console_out('Usa: EXEC <exploit> <host>', 'red')
        return
    exploit = a[0]
    host = a[1].lower()
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
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
                self.console_out('Porta non valida.', 'red')
                return
            g.hack_count += 1
            self.console_out_type(f'[+] Exploit {exploit} eseguito su {host}!', 'green', 12)
            self._sound_success()
            g.add_news('Exploit {e} deployed su {h}', e=exploit, h=host)
            if g.add_trace(5):
                self.console_out('TRACED!', 'red')
            self.refresh_all()
            return
    self.console_out('Exploit non trovato.', 'red')


def h_transfer(self, a, r):
    if not a:
        self.console_out('Usa: TRANSFER <amount>', 'red')
        return
    if not self._connected():
        return
    try:
        amt = int(a[0])
    except ValueError:
        self.console_out('Importo non valido.', 'red')
        return
    s = g.current_server
    if s['money'] < amt:
        self.console_out(f'Il server ha solo ${s["money"]}', 'red')
        return
    self.console_out_type(f'Trasferimento ${amt}...', 'yellow', 10)
    self._progress('transfer', amt, None, None)


def h_abort(self, a, r):
    self.action_cancel = True
    self.console_out('Annullato.', 'yellow')


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
        title='[bold yellow]HARDWARE CONFIG[/]',
        headers=['Component', 'Level', 'Progress', 'Effect'],
        rows=rows,
    )
    self.console_rich(table)
    stats = f'  [bold cyan]Memoria:[/] {g.used_mem()}/{g.memory()} blk  [bold yellow]Trace:[/] {g.trace_level:.1f}%  [bold green]Soldi:[/] ${g.money:,}'
    self.console_rich(stats)


def h_upgrade(self, a, r):
    self.show_upgrade()


# ═══════════════════════════════════════════════════════════════════════════════
# h_nextlevel / h_newgame
# ═══════════════════════════════════════════════════════════════════════════════

def h_nextlevel(self, a, r):
    self.console_out('Passando al livello successivo...', 'yellow')
    g.level += 1
    from engine.game import generate_servers
    g.servers = generate_servers(8 + min(g.level, 4))
    g.current_server = None
    g.current_port = None
    g.bounce_chain = []
    g.skill_points += 1
    g.gen_missions()
    g.add_news('Livello {lvl} sbloccato — nuovi target disponibili', lvl=g.level)
    g.add_log(f'Livello {g.level} iniziato!', 'ok')
    self.console_out(f'═══ LIVELLO {g.level} ═══', 'green')
    self.console_out(f'Generate {len(g.missions)} missioni.', 'dim')
    for e in g.narrative_unread:
        if e['lvl'] <= g.level:
            g.narrative_unread.remove(e)
            self.console_out(f'📧 NUOVA EMAIL: {e["sub"]} (digita EMAIL)', 'yellow')
            self.notify(f'📧 {e["sub"]}', 'cyan')
            break
    for sm in STORY_MISSIONS:
        if sm['lvl'] == g.level and not g.story_progress.get(sm['id']):
            self.console_out(f'📜 STORY SBLOCCATA: {sm["name"]} (digita STORY)', 'yellow')
            self.notify(f'📜 {sm["name"]} sbloccata!', 'yellow')
    self.update_map()
    self.refresh_all()


def h_newgame_wrapper(self):
    self.h_newgame([], 'newgame')


def h_newgame(self, a, r):
    if messagebox.askyesno('Nuova Partita', 'Ricominciare? Tutti i progressi andranno persi.'):
        g.reset(first=False)
        self.console_clear()
        self.console_out('═══ NUOVA PARTITA ═══', 'green')
        self.console_out('Digita HELP per i comandi.', 'dim')
        self.update_map()
        self.refresh_all()
        g.add_log('Nuova partita iniziata.', 'ok')


# ═══════════════════════════════════════════════════════════════════════════════
# h_bounce / h_bounceinfo / h_bouncehelp
# ═══════════════════════════════════════════════════════════════════════════════

def h_bounce(self, a, r):
    if not a:
        self.console_out('Usa: BOUNCE <host>', 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
        return
    if g.current_server:
        self.console_out('Disconnettiti prima.', 'red')
        return
    if not g.hacked(s):
        self.console_out(f'{host} non hackerato.', 'red')
        return
    if s['bounce_used'] >= 3:
        self.console_out(f'{host} ha finito i rimbalzi.', 'red')
        return
    if host in g.bounce_chain:
        g.bounce_chain.remove(host)
        s['bounce_used'] -= 1
        self.console_out(f'{host} rimosso dal bounce.', 'yellow')
    else:
        g.bounce_chain.append(host)
        s['bounce_used'] += 1
        g.stats['bounces'] += 1
        self.console_out(f'{host} aggiunto al bounce. ({len(g.bounce_chain)} hop)', 'green')
        g.check_story_missions('bounce')
    self.update_map()


def h_bounceinfo(self, a, r):
    if not g.bounce_chain:
        self.console_out('Catena vuota.', 'yellow')
        return
    self.console_out(f'Catena ({len(g.bounce_chain)} hop):', 'cyan')
    for i, h in enumerate(g.bounce_chain):
        self.console_out(f'  {i + 1}. {h}', 'green')
    self.console_out(f'Trace multiplier: {g.trace_mult()}x', 'yellow')


def h_bouncehelp(self, a, r):
    self.console_out('═' * 60, 'cyan')
    self.console_out('BOUNCE HELP', 'yellow')
    self.console_out('═' * 60, 'cyan')
    for l in [
        'I bounced link aumentano il tempo di trace.',
        'Usa BOUNCE <host> per aggiungere server hackerati.',
        'Trace time = base × (hop+1) × firewall bonus',
        'Max 3 rimbalzi per server.',
        'Non puoi modificare il bounce mentre sei connesso.',
    ]:
        self.console_out(f'  {l}', 'green')


# ═══════════════════════════════════════════════════════════════════════════════
# h_killtrace / h_deletelogs
# ═══════════════════════════════════════════════════════════════════════════════

def h_killtrace(self, a, r):
    if g.money < 500:
        self.console_out('Servono $500.', 'red')
        return
    g.money -= 500
    g.trace_level = max(0, g.trace_level - 10)
    g.trace_count += 1
    self.console_out(f'Trace ridotto a {g.trace_level:.1f}% (-$500)', 'green')
    self.refresh_all()


def h_deletelogs(self, a, r):
    if not self._connected():
        return
    red = min(15, g.trace_level)
    g.trace_level = max(0, g.trace_level - red)
    self.console_out(f'Log cancellati. Trace: {g.trace_level:.1f}%', 'green')
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
                self.console_out(f'[+] Password CRACKATA su {host}:{port}!', 'green')
                self._sound_success()
                g.add_news('Server violato! {h}:{p} compromesso.', h=host, p=port)
                g.add_log(f'Crack: {host}:{port}', 'ok')
                g.check_story_missions('crack')
                cx, cy = s.get('pos', (100, 100))
                self.root.after(10, lambda cx=cx, cy=cy: self._impact_wave(cx, cy))
        elif action == 'decrypt' and host:
            s = g.server(host)
            if s:
                s['decrypted'] = True
            self.console_out(f'[+] Chiave DECIFRATA su {host}!', 'green')
            self._sound_success()
            g.add_news('Chiave decifrata per {h}', h=host)
            g.add_log(f'Decrypt: {host}', 'ok')
        elif action == 'transfer' and g.current_server:
            amt = total
            g.current_server['money'] -= amt
            g.money += amt
            g.score += amt // 10
            g.total_earned += amt
            g.stats['transfers'] += 1
            g.stats['money_stolen'] += amt
            g.check_story_missions('transfer')
            self.console_out(f'[+] Trasferiti ${amt}', 'green')
            self._sound_success()
            g.add_news('Fondi trasferiti: ${a} da {h}', a=amt, h=g.current_server['name'])
            g.add_log(f'Transfer: ${amt}', 'ok')

        if self._hex_lbl:
            self._hex_lbl.config(text='')
        if g.add_trace(trace_p / max(1, mult)):
            self.console_out('⚠️ TRACE 100%! GAME OVER!', 'red')
            g.add_log('GAME OVER - Trace 100%', 'fail')

        self.action_active = False
        self.pf.pack_forget()
        self.refresh_all()

    threading.Thread(target=run, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════════════
# h_sound / h_ping / h_traceroute / h_schematic
# ═══════════════════════════════════════════════════════════════════════════════

def h_sound(self, a, r):
    self._sound = not self._sound
    self.console_out(f'Suono: {"ON" if self._sound else "OFF"}', 'green' if self._sound else 'red')


def h_ping(self, a, r):
    if not a:
        self.console_out('Usa: PING <host>', 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
        return
    self.console_out(f'PING {host}...', 'yellow')
    def run():
        for _ in range(4):
            if not self.root.winfo_exists():
                return
            ms = random.randint(5, 120)
            ttl = random.randint(32, 255)
            time.sleep(0.4)
            self.root.after(0, lambda m=ms, t=ttl: self.console_out(
                f'  Risposta da {host}: byte=64 tempo={m}ms TTL={t}', 'green'))
        self.root.after(0, lambda: self.console_out('  --- statistics ---', 'cyan'))
        self.root.after(0, lambda: self.console_out(
            '  Pacchetti: inviati=4 ricevuti=4 persi=0', 'green'))
    threading.Thread(target=run, daemon=True).start()


def h_traceroute(self, a, r):
    if not a:
        self.console_out('Usa: TRACEROUTE <host>', 'red')
        return
    host = a[0].lower()
    s = g.server(host)
    if not s:
        self.console_out(f'Sconosciuto: {host}', 'red')
        return
    self.console_out(f'Traceroute verso {host}...', 'yellow')
    def run():
        hops = random.randint(3, 8)
        for i in range(1, hops + 1):
            if not self.root.winfo_exists():
                return
            ip = f'{random.randint(10, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}'
            ms = random.randint(1, 80)
            time.sleep(0.2)
            self.root.after(0, lambda h=i, a=ip, m=ms: self.console_out(f'  {h:2}  {a:<15} {m}ms', 'green'))
        self.root.after(0, lambda: self.console_out(f'  {hops + 1:2}  {host}  *', 'cyan'))
    threading.Thread(target=run, daemon=True).start()


def h_schematic(self, a, r):
    self.console_out('═' * 60, 'cyan')
    self.console_out('SCHEMATIC — Reticolo Rete', 'yellow')
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
    self.console_out('CRYPTOVALUTE', 'yellow')
    self.console_out('─' * 60, 'cyan')
    for c in g.crypto:
        val = g.crypto[c]['qty'] * g.crypto[c]['price']
        self.console_out(f'  {c.upper():>4}  ${g.crypto[c]["price"]:>6,}  QTY: {g.crypto[c]["qty"]:.4f}  VAL: ${val:,.0f}', 'cyan')
    total = sum(g.crypto[c]['qty'] * g.crypto[c]['price'] for c in g.crypto)
    self.console_out(f'  Totale portafoglio crypto: ${total:,.0f}', 'yellow')
    self.console_out('  Usa: BUYCRYPTO <coin> <amount>  |  SELLCRYPTO <coin> <amount>', 'dim')
    self.console_out('  Coins: BTC, ETH, XMR', 'dim')


def h_buycrypto(self, a, r):
    if len(a) < 2:
        self.console_out('Usa: BUYCRYPTO <coin> <amount>', 'red')
        return
    coin = a[0].lower()
    try:
        amt = float(a[1])
    except ValueError:
        self.console_out('Importo non valido.', 'red')
        return
    if coin not in g.crypto:
        self.console_out('Coin non valida. BTC, ETH, XMR', 'red')
        return
    cost = amt * g.crypto[coin]['price']
    if g.money < cost:
        self.console_out(f'Servono ${cost:,.0f}', 'red')
        return
    g.money -= cost
    g.crypto[coin]['qty'] += amt
    self.console_out(f'Comprati {amt:.4f} {coin.upper()} per ${cost:,.0f}', 'green')
    g.add_news('Acquisto crypto: {a:.2f} {c}', a=amt, c=coin.upper())


def h_sellcrypto(self, a, r):
    if len(a) < 2:
        self.console_out('Usa: SELLCRYPTO <coin> <amount>', 'red')
        return
    coin = a[0].lower()
    try:
        amt = float(a[1])
    except ValueError:
        self.console_out('Importo non valido.', 'red')
        return
    if coin not in g.crypto:
        self.console_out('Coin non valida. BTC, ETH, XMR', 'red')
        return
    if g.crypto[coin]['qty'] < amt:
        self.console_out(f'Hai solo {g.crypto[coin]["qty"]:.4f} {coin.upper()}', 'red')
        return
    g.crypto[coin]['qty'] -= amt
    gain = amt * g.crypto[coin]['price']
    g.money += int(gain)
    g.total_earned += int(gain)
    self.console_out(f'Venduti {amt:.4f} {coin.upper()} per ${int(gain):,}', 'green')


# ═══════════════════════════════════════════════════════════════════════════════
# h_combine (virus factory)
# ═══════════════════════════════════════════════════════════════════════════════

def h_combine(self, a, r):
    if len(a) < 2:
        self.console_out('Usa: COMBINE <file1> <file2>', 'red')
        return
    f1 = next((f for f in g.local_files if f['name'] == a[0]), None)
    f2 = next((f for f in g.local_files if f['name'] == a[1]), None)
    if not f1 or not f2:
        self.console_out('File non trovato.', 'red')
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
                self.console_out('Memoria piena!', 'red')
                return
            g.local_files.append({'name': new_name, 'content': new_content})
            if f1 in g.local_files:
                g.local_files.remove(f1)
            if f2 in g.local_files:
                g.local_files.remove(f2)
            self.console_out(f'[+] Creato {new_name} dai file {f1["name"]} + {f2["name"]}!', 'green')
            g.check_story_missions('combine')
            self._sound_success()
            self.refresh_all()
            return
    self.console_out('Nessuna combinazione valida. Prova exploit + bin.', 'red')


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
            status = '[green]COMPLETATA[/]'
        elif current:
            icon = '▶'
            color = 'yellow'
            status = '[bold yellow]ATTIVA[/]'
        elif unlocked:
            icon = '○'
            color = 'dim'
            status = '[dim]DISPONIBILE[/]'
        else:
            icon = '🔒'
            color = 'dim'
            status = '[dim]BLOCCATA[/]'
        name = f'[{color}]{icon} [{sm["lvl"]}] {sm["name"]}[/]'
        desc = f'[dim]{sm["desc"][:65]}[/]'
        reward = f'[yellow]${sm["reward"]:,}[/]'
        rows.append([name, desc, status, reward])
        if current:
            rows.append([f'[yellow]   🎯 {sm["obj"]}[/]', '', '', ''])
    table = make_table(
        title='[bold yellow]MISSIONI LEGGENDE HACKER[/]',
        headers=['Missione', 'Descrizione', 'Stato', 'Reward'],
        rows=rows,
    )
    self.console_rich(table)
    complete = sum(1 for v in g.story_progress.values() if v)
    self.console_rich(f'[bold green]Completate:[/] {complete}/{len(STORY_MISSIONS)}')


def h_intel(self, a, r):
    if not g.gov_intel:
        self.console_out('Nessuna intelligence rubata.', 'dim')
        return
    self.console_out('═' * 40, 'cyan')
    self.console_out('📁 INTELLIGENCE RUBATE', 'yellow')
    self.console_out('═' * 40, 'cyan')
    for i, ii in enumerate(g.gov_intel):
        self.console_out(f'  [{i}] {ii["name"]} — ${ii["value"]:,}', 'green')
        self.console_out(f'       {ii["desc"]}', 'dim')
    self.console_out('Usa SELLINTEL <id> per vendere al mercato nero.', 'yellow')


def h_sellintel(self, a, r):
    if not a:
        self.console_out('Usa: SELLINTEL <id>  (vedi INTEL per la lista)', 'red')
        return
    try:
        idx = int(a[0])
    except ValueError:
        self.console_out('ID non valido.', 'red')
        return
    if idx < 0 or idx >= len(g.gov_intel):
        self.console_out(f'ID {idx} non trovato. Usa INTEL per la lista.', 'red')
        return
    ii = g.gov_intel.pop(idx)
    payout = int(ii['value'] * (0.7 + random.random() * 0.3))
    g.money += payout
    g.score += payout // 10
    g.total_earned += payout
    self.console_out(f'[+] Intelligence venduta: {ii["name"]} per ${payout:,}', 'green')
    g.check_story_missions('sell_intel')
    self._sound_success()
    g.add_news('Intel {i} venduto al mercato nero (+${p})', i=ii['name'], p=payout)
    self.refresh_all()


# ═══════════════════════════════════════════════════════════════════════════════
# h_alias / h_unalias
# ═══════════════════════════════════════════════════════════════════════════════

def h_alias(self, a, r):
    if len(a) < 2:
        if g.aliases:
            self.console_out('Alias attivi:', 'yellow')
            for al in g.aliases:
                self.console_out(f'  {al} → {g.aliases[al]}', 'cyan')
        else:
            self.console_out('Nessun alias.', 'dim')
        return
    g.aliases[a[0]] = ' '.join(a[1:])
    self.console_out(f'Alias: {a[0]} → {" ".join(a[1:])}', 'green')


def h_unalias(self, a, r):
    if not a:
        self.console_out('Usa: UNALIAS <nome>', 'red')
        return
    if a[0] in g.aliases:
        del g.aliases[a[0]]
        self.console_out(f'Alias {a[0]} rimosso.', 'yellow')


# ═══════════════════════════════════════════════════════════════════════════════
# h_stats
# ═══════════════════════════════════════════════════════════════════════════════

def h_stats(self, a, r):
    self.console_out('═' * 60, 'cyan')
    self.console_out('STATISTICHE DETTAGLIATE', 'yellow')
    self.console_out('─' * 60, 'cyan')
    s = g.stats
    hacked = sum(1 for sv in g.servers if g.hacked(sv))
    self.console_out(f'  Server hackerati:     {hacked}/{len(g.servers)}', 'green')
    self.console_out(f'  Tentativi di hack:    {s["hacks"]}', 'cyan')
    self.console_out(f'  Trasferimenti:        {s["transfers"]}', 'yellow')
    self.console_out(f'  Soldi rubati:         ${s["money_stolen"]:,}', 'white')
    self.console_out(f'  Bounce usati:         {s["bounces"]}', 'pink')
    self.console_out(f'  Missioni completate:  {s["missions_done"]}', 'green')
    self.console_out(f'  Trace massima:        {g.max_trace:.1f}%',
                     'red' if g.max_trace > 80 else 'yellow')
    self.console_out(f'  Livello:              {g.level}', 'cyan')
    self.console_out(f'  Soldi totali:         ${g.money:,}', 'yellow')
    self.console_out(f'  Score:                {g.score:,}', 'green')
    self.console_out(f'  Tempo gioco:          --', 'dim')
    self.console_out('─' * 60, 'cyan')


# ═══════════════════════════════════════════════════════════════════════════════
# h_email
# ═══════════════════════════════════════════════════════════════════════════════

def h_email(self, a, r):
    emails = [e for e in DARIUS_EMAILS if e['lvl'] <= g.level]
    if not emails:
        self.console_out('Nessuna email da Darius.', 'dim')
        return
    self.console_out('═' * 60, 'cyan')
    self.console_out('📧 EMAIL — Darius', 'yellow')
    self.console_out('═' * 60, 'cyan')
    for e in emails:
        self.console_out(f'  Oggetto: {e["sub"]}', 'cyan')
        self.console_out(f'  (Livello {e["lvl"]})', 'dim')
        self.console_out('─' * 40, 'dim')
        for line in e['body'].split('\n'):
            self.console_out(f'  {line}', 'white')
        self.console_out('')


# ═══════════════════════════════════════════════════════════════════════════════
# Patch methods onto HackerApp
# ═══════════════════════════════════════════════════════════════════════════════

from ui.app import HackerApp

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
