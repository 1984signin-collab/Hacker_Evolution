#!/usr/bin/env python3
# HACKER EVOLUTION — Game Engine
# Gestisce lo stato di gioco, il sistema di salvataggio e la logica di base.

import json
import os
import random
import time

from engine.config import SAVE_FILE, AUTO_FILE
from engine.command_registry import CommandRegistry
from engine.services import EventBus, DomainEvent, DomainEventType
from engine.services.network_service import NetworkService
from engine.services.economy_service import EconomyService
from engine.services.trace_service import TraceService
from engine.services.mission_service import MissionService
from engine.services.sentinel_service import SentinelService
from engine.sentinel import SentinelFSM
from data import SERVERS_POOL, GOV_INTEL_TYPES, GOV_DOMAINS, STORY_MISSIONS, DARIUS_EMAILS, HARDWARE, EXPLOITS


from ui.lang import _, _fmt
# ═══════════════════════════════════════════════════════════════════════════════
# Server generation
# ═══════════════════════════════════════════════════════════════════════════════

def generate_servers(count=10):
    """Genera una lista random di server dal pool globale.
    Costruisce un grafo di rete: ogni server ha collegamenti (links)
    ad altri server visibili. I server di ingresso sono visibili da subito.
    """
    pool = random.sample(SERVERS_POOL, min(count, len(SERVERS_POOL)))
    # Mappa temporanea name → dict per risolvere i link
    name_to_sv = {}
    servers = []
    for s in pool:
        is_gov = '.gov' in s[0] or '.mil' in s[0] or '.int' in s[0]
        links_raw = s[6] if len(s) > 6 else []
        sv = {
            'name': s[0],
            'ports': list(s[1]),
            'key_bits': s[2],
            'files': [{'name': f[0], 'content': f[1]} for f in s[3]],
            'money': s[4],
            'desc': s[5],
            'cracked': {},
            'decrypted': False,
            'scanned': False,
            'bounce_used': 0,
            'visited': False,
            'pos': (0, 0),
            'is_gov': is_gov,
            'intel_stolen': False,
            # Nuovi campi per il grafo di rete
            'links': [],       # lista di riferimenti ad altri server (oggetti)
            'links_raw': links_raw,  # nomi dei vicini dal pool (per salvataggio)
            'visible': False,  # il giocatore lo vede sulla mappa?
            'entry_point': False,  # server d'ingresso
        }
        if is_gov:
            sv['money'] = 0
            intel = random.choice(GOV_INTEL_TYPES)
            sv['intel_id'] = intel[0]
            sv['intel_desc'] = intel[1]
            sv['intel_value'] = intel[2]
            sv['intel_size'] = intel[3]
        servers.append(sv)
        name_to_sv[s[0].lower()] = sv

    # Risolvi i collegamenti: solo tra server presenti in questa partita
    for sv in servers:
        sv['links'] = [
            name_to_sv[n.lower()]
            for n in sv['links_raw']
            if n.lower() in name_to_sv
        ]

    # Determina i server d'ingresso (desk) e rendili visibili
    desk_names = {'desk-11.corporate.com', 'desk-25.corporate.com'}
    for sv in servers:
        if sv['name'] in desk_names:
            sv['visible'] = True
            sv['entry_point'] = True
    # Fallback: se nessun desk è nel pool, rendi visibile il primo server
    if not any(s['visible'] for s in servers):
        servers[0]['visible'] = True
        servers[0]['entry_point'] = True

    return servers


# ═══════════════════════════════════════════════════════════════════════════════
# Game State
# ═══════════════════════════════════════════════════════════════════════════════

