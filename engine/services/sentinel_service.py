#!/usr/bin/env python3
"""HACKER EVOLUTION — Sentinel Service (Phase 3: Domain).

Wraps the SentinelFSM for integration with the game layer.
"""

from __future__ import annotations

from typing import Any, Callable

from engine.sentinel import SentinelFSM, SentinelEvent
from . import DomainEvent, DomainEventType, EventBus


class SentinelService:
    """Service wrapper around SentinelFSM for game integration."""

    def __init__(self, fsm: SentinelFSM):
        self._fsm = fsm
        self._bus = EventBus()

    def tick(self) -> str | None:
        """Advance the sentinel FSM.

        Returns event string if transition occurred.
        """
        result = self._fsm.tick()
        self._bus.publish(DomainEvent(
            DomainEventType.SENTINEL, 'tick',
            {'state': self._fsm.state.value}
        ))
        return result

    def reset(self):
        """Reset sentinel to dormant."""
        self._fsm.state = self._fsm.state.DORMANT
        self._fsm.timer = 0
        self._fsm.cooldown = 0

    def is_hacked(self, server: dict) -> bool:
        return self._fsm.is_hacked(server)

    @property
    def state(self):
        return self._fsm.state

    @property
    def strikes(self) -> int:
        return self._fsm.strikes

    @property
    def cooldown(self) -> int:
        return self._fsm.cooldown

    # Delegate to FSM's event system
    def on_sentinel_event(self, event_type: str,
                          callback: Callable[[SentinelEvent], None]):
        self._fsm.on(event_type, callback)

    def to_dict(self) -> dict:
        return self._fsm.to_dict()

    def from_dict(self, d: dict):
        self._fsm.from_dict(d)
