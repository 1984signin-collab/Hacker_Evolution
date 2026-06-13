#!/usr/bin/env python3
"""HACKER EVOLUTION — Typed data models (Phase 1: Hardening).

Replaces bare dicts with dataclasses for all game content types.
Provides from_dict/to_dict for JSON serialization compatibility.
"""

from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field, fields
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# Server
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ServerFile:
    name: str
    content: str

    def to_dict(self) -> dict:
        return {'name': self.name, 'content': self.content}

    @classmethod
    def from_dict(cls, d: dict) -> ServerFile:
        return cls(name=d['name'], content=d['content'])


@dataclass
class Server:
    name: str
    ports: list[int]
    key_bits: int
    files: list[ServerFile]
    money: int
    desc: str
    links_raw: list[str] = field(default_factory=list)
    cracked: dict[int, bool] = field(default_factory=dict)
    decrypted: bool = False
    scanned: bool = False
    bounce_used: int = 0
    visited: bool = False
    pos: tuple[float, float] = (0.0, 0.0)
    is_gov: bool = False
    intel_stolen: bool = False
    links: list[Any] = field(default_factory=list)  # resolved at runtime
    visible: bool = False
    entry_point: bool = False
    # Gov intel (only for gov servers)
    intel_id: str = ''
    intel_desc: str = ''
    intel_value: int = 0
    intel_size: int = 0

    def to_dict(self) -> dict:
        d = {}
        for fld in fields(self):
            v = getattr(self, fld.name)
            if fld.name == 'files':
                d['files'] = [f.to_dict() for f in v]
            elif fld.name == 'links':
                d['links'] = [s.name for s in v if hasattr(s, 'name')]
            elif fld.name == 'pos':
                d['pos'] = list(v)
            else:
                d[fld.name] = v
        return d

    @classmethod
    def from_dict(cls, d: dict) -> Server:
        kwargs = dict(d)
        kwargs['files'] = [ServerFile.from_dict(f) for f in kwargs.pop('files', [])]
        kwargs['links'] = []  # resolved later
        if 'pos' in kwargs and isinstance(kwargs['pos'], (list, tuple)):
            kwargs['pos'] = (float(kwargs['pos'][0]), float(kwargs['pos'][1]))
        return cls(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# Mission
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Mission:
    id: str = ''
    name: str = ''
    lvl: int = 1
    desc: str = ''
    obj_type: str = 'hack'
    target: str = ''
    port: Optional[int] = None
    amount: int = 0
    obj_file: str = ''
    obj_count: int = 0
    reward: int = 100
    done: bool = False
    dialogue: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {fld.name: getattr(self, fld.name) for fld in fields(self)}

    @classmethod
    def from_dict(cls, d: dict) -> Mission:
        return cls(**{fld.name: d.get(fld.name, fld.default) for fld in fields(cls)})


# ═══════════════════════════════════════════════════════════════════════════════
# Story Mission (from data/missions/*.json)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class StoryMission:
    id: str
    name: str
    lvl: int
    desc: str
    obj_type: str
    obj_file: str = ''
    obj_count: int = 0
    reward: int = 0
    dialogue: list[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> StoryMission:
        return cls(**{fld.name: d.get(fld.name, fld.default) for fld in fields(cls)})


# ═══════════════════════════════════════════════════════════════════════════════
# Email
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Email:
    id: str = ''
    lvl: int = 1
    sub: str = ''
    body: str = ''

    @classmethod
    def from_dict(cls, d: dict) -> Email:
        return cls(**{fld.name: d.get(fld.name, fld.default) for fld in fields(cls)})


# ═══════════════════════════════════════════════════════════════════════════════
# Exploit (Darknet)
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Exploit:
    id: str
    name: str
    desc: str
    cost: int
    level: int = 1
    type: str = 'tool'
    effect: str = 'none'
    content: str = ''

    @classmethod
    def from_dict(cls, d: dict) -> Exploit:
        return cls(**{fld.name: d.get(fld.name, fld.default) for fld in fields(cls)})


# ═══════════════════════════════════════════════════════════════════════════════
# Hardware
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HardwareItem:
    name: str
    key: str
    desc: str
    base_cost: int
    cost_mult: float
    max_level: int

    @classmethod
    def from_list(cls, arr: list) -> HardwareItem:
        return cls(
            name=arr[0], key=arr[1], desc=arr[2],
            base_cost=arr[3], cost_mult=arr[4], max_level=arr[5],
        )

    def to_list(self) -> list:
        return [self.name, self.key, self.desc, self.base_cost, self.cost_mult, self.max_level]


# ═══════════════════════════════════════════════════════════════════════════════
# Intel
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class GovernmentIntel:
    id: str
    desc: str
    value: int
    size: int

    @classmethod
    def from_list(cls, arr: list) -> GovernmentIntel:
        return cls(id=arr[0], desc=arr[1], value=arr[2], size=arr[3])


# ═══════════════════════════════════════════════════════════════════════════════
# Achievement
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Achievement:
    id: str
    name: str
    desc: str
    reward: int
