#!/usr/bin/env python3
"""HACKER EVOLUTION — Mission Service (Phase 3: Domain).

Mission lifecycle: progress checking, completion, generation.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from . import DomainEvent, DomainEventType, EventBus


class MissionService:
    """Manages mission lifecycle — delegate for the game's mission logic."""

    def __init__(self, get_missions: Callable[[], list[dict]],
                 set_missions: Callable[[list[dict]], None],
                 add_log: Callable[[str, str], None],
                 add_news: Callable[[str], None],
                 add_money: Callable[[float], None] | None = None):
        self._get_missions = get_missions
        self._set_missions = set_missions
        self._add_log = add_log
        self._add_news = add_news
        self._add_money = add_money
        self._bus = EventBus()

    def check_progress(self, obj_type: str, target: str = '',
                       amount: int = 0, port: int = 0,
                       obj_file: str = '', obj_count: int = 0) -> list[dict]:
        """Check active missions for progress against a player action.

        Returns updated mission list.
        """
        missions = self._get_missions()
        updated = False
        completed: list[dict] = []

        for m in missions:
            if m.get('done', False):
                continue

            # Match by objective type
            if m.get('obj_type') != obj_type:
                continue

            # Match target if specified
            if target and m.get('target') and m['target'] != target:
                continue

            # Download missions: check file match
            if obj_type == 'download' and obj_file:
                if m.get('obj_file') == obj_file:
                    m['done'] = True
                    updated = True
                    completed.append(m)
                elif m.get('obj_file') == 'any':
                    # Any file download counts — track count
                    prog = m.setdefault('progress', 0) + 1
                    m['progress'] = prog
                    if prog >= obj_count:
                        m['done'] = True
                        completed.append(m)
                    updated = True
                continue

            # Hack missions: match port
            if obj_type == 'hack' and port:
                if m.get('port') == port or m.get('obj_type') == 'hack':
                    m['done'] = True
                    updated = True
                    completed.append(m)
                continue

            # Generic completion
            m['done'] = True
            updated = True
            completed.append(m)

        if updated:
            self._set_missions(missions)

        for m in completed:
            reward = m.get('reward', 0)
            self._add_log(f'[MISSION] "{m.get("name", "?")}" completed! +${reward}', 'green')
            self._add_news(f'Mission complete: {m.get("name", "?")}!')
            if self._add_money and reward:
                self._add_money(float(reward))
            self._bus.publish(DomainEvent(
                DomainEventType.MISSION, 'completed',
                {'name': m.get('name', '?'), 'reward': reward}
            ))

        return completed

    def complete(self, mission_id: str) -> dict | None:
        """Force-complete a specific mission by id."""
        missions = self._get_missions()
        for m in missions:
            if m.get('id') == mission_id and not m.get('done', False):
                m['done'] = True
                self._set_missions(missions)
                self._bus.publish(DomainEvent(
                    DomainEventType.MISSION, 'completed',
                    {'name': m.get('name', '?'), 'id': mission_id}
                ))
                return m
        return None

    def generate_new(self, template: dict) -> dict:
        """Generate a new mission from a template dict."""
        mission = dict(template)
        mission['done'] = False
        mission['progress'] = 0
        # Fill defaults
        mission.setdefault('obj_type', 'hack')
        mission.setdefault('reward', 100)
        # Ensure unique-ish id
        if not mission.get('id'):
            mission['id'] = f'mission_{random.randint(10000, 99999)}'
        return mission
