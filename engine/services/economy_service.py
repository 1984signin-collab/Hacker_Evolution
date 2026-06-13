#!/usr/bin/env python3
"""HACKER EVOLUTION — Economy Service (Phase 3: Domain).

Money management, purchase validation, crypto market simulation.
"""

from __future__ import annotations

import random
from typing import Callable

from . import DomainEvent, DomainEventType, EventBus


class EconomyService:
    """Encapsulates economy/game-money operations."""

    def __init__(self, get_money: Callable[[], float],
                 set_money: Callable[[float], None],
                 get_money_max: Callable[[], float] | None = None):
        self._get_money = get_money
        self._set_money = set_money
        self._get_money_max = get_money_max
        self._bus = EventBus()

    @property
    def balance(self) -> float:
        return self._get_money()

    def can_afford(self, amount: float) -> bool:
        return self._get_money() >= amount

    def transfer(self, amount: float, from_player: bool = True) -> dict:
        """Transfer money to/from player. Returns {'success': bool, 'msg': str}."""
        if from_player:
            if not self.can_afford(amount):
                return {'success': False, 'msg': f'Need ${amount:,.0f}, have ${self._get_money():,.0f}.'}
            self._set_money(self._get_money() - amount)
        else:
            max_money = self._get_money_max() if self._get_money_max else float('inf')
            new_balance = min(self._get_money() + amount, max_money)
            self._set_money(new_balance)

        direction = 'spend' if from_player else 'earn'
        self._bus.publish(DomainEvent(
            DomainEventType.ECONOMY, 'transfer',
            {'amount': amount, 'direction': direction, 'balance': self._get_money()}
        ))
        return {'success': True, 'msg': f'${amount:,.0f} {"spent" if from_player else "received"}. Balance: ${self._get_money():,.0f}.'}

    def add_money(self, amount: float) -> dict:
        return self.transfer(amount, from_player=False)

    def remove_money(self, amount: float) -> dict:
        return self.transfer(amount, from_player=True)

    def simulate_crypto_market(self) -> dict:
        """Simple crypto tick — returns price movement info."""
        btc = 45000 + random.gauss(0, 500)
        eth = 2800 + random.gauss(0, 80)
        doge = 0.12 + random.gauss(0, 0.01)

        self._bus.publish(DomainEvent(
            DomainEventType.ECONOMY, 'crypto_tick',
            {'btc': round(btc, 2), 'eth': round(eth, 2), 'doge': round(doge, 4)}
        ))
        return {'btc': round(btc, 2), 'eth': round(eth, 2), 'doge': round(doge, 4)}