class Game:
    ACHIEVEMENTS = [
        ('first_hack', 'First Hack!', 'Hack the first server', 5),
        ('ten_hacks', 'Specialist', 'Hack 10 servers', 25),
        ('twenty_hacks', 'Hacker Legend', 'Hack 20 servers', 100),
        ('thief', 'Thief', 'Total $10,000', 20),
        ('rich', 'Rich', 'Total $100,000', 50),
        ('fat_cat', 'Fat Cat', 'Total $1,000,000', 500),
        ('bounce_3', 'Bouncer', 'Chain of 3 hops', 10),
        ('bounce_5', 'Bounce Master', 'Chain of 5 hops', 50),
        ('trace_90', 'Ghost', 'Survive 90% trace', 30),
        ('hardware_full', 'Power', 'All hardware maxed', 100),
        ('level_5', 'Veteran', 'Reach level 5', 20),
        ('level_10', 'Elite', 'Reach level 10', 100),
        ('neural', 'Cyberpunk', 'Buy Neural Adapter', 200),
    ]

    def __init__(self):
        self.reset()
        if os.path.exists(AUTO_FILE):
            self.load(AUTO_FILE)

    def reset(self, first=True):
        self.money = 500
        self.level = 1
        self.score = 0
        self.trace_level = 0.0
        self.hack_count = 0
        self.trace_count = 0
        self.servers = generate_servers()
        self.current_server = None
        self.current_port = None
        self.local_files = []
        self.local_memory = 10
        self.bounce_chain = []
        self.log = []
        self.hardware = {h[1]: 0 for h in HARDWARE}
        self.missions = []
        self.mission_active = None
        self.achievements = {}
        self.news = []
        self.total_earned = 0
        self.max_trace = 0
        self.crypto = {
            'btc': {'qty': 0, 'price': 1000},
            'eth': {'qty': 0, 'price': 200},
            'xmr': {'qty': 0, 'price': 50},
        }
        self.skills = {
            'stealth': 0, 'brute': 0, 'phish': 0,
            'crypto_bonus': 0, 'trace_reduce': 0,
        }
        self.skill_points = 0
        self.aliases = {}
        self.black_market_items = []
        self.hackback_cooldown = 0
        self.stats = {
            'hacks': 0, 'transfers': 0, 'money_stolen': 0,
            'servers_hacked': 0, 'bounces': 0, 'missions_done': 0,
            'download_count': 0,
        }
        self.gov_intel = []
        self.story_progress = {s['id']: False for s in STORY_MISSIONS}
        self.story_active = 0
        self.narrative_unread = [dict(e) for e in DARIUS_EMAILS]
        self.narrative_switch_used = False
        self._notify_cb = None
        # ── Darknet / exploits ──
        self.exploits = []        # list of exploit IDs the player owns
        self.stealth_charges = 0  # remaining stealth boost actions
        # ── Sentinel AI ──
        self.sentinel_state = 'DORMANT'  # DORMANT → ANALYZING → ACTIVE
        self.sentinel_timer = 0          # ticks before state transition
        self.sentinel_cooldown = 0       # ticks before can re-enter ACTIVE
        self.sentinel_strikes = 0        # how many times sentinel attacked
        self.ports_closed = {}           # {server_name: [port, ...]} ports sentinel closed
        # ── Random events ──
        self.event_timer = 0
        self.event_paused = False

        # ── Phase 3+4: Services & Event Bus ──
        self._bus = EventBus()
        self._init_services()

    def _init_services(self):
        """Initialize the service layer (Phase 3: Domain)."""
        self.services = Services(self)

    def _make_sentinel_fsm(self):
        """Create the SentinelFSM instance wired to this game."""
        return SentinelFSM(
            get_trace=lambda: self.trace_level,
            get_current_server=lambda: self.current_server,
            get_local_files=lambda: self.local_files,
            add_log=self.add_log,
            add_news=self.add_news,
            notify=self.notify,
            has_exploit=self.has_exploit,
        )

    @property
    def network(self) -> 'NetworkService':
        return self.services.network

    @property
    def economy(self) -> 'EconomyService':
        return self.services.economy

    @property
    def trace_svc(self) -> 'TraceService':
        return self.services.trace

    @property
    def mission_svc(self) -> 'MissionService':
        return self.services.missions

    @property
    def sentinel_svc(self) -> 'SentinelService':
        return self.services.sentinel

    # ── Hardware helpers ──

    def hw_lvl(self, t):
        return self.hardware.get(t, 0)

    def trace_mult(self):
        se = self.skill_effect()
        base = (2 ** self.hw_lvl('firewall')) * (len(self.bounce_chain) + 1)
        neural = (2 ** self.hw_lvl('neural')) if self.hw_lvl('neural') else 1
        return base * neural * (1 + se['stealth'])

    def transfer_speed(self):
        s = 2 ** self.hw_lvl('modem')
        return s * (2 ** self.hw_lvl('neural')) if self.hw_lvl('neural') else s

    def crack_speed(self):
        se = self.skill_effect()
        s = (2 ** self.hw_lvl('cpu')) * se['brute']
        return s * (2 ** self.hw_lvl('neural')) if self.hw_lvl('neural') else s

    def memory(self):
        m = self.local_memory + 5 * self.hw_lvl('memory')
        return int(m * (2 ** self.hw_lvl('neural'))) if self.hw_lvl('neural') else int(m)

    def used_mem(self):
        if not self.local_files:
            return 0
        return sum(max(1, len(f['content']) // 100) for f in self.local_files)

    def server(self, n):
        return next((s for s in self.servers if s['name'].lower() == n.lower()), None)

    def hacked(self, s):
        return s and all(s['cracked'].get(p, False) for p in s['ports']) and s['decrypted']

    def can_download(self, f):
        return self.used_mem() + max(1, len(f['content']) // 100) <= self.memory()

    # ── Network graph ──

    @property
    def entry_servers(self):
        """Server d'ingresso: visibili e raggiungibili senza connessione."""
        return [s for s in self.servers if s.get('entry_point')]

    def reachable_servers(self):
        """Elenco dei server raggiungibili al momento."""
        if self.current_server:
            # Connesso: i vicini del server corrente
            return list(self.current_server.get('links', []))
        else:
            # Non connesso: solo i server d'ingresso
            return list(self.entry_servers)

    def is_reachable(self, sv):
        """Un server è raggiungibile se è vicino al server corrente
        oppure è un punto d'ingresso (quando non connessi)."""
        if sv is None:
            return False
        # Se siamo connessi e il target è un vicino → raggiungibile
        if self.current_server and sv in self.current_server.get('links', []):
            return True
        # Se non connessi e il target è un punto d'ingresso → raggiungibile
        if not self.current_server and sv.get('entry_point'):
            return True
        return False

    def reveal_neighbors(self, sv):
        """Rivela i vicini di un server (li rende visibili sulla mappa)."""
        for neighbor in sv.get('links', []):
            neighbor['visible'] = True

    # ── Trace system ──

    def add_trace(self, a):
        se = self.skill_effect()
        a = a * (1 - se['trace_reduce'])
        self.trace_level = min(100, self.trace_level + a)
        if self.trace_level > self.max_trace:
            self.max_trace = self.trace_level
        if self.trace_level >= 100:
            self.add_log(_('GAME OVER - Trace 100%'), 'fail')
            return True
        if self.trace_level > 70:
            self.add_news(
                _('WARNING: Trace at {t:.0f}% — suspicious activity detected!'),
                t=self.trace_level,
            )
        return False

    def add_log(self, m, t='ok'):
        self.log.insert(0, (f'[{time.strftime("%H:%M:%S")}] {m}', t))
        self.log = self.log[:200]

    def add_news(self, template, **kw):
        try:
            txt = template.format(**kw)
        except Exception:
            txt = template
        self.news.insert(0, f'[{time.strftime("%H:%M")}] {txt}')
        self.news = self.news[:30]

    # ── Achievements ──

    def unlock_achievement(self, aid):
        if aid in self.achievements:
            return False
        for a in self.ACHIEVEMENTS:
            if a[0] == aid:
                self.achievements[aid] = True
                self.money += a[3]
                self.score += a[3] * 10
                self.add_log(_fmt('Achievement: {} (+${})', a[1], a[3]), 'ok')
                return a
        return False

    def check_achievements(self):
        unlocked = []
        if self.hack_count >= 1 and 'first_hack' not in self.achievements:
            unlocked.append('first_hack')
        if self.hack_count >= 10 and 'ten_hacks' not in self.achievements:
            unlocked.append('ten_hacks')
        if self.hack_count >= 20 and 'twenty_hacks' not in self.achievements:
            unlocked.append('twenty_hacks')
        if self.total_earned >= 10000 and 'thief' not in self.achievements:
            unlocked.append('thief')
        if self.total_earned >= 100000 and 'rich' not in self.achievements:
            unlocked.append('rich')
        if self.total_earned >= 1000000 and 'fat_cat' not in self.achievements:
            unlocked.append('fat_cat')
        if len(self.bounce_chain) >= 3 and 'bounce_3' not in self.achievements:
            unlocked.append('bounce_3')
        if len(self.bounce_chain) >= 5 and 'bounce_5' not in self.achievements:
            unlocked.append('bounce_5')
        if self.max_trace >= 90 and 'trace_90' not in self.achievements:
            unlocked.append('trace_90')
        if all(self.hw_lvl(h[1]) >= h[5] for h in HARDWARE) and 'hardware_full' not in self.achievements:
            unlocked.append('hardware_full')
        if self.level >= 5 and 'level_5' not in self.achievements:
            unlocked.append('level_5')
        if self.level >= 10 and 'level_10' not in self.achievements:
            unlocked.append('level_10')
        if self.hw_lvl('neural') > 0 and 'neural' not in self.achievements:
            unlocked.append('neural')
        return unlocked

    # ── Missions ──

    def gen_missions(self):
        self.missions = []
        pool = [s for s in self.servers if not g.hacked(s)]
        gov_pool = [s for s in pool if s.get('is_gov')]
        if not pool:
            pool = self.servers[:]
        if gov_pool and random.random() < 0.4:
            s = random.choice(gov_pool)
            self.missions.append({
                'type': 'intel', 'target': s['name'],
                'reward': s['intel_value'] // 2 + 500,
                'desc': f'Rubare {s["intel_id"]} da {s["name"]}', 'done': False,
            })
            pool = [x for x in pool if x is not s]
        for _ in range(min(3 if not gov_pool else 2, len(pool))):
            if not pool:
                break
            s = random.choice(pool)
            pool.remove(s)
            t = random.choice(['hack', 'crack', 'transfer'])
            if t == 'hack':
                self.missions.append({
                    'type': 'hack', 'target': s['name'],
                    'reward': s['money'] // 2 + 100,
                    'desc': f'Hack {s["name"]}', 'done': False,
                })
            elif t == 'crack':
                p = random.choice(s['ports'])
                self.missions.append({
                    'type': 'crack', 'target': s['name'], 'port': p,
                    'reward': 150,
                    'desc': f'Crack {s["name"]}:{p}', 'done': False,
                })
            else:
                self.missions.append({
                    'type': 'transfer', 'target': s['name'],
                    'amount': s['money'] // 2, 'reward': 100,
                    'desc': f'Transfer ${s["money"] // 2} da {s["name"]}',
                    'done': False,
                })

    def check_missions(self):
        for m in self.missions:
            if m['done']:
                continue
            if m['type'] == 'hack' and self.server(m['target']) and self.hacked(self.server(m['target'])):
                m['done'] = True
                self.money += m['reward']
                self.score += m['reward'] * 2
                self.add_log(_fmt('Mission: {} (+${})', m["desc"], m["reward"]), 'ok')
                self.add_news(_('Contract completed: {t}'), t=m['desc'])
            elif m['type'] == 'crack' and self.server(m['target']):
                s = self.server(m['target'])
                if s['cracked'].get(m['port']):
                    m['done'] = True
                    self.money += m['reward']
                    self.score += m['reward'] * 2
                    self.add_log(_fmt('Mission: {} (+${})', m["desc"], m["reward"]), 'ok')
                    self.add_news(_('Contract completed: {t}'), t=m['desc'])
            elif m['type'] == 'intel':
                for ii in self.gov_intel:
                    if ii.get('server_name') == m['target']:
                        m['done'] = True
                        self.money += m['reward']
                        self.score += m['reward'] * 2
                        self.add_log(_fmt('Mission: {} (+${})', m["desc"], m["reward"]), 'ok')
                        self.add_news(_('Contract completed: {t}'), t=m['desc'])
                        break

    # ── Story missions ──

    def check_story_missions(self, action, **kw):
        if self.story_active >= len(STORY_MISSIONS):
            return
        sm = STORY_MISSIONS[self.story_active]
        if self.level < sm['lvl']:
            return
        done = False
        if sm['obj_type'] == 'download' and action == 'download':
            done = any(f['name'] == sm['obj_file'] for f in self.local_files)
        elif sm['obj_type'] == 'bounce' and action == 'bounce':
            done = len(self.bounce_chain) >= sm['obj_count']
        elif sm['obj_type'] == 'login' and action == 'login':
            done = True
        elif sm['obj_type'] == 'combine' and action == 'combine':
            done = True
        elif sm['obj_type'] == 'gsm_transfer' and action == 'gsm':
            done = True
        elif sm['obj_type'] == 'levin_heist' and action == 'transfer' and self.money >= 10000:
            done = len(self.bounce_chain) >= sm['obj_count']
            if done and self.money >= 10000:
                done = True
        elif sm['obj_type'] == 'mckinnon_intel' and action == 'sell_intel':
            done = True
        elif sm['obj_type'] == 'download_multi' and action == 'download':
            done = self.stats.get('download_count', 0) >= sm['obj_count']
        elif sm['obj_type'] == 'lamp_upload' and action == 'upload':
            done = True
        elif sm['obj_type'] == 'anon_rising' and action == 'crack':
            ngov = sum(1 for s in self.servers if s.get('is_gov') and self.hacked(s))
            total_bounces = g.stats.get('bounces', 0)
            done = ngov >= 1 and total_bounces >= 6
        if done:
            self.story_progress[sm['id']] = True
            self.money += sm['reward']
            self.score += sm['reward'] * 2
            self.add_log(_fmt('📜 STORY: {} completed! (+${})', sm["name"], sm["reward"]), 'ok')
            self.add_news(_('Hacker Legend: {n} — mission accomplished!'), n=sm['name'])
            self.story_active += 1
            self.notify(f'📜 {sm["name"]} — ${sm["reward"]}')
            if self.story_active < len(STORY_MISSIONS):
                self.add_log(_fmt('Next mission: {}', STORY_MISSIONS[self.story_active]["name"]), 'info')
            else:
                self.add_log(_('🏆 ALL LEGENDS COMPLETED! You are a true hacking icon!'), 'ok')
                self.money += 50000
                self.score += 100000
                self.notify('🏆 LEGEND COMPLETE! +$50,000')

    def notify(self, text, color='cyan'):
        """Placeholder: UI registers its own notify handler."""
        if hasattr(self, '_notify_cb') and self._notify_cb:
            self._notify_cb(text, color)

    # ── Crypto ──

    def crypto_tick(self):
        for c in self.crypto:
            self.crypto[c]['price'] = max(
                1, int(self.crypto[c]['price'] * (0.85 + random.random() * 0.3))
            )

    # ── Hackback ──

    def hackback(self):
        if self.hackback_cooldown > 0:
            self.hackback_cooldown -= 1
            return None
        if self.trace_level > 30 and random.random() < 0.15:
            self.hackback_cooldown = 5
            loss = min(self.money, int(100 + random.random() * self.level * 50))
            self.money -= loss
            msg = _fmt('HACKBACK! An enemy server stole ${}', loss)
            if self.local_files and random.random() < 0.3:
                idx = random.randint(0, len(self.local_files) - 1)
                gone = self.local_files.pop(idx) if self.local_files else None
                if gone:
                    msg += _fmt(' and deleted "{}"', gone["name"])
                return msg
            return _fmt('HACKBACK! An enemy server withdrew ${}!', loss)
        return None

    # ── Black market ──

    def gen_black_market(self):
        items = []
        for _ in range(random.randint(3, 5)):
            t = random.choice(['exploit', 'fake_ip', 'scanner', 'decrypt_tool', 'worm'])
            costs = {
                'exploit': 300, 'fake_ip': 200, 'scanner': 150,
                'decrypt_tool': 400, 'worm': 600,
            }
            descs = {
                'exploit': _('Zero-day exploit (instant crack)'),
                'fake_ip': _('Fake IP (-5% trace on actions)'),
                'scanner': _('Advanced scanner (finds all ports)'),
                'decrypt_tool': _('Instant decryption'),
                'worm': _('Auto-spreading worm (automatic hack)'),
            }
            items.append({
                'type': t, 'name': t.replace('_', ' ').title(),
                'cost': costs[t] * self.level, 'desc': descs[t],
            })
        items.append({
            'type': 'burner_phone',
            'name': _('GSM Burner Phone'),
            'cost': 200 * self.level,
            'desc': _('Encrypted anonymous phone (-30% trace on next action)'),
        })
        self.black_market_items = items

    # ── Skills ──

    def skill_cost(self, s):
        costs = {
            'stealth': [1, 2, 3, 5, 8],
            'brute': [1, 2, 3, 5, 8],
            'phish': [1, 2, 3, 5, 8],
            'crypto_bonus': [2, 3, 5],
            'trace_reduce': [2, 4, 6],
        }
        l = self.skills.get(s, 0)
        cc = costs.get(s, [1] * 5)
        return cc[l] if l < len(cc) else None

    def skill_effect(self):
        return {
            'stealth': 0.1 * self.skills['stealth'],
            'brute': 1 + 0.2 * self.skills['brute'],
            'phish': self.skills['phish'] > 0,
            'crypto_bonus': 1 + 0.3 * self.skills['crypto_bonus'],
            'trace_reduce': 0.05 * self.skills['trace_reduce'],
        }

    # ── Darknet / Exploit helpers ──

    def has_exploit(self, eid):
        """Check if player owns a specific exploit by ID."""
        return eid in self.exploits

    def buy_exploit(self, eid):
        """Add an exploit to inventory. Returns the exploit dict or None."""
        for ex in EXPLOITS:
            if ex['id'] == eid:
                if self.money < ex['cost'] or eid in self.exploits:
                    return None
                self.money -= ex['cost']
                self.exploits.append(eid)
                return ex
        return None

    def get_exploits_purchasable(self):
        """Return list of exploits the player can afford and doesn't own."""
        return [ex for ex in EXPLOITS
                if ex['id'] not in self.exploits and self.money >= ex['cost']]

    def get_exploits_owned(self):
        """Return list of exploit dicts the player owns."""
        return [ex for ex in EXPLOITS if ex['id'] in self.exploits]

    # ── Sentinel AI (Ghost in the Machine) ──

    def sentinel_tick(self):
        """Advance the Sentinel FSM by one tick (called on player actions).
        
        States:
          DORMANT   → no threat detected
          ANALYZING → suspicious activity, scanning countermeasures
          ACTIVE    → actively attacking: closing ports, deleting files
        
        Transitions are driven by trace_level and player actions.
        """
        # Cooldown expired?
        if self.sentinel_cooldown > 0:
            self.sentinel_cooldown -= 1
            if self.sentinel_cooldown <= 0 and self.sentinel_state == 'DORMANT':
                # Done cooling down, but stays dormant
                pass

        # If player has firewall_bypass, sentinel is suppressed
        if self.has_exploit('firewall_bypass'):
            if self.sentinel_state == 'ACTIVE':
                self.add_log(_('[SENTINEL] Firewall bypass active — countermeasures suppressed.'), 'info')
            return  # no sentinel activity while bypass active

        if self.sentinel_state == 'DORMANT':
            # Transition to ANALYZING when trace > 30 or on suspicious actions
            if self.trace_level > 30 or self.sentinel_timer > 5:
                self.sentinel_state = 'ANALYZING'
                self.sentinel_timer = 0
                self.add_log(_('[SENTINEL] Unusual network activity detected. Entering analysis mode.'), 'yellow')
                self.add_log(_fmt('[SENTINEL] Trace signature: {}%', self.trace_level), 'dim')
                self.add_news('⚠ Sentinel AI is analyzing your traffic.')
                if self._notify_cb:
                    self._notify_cb(_('SENTINEL analyzing...'), 'yellow')
            else:
                self.sentinel_timer += 1

        elif self.sentinel_state == 'ANALYZING':
            # Accumulate timer — after enough ticks or high trace → ACTIVE
            self.sentinel_timer += 1
            if self.trace_level > 60 or self.sentinel_timer > 8:
                self.sentinel_state = 'ACTIVE'
                self.sentinel_timer = 0
                self.sentinel_strikes += 1
                self.add_log(_('[SENTINEL] ⚠ INTRUSION CONFIRMED. Activating countermeasures.'), 'red')
                self.add_log(_('[SENTINEL] Locking ports and removing unauthorized files.'), 'red')
                self.add_news('🚨 SENTINEL IS ACTIVE! Countermeasures deployed!')
                if self._notify_cb:
                    self._notify_cb(_('🚨 SENTINEL ACTIVE!'), 'red')
                return 'sentinel_active'
            # Still analyzing — random checks
            if random.random() < 0.25 and self.trace_level > 40:
                self.add_log(_('[SENTINEL] Scanning for known exploit signatures...'), 'dim')

        elif self.sentinel_state == 'ACTIVE':
            # Active attack: close ports, delete files, increase trace
            self.sentinel_timer += 1

            # Every 3-4 ticks, do something nasty
            if self.sentinel_timer % 3 == 0:
                self._sentinel_strike()

            # Transition back to dormant after enough actions or if trace drops
            if self.trace_level < 15 and self.sentinel_timer > 6:
                self.sentinel_state = 'DORMANT'
                self.sentinel_timer = 0
                self.sentinel_cooldown = 15
                self.add_log(_('[SENTINEL] Threat neutralized. Returning to dormant state.'), 'green')
                self.add_news('✅ Sentinel back to dormant.')
                if self._notify_cb:
                    self._notify_cb(_('Sentinel dormant.'), 'green')

            # If trace hits 0, sentinel loses track
            if self.trace_level <= 0:
                self.sentinel_state = 'DORMANT'
                self.sentinel_timer = 0
                self.sentinel_cooldown = 10
                self.add_log(_('[SENTINEL] Target lost. Resetting countermeasures.'), 'dim')

        return None

    def _sentinel_strike(self):
        """Execute a Sentinel countermeasure."""
        strikes = [
            self._sentinel_close_ports,
            self._sentinel_delete_files,
            self._sentinel_increase_trace,
        ]
        action = random.choice(strikes)
        action()

    def _sentinel_close_ports(self):
        """Close a random cracked port on the current server."""
        if self.current_server and self.hacked(self.current_server):
            # Find a port that's been cracked
            cracked_ports = [p for p in self.current_server.get('cracked', {})
                             if self.current_server['cracked'].get(p)]
            if cracked_ports:
                target = random.choice(cracked_ports)
                self.current_server['cracked'][target] = False
                sn = self.current_server['name']
                if sn not in self.ports_closed:
                    self.ports_closed[sn] = []
                self.ports_closed[sn].append(target)
                self.add_log(
                    _fmt('[SENTINEL] Port {} closed on {} by firewall.', target, sn),
                    'red'
                )
                self.add_news('Sentinel closed port {p} on {h}!', p=target, h=sn)
                if self._notify_cb:
                    self._notify_cb(_fmt('🚪 Port {} closed by Sentinel!', target), 'red')

    def _sentinel_delete_files(self):
        """Delete a random downloaded file from local storage."""
        if self.local_files:
            idx = random.randint(0, len(self.local_files) - 1)
            gone = self.local_files.pop(idx)
            self.add_log(
                _fmt('[SENTINEL] File "{}" has been remotely deleted.', gone["name"]),
                'red'
            )
            self.add_news('Sentinel deleted {f}!', f=gone['name'])
            if self._notify_cb:
                self._notify_cb(_fmt('📁 "{}" deleted by Sentinel!', gone['name']), 'red')

    def _sentinel_increase_trace(self):
        """Jump trace level as a punishment."""
        jump = random.uniform(5, 15)
        self.trace_level = min(100, self.trace_level + jump)
        self.max_trace = max(self.max_trace, self.trace_level)
        self.add_log(
            _fmt('[SENTINEL] Trace signal amplified! +{:.0f}%', jump),
            'red'
        )
        self.add_news('Sentinel amplified trace signal!')

    def sentinel_hacked_server(self, s):
        """Check if Sentinel has closed ports on this server, making it
        no longer fully hacked."""
        if s['name'] in self.ports_closed:
            closed = self.ports_closed[s['name']]
            # Check if any key port is closed
            for p in closed:
                if s['cracked'].get(p) == False:
                    return False
        return True

    # ── Random events ──

    RANDOM_EVENTS = [
        "[SYSTEM] Maintenance window: 5 minutes. Some services may restart.",
        "[NET] Unusual traffic spike from IP {ip4}",
        "[SEC] Firewall signature updated. 12 new rules deployed.",
        "[SYS] Background scan: {n} files checked, {n2} threats found.",
        "[NET] Connection timeout on upstream router (hop {h}).",
        "[SEC] Brute-force attempt detected on secondary server.",
        "[SYS] Kernel module nf_conntrack updated.",
        "[NET] Routing table recalculated. Latency: {ms}ms.",
        "[SEC] Intrusion detection system: pattern update #{n}.",
        "[SYS] Log rotation complete. {n} archives purged.",
        "[NET] Bandwidth throttling detected on port {p}.",
    ]
    EVENT_COLORS = ['yellow', 'orange', 'red', 'dim', 'orange', 'red',
                    'dim', 'orange', 'red', 'dim', 'orange']

    def random_event(self):
        """Generate a random system event message."""
        if self.event_paused:
            return None
        idx = random.randrange(len(self.RANDOM_EVENTS))
        template = self.RANDOM_EVENTS[idx]
        color = self.EVENT_COLORS[idx]
        r4 = lambda: random.randint(1, 254)
        rn = lambda: random.randint(10, 9999)
        text = template.format(
            ip4=f'{r4()}.{r4()}.{r4()}.{r4()}',
            n=rn(), n2=rn() + random.randint(1, 100),
            h=random.randint(1, 24),
            ms=random.randint(10, 500),
            p=random.randint(1, 65535),
        )
        return text, color, random.uniform(0.3, 0.8)

    # ── Save / Load ──

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if k != 'running'}

    def from_dict(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    def save(self, p=SAVE_FILE):
        try:
            d = dict(self.__dict__)
            d['log'] = d['log'][:100]
            with open(p, 'w') as f:
                json.dump(d, f, indent=2)
            return True
        except Exception:
            return False

    def load(self, p=SAVE_FILE):
        try:
            with open(p) as f:
                d = json.load(f)
            for k, v in d.items():
                setattr(self, k, v)
            return True
        except Exception:
            return False


# ═══════════════════════════════════════════════════════════════════════════════
# Services container
# ═══════════════════════════════════════════════════════════════════════════════

class Services:
    """Container for all Phase 3 services. Wraps Game state without duplicating it."""

    def __init__(self, game: Game):
        self.game = game
        self.economy = EconomyService(
            get_money=lambda: game.money,
            set_money=lambda v: setattr(game, 'money', v),
            get_money_max=lambda: game.money if hasattr(game, 'money') else 10_000_000,
        )
        self.network = NetworkService(
            get_server=game.server,
            get_all_servers=lambda: game.servers,
        )
        self.trace = TraceService(
            get_trace=lambda: game.trace_level,
            set_trace=lambda v: setattr(game, 'trace_level', v),
        )
        self.missions = MissionService(
            get_missions=lambda: game.missions,
            set_missions=lambda ms: setattr(game, 'missions', ms),
            add_log=game.add_log,
            add_news=game.add_news,
        )
        # SentinelFSM — wraps game's existing sentinel logic
        sentinel_fsm = SentinelFSM(
            get_trace=lambda: game.trace_level,
            get_current_server=lambda: game.current_server,
            get_local_files=lambda: game.local_files,
            add_log=game.add_log,
            add_news=game.add_news,
            notify=game.notify,
            has_exploit=game.has_exploit,
        )
        self.sentinel = SentinelService(sentinel_fsm)


# ── Global game instance ──
g = Game()
