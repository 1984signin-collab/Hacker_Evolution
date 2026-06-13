#!/usr/bin/env python3
"""HACKER EVOLUTION — Sentinel AI FSM (Phase 4: FSM & Events).

A dedicated Finite State Machine for the adversarial AI.
States: DORMANT → ANALYZING → ACTIVE
Emits domain events for the UI layer to consume.
"""

from __future__ import annotations

import random
from enum import Enum
from typing import Any, Callable, Optional


class SentinelState(Enum):
    DORMANT = 'DORMANT'
    ANALYZING = 'ANALYZING'
    ACTIVE = 'ACTIVE'


# ── Domain events ──

class SentinelEvent:
    """Base class for sentinel domain events."""
    def __init__(self, event_type: str, data: dict | None = None):
        self.event_type = event_type
        self.data = data or {}


# ── Sentinel FSM ──

class SentinelFSM:
    """Finite State Machine for the Sentinel anti-intrusion AI.

    The Sentinel monitors player actions (via tick()) and progresses
    through states based on trace level and action count. In ACTIVE
    state it performs counter-strikes.

    The FSM is observable — it emits events that the UI layer can
    subscribe to via notify().
    """

    def __init__(self, get_trace: Callable[[], float],
                 get_current_server: Callable[[], Any | None],
                 get_local_files: Callable[[], list],
                 add_log: Callable[[str, str], None],
                 add_news: Callable[[str], None],
                 notify: Callable[[str, str], None] | None = None,
                 has_exploit: Callable[[str], bool] | None = None):
        self.state = SentinelState.DORMANT
        self.timer = 0
        self.cooldown = 0
        self.strikes = 0
        self.ports_closed: dict[str, list[int]] = {}

        # Dependencies (injected for testability)
        self._get_trace = get_trace
        self._get_current_server = get_current_server
        self._get_local_files = get_local_files
        self._add_log = add_log
        self._add_news = add_news
        self._notify = notify or (lambda t, c: None)
        self._has_exploit = has_exploit or (lambda e: False)

        # Event listeners
        self._event_listeners: dict[str, list[Callable]] = {}

    def on(self, event_type: str, callback: Callable):
        """Subscribe to a domain event."""
        self._event_listeners.setdefault(event_type, []).append(callback)

    def _emit(self, event_type: str, data: dict | None = None):
        """Emit a domain event to all listeners."""
        ev = SentinelEvent(event_type, data)
        for cb in self._event_listeners.get(event_type, []):
            try:
                cb(ev)
            except Exception:
                pass

    # ── FSM logic ──

    def tick(self) -> str | None:
        """Advance the FSM by one tick. Call after each player command.

        Returns:
            'sentinel_active' when transitioning to ACTIVE, None otherwise.
        """
        trace = self._get_trace()

        # Cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Firewall bypass suppresses sentinel
        if self._has_exploit('firewall_bypass'):
            if self.state == SentinelState.ACTIVE:
                self._add_log('[SENTINEL] Bypass active — countermeasures suppressed.', 'info')
            return None

        if self.state == SentinelState.DORMANT:
            return self._tick_dormant(trace)
        elif self.state == SentinelState.ANALYZING:
            return self._tick_analyzing(trace)
        elif self.state == SentinelState.ACTIVE:
            return self._tick_active(trace)
        return None

    def _tick_dormant(self, trace: float) -> str | None:
        if trace > 30 or self.timer > 5:
            self.state = SentinelState.ANALYZING
            self.timer = 0
            self._add_log('[SENTINEL] Unusual traffic detected. Entering analysis mode.', 'yellow')
            self._add_news('Sentinel AI is analyzing your traffic.')
            self._notify('SENTINEL analyzing...', 'yellow')
            self._emit('sentinel.state_changed', {'from': 'DORMANT', 'to': 'ANALYZING', 'trace': trace})
        else:
            self.timer += 1
        return None

    def _tick_analyzing(self, trace: float) -> str | None:
        self.timer += 1
        if trace > 60 or self.timer > 8:
            self.state = SentinelState.ACTIVE
            self.timer = 0
            self.strikes += 1
            self._add_log('[SENTINEL] INTRUSION CONFIRMED. Activating countermeasures.', 'red')
            self._add_news('SENTINEL IS ACTIVE! Countermeasures deployed!')
            self._notify('SENTINEL ACTIVE!', 'red')
            self._emit('sentinel.state_changed', {'from': 'ANALYZING', 'to': 'ACTIVE', 'trace': trace})
            return 'sentinel_active'
        if random.random() < 0.25 and trace > 40:
            self._add_log('[SENTINEL] Scanning for known exploit signatures...', 'dim')
        return None

    def _tick_active(self, trace: float) -> str | None:
        self.timer += 1

        # Strike every 3 ticks
        if self.timer % 3 == 0:
            self._strike()

        # De-escalate when trace drops
        if trace < 15 and self.timer > 6:
            self.state = SentinelState.DORMANT
            self.timer = 0
            self.cooldown = 15
            self._add_log('[SENTINEL] Threat neutralized. Returning to dormant.', 'green')
            self._add_news('Sentinel back to dormant.')
            self._notify('Sentinel dormant.', 'green')
            self._emit('sentinel.state_changed', {'from': 'ACTIVE', 'to': 'DORMANT', 'trace': trace})

        if trace <= 0:
            self.state = SentinelState.DORMANT
            self.timer = 0
            self.cooldown = 10
            self._add_log('[SENTINEL] Target lost. Resetting.', 'dim')

        return None

    # ── Counter-strikes ──

    def _strike(self):
        strikes = [
            self._close_ports,
            self._delete_files,
            self._amplify_trace,
        ]
        random.choice(strikes)()

    def _close_ports(self):
        server = self._get_current_server()
        if server is None:
            return
        cracked = {p: v for p, v in server.get('cracked', {}).items() if v}
        if not cracked:
            return
        target = random.choice(list(cracked.keys()))
        server['cracked'][target] = False
        sn = server.get('name', '?')
        self.ports_closed.setdefault(sn, []).append(target)
        msg = f'[SENTINEL] Port {target} closed on {sn}.'
        self._add_log(msg, 'red')
        self._add_news(f'Sentinel closed port {target} on {sn}!')
        self._notify(f'Port {target} closed by Sentinel!', 'red')
        self._emit('sentinel.port_closed', {'server': sn, 'port': target})

    def _delete_files(self):
        files = self._get_local_files()
        if not files:
            return
        idx = random.randint(0, len(files) - 1)
        gone = files.pop(idx)
        self._add_log(f'[SENTINEL] File "{gone["name"]}" remotely deleted.', 'red')
        self._add_news(f'Sentinel deleted {gone["name"]}!')
        self._notify(f'"{gone["name"]}" deleted by Sentinel!', 'red')
        self._emit('sentinel.file_deleted', {'file': gone['name']})

    def _amplify_trace(self):
        jump = random.uniform(5, 15)
        # Inject trace via the game's add_trace mechanism (handled externally)
        self._add_log(f'[SENTINEL] Trace signal amplified! +{jump:.0f}%', 'red')
        self._add_news('Sentinel amplified trace signal!')
        self._emit('sentinel.trace_amplified', {'amount': jump})

    # ── Queries ──

    def is_hacked(self, server: dict) -> bool:
        """Check if Sentinel has closed ports making a server no longer fully hacked."""
        sn = server.get('name', '')
        if sn in self.ports_closed:
            for p in self.ports_closed[sn]:
                if server.get('cracked', {}).get(p) == False:
                    return False
        return True

    def to_dict(self) -> dict:
        return {
            'state': self.state.value,
            'timer': self.timer,
            'cooldown': self.cooldown,
            'strikes': self.strikes,
            'ports_closed': self.ports_closed,
        }

    def from_dict(self, d: dict):
        self.state = SentinelState(d.get('state', 'DORMANT'))
        self.timer = d.get('timer', 0)
        self.cooldown = d.get('cooldown', 0)
        self.strikes = d.get('strikes', 0)
        self.ports_closed = d.get('ports_closed', {})
