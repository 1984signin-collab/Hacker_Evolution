#!/usr/bin/env python3
"""HACKER EVOLUTION — Trace Service (Phase 3: Domain).

Trace/suspicion level management.
"""

from __future__ import annotations

from typing import Callable

from . import DomainEvent, DomainEventType, EventBus


class TraceService:
    """Manages player trace (suspicion) level."""

    MAX_TRACE = 100.0

    def __init__(self, get_trace: Callable[[], float],
                 set_trace: Callable[[float], None],
                 get_trace_gain: Callable[[], float] | None = None):
        self._get_trace = get_trace
        self._set_trace = set_trace
        self._get_trace_gain = get_trace_gain
        self._bus = EventBus()

    @property
    def level(self) -> float:
        return self._get_trace()

    def add_trace(self, amount: float) -> dict:
        multiplier = self._get_trace_gain() if self._get_trace_gain else 1.0
        actual = amount * multiplier
        new_trace = min(self._get_trace() + actual, self.MAX_TRACE)
        self._set_trace(new_trace)

        self._bus.publish(DomainEvent(
            DomainEventType.TRACE, 'increased',
            {'amount': actual, 'total': new_trace}
        ))

        if new_trace >= self.MAX_TRACE:
            return {'success': False, 'msg': 'TRACE MAX — GAME OVER', 'trace': new_trace}
        return {'success': True, 'msg': f'Trace +{actual:.0f}% (total: {new_trace:.0f}%)', 'trace': new_trace}

    def reduce_trace(self, amount: float) -> dict:
        new_trace = max(0, self._get_trace() - amount)
        self._set_trace(new_trace)

        self._bus.publish(DomainEvent(
            DomainEventType.TRACE, 'reduced',
            {'amount': amount, 'total': new_trace}
        ))
        return {'success': True, 'msg': f'Trace -{amount:.0f}% (total: {new_trace:.0f}%)', 'trace': new_trace}

    def reset(self):
        self._set_trace(0)

    def check_state(self) -> dict:
        t = self._get_trace()
        state = 'safe'
        if t > 75:
            state = 'critical'
        elif t > 50:
            state = 'danger'
        elif t > 25:
            state = 'warning'
        return {'trace': t, 'state': state, 'max': self.MAX_TRACE}
