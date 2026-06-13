#!/usr/bin/env python3
"""HACKER EVOLUTION — Service Layer (Phase 3: Domain).

Event-driven service architecture for decoupled game logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class DomainEventType(Enum):
    ECONOMY = 'economy'
    NETWORK = 'network'
    TRACE = 'trace'
    MISSION = 'mission'
    SENTINEL = 'sentinel'
    PLAYER = 'player'
    SYSTEM = 'system'


@dataclass
class DomainEvent:
    """A domain event with type, subtype, and optional payload."""
    type: DomainEventType
    subtype: str
    data: dict = field(default_factory=dict)


# Type alias for event handlers
EventHandler = Callable[[DomainEvent], None]


class EventBus:
    """Simple pub/sub event bus. Singleton.

    Decouples engine services from the UI layer.
    Services publish events; the game/app layer subscribes.
    """

    _instance: EventBus | None = None
    _subscribers: dict[str, list[EventHandler]]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance

    def subscribe(self, event_key: str, handler: EventHandler):
        """Subscribe to an event by key like 'economy.transfer' or '*' for all."""
        self._subscribers.setdefault(event_key, []).append(handler)

    def unsubscribe(self, event_key: str, handler: EventHandler):
        handlers = self._subscribers.get(event_key, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, event: DomainEvent):
        """Publish an event to matching subscribers."""
        # Exact match
        key = f'{event.type.value}.{event.subtype}'
        for handler in self._subscribers.get(key, []):
            try:
                handler(event)
            except Exception:
                import traceback
                traceback.print_exc()

        # Type-category match (e.g., 'economy.*')
        wildcard = f'{event.type.value}.*'
        for handler in self._subscribers.get(wildcard, []):
            try:
                handler(event)
            except Exception:
                import traceback
                traceback.print_exc()

        # Global wildcard
        for handler in self._subscribers.get('*', []):
            try:
                handler(event)
            except Exception:
                import traceback
                traceback.print_exc()

    @classmethod
    def reset(cls):
        """Clear all subscribers (useful for testing)."""
        if cls._instance:
            cls._instance._subscribers = {}
