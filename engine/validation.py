#!/usr/bin/env python3
"""HACKER EVOLUTION — Content validation (Phase 1: Hardening).

Validates all JSON-loaded content at startup. Reports errors without crashing.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Optional


class ValidationError(Exception):
    """A content validation error. Doesn't crash the game — just logs."""


class ContentValidator:
    """Centralized validator for all game content loaded from JSON files."""

    def __init__(self, silent: bool = False):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.silent = silent

    def report(self) -> bool:
        """Print all accumulated errors/warnings. Returns True if any errors."""
        for err in self.errors:
            print(f'[VALIDATION ERROR] {err}', file=sys.stderr)
        for warn in self.warnings:
            print(f'[VALIDATION WARN] {warn}', file=sys.stderr)
        return len(self.errors) > 0

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    # ── Server pool ──

    def validate_server_pool(self, pool: list) -> list:
        """Validate and return server pool. Filters out invalid entries."""
        valid = []
        for i, s in enumerate(pool):
            if not isinstance(s, (list, tuple)) or len(s) < 6:
                self.error(f'Servers[{i}]: expected list of 6+ elements, got {type(s).__name__}')
                continue
            name = s[0]
            if not isinstance(name, str) or not name.strip():
                self.error(f'Servers[{i}]: name must be non-empty string')
                continue
            ports = s[1]
            if not isinstance(ports, list) or not all(isinstance(p, int) for p in ports):
                self.error(f'Servers[{i}] ({name}): ports must be list of ints')
                continue
            key_bits = s[2]
            if not isinstance(key_bits, int) or key_bits < 128:
                self.warn(f'Servers[{i}] ({name}): key_bits < 128 ({key_bits})')
            files = s[3]
            if not isinstance(files, list):
                self.error(f'Servers[{i}] ({name}): files must be list')
                continue
            for j, f in enumerate(files):
                if not isinstance(f, (list, tuple)) or len(f) < 2:
                    self.error(f'Servers[{i}] ({name}): files[{j}] must be [name, content]')
            money = s[4]
            if not isinstance(money, (int, float)):
                self.warn(f'Servers[{i}] ({name}): money not a number')
            desc = s[5]
            if not isinstance(desc, str):
                self.warn(f'Servers[{i}] ({name}): desc must be string')
            valid.append(s)
        return valid

    # ── Hardware ──

    def validate_hardware(self, items: list) -> list:
        valid = []
        for i, h in enumerate(items):
            if not isinstance(h, (list, tuple)) or len(h) < 6:
                self.error(f'Hardware[{i}]: expected list of 6 elements')
                continue
            if not isinstance(h[3], (int, float)) or h[3] < 0:
                self.error(f'Hardware[{i}] ({h[0]}): base_cost must be positive number')
                continue
            if not isinstance(h[5], int) or h[5] < 1:
                self.error(f'Hardware[{i}] ({h[0]}): max_level must be int >= 1')
                continue
            valid.append(h)
        return valid

    # ── Exploits ──

    def validate_exploits(self, exploits: list) -> list:
        valid = []
        seen_ids = set()
        for i, ex in enumerate(exploits):
            if not isinstance(ex, dict):
                self.error(f'Exploits[{i}]: expected dict')
                continue
            eid = ex.get('id', '')
            if not eid:
                self.error(f'Exploits[{i}]: missing id')
                continue
            if eid in seen_ids:
                self.error(f'Exploits[{i}] ({eid}): duplicate id')
                continue
            seen_ids.add(eid)
            if not isinstance(ex.get('name'), str):
                self.error(f'Exploits[{i}] ({eid}): missing name')
                continue
            cost = ex.get('cost', 0)
            if not isinstance(cost, int) or cost < 0:
                self.error(f'Exploits[{i}] ({eid}): cost must be positive int')
                continue
            valid.append(ex)
        return valid

    # ── Story missions ──

    def validate_story_missions(self, missions: list) -> list:
        valid = []
        seen_ids = set()
        for i, m in enumerate(missions):
            if not isinstance(m, dict):
                self.error(f'Missions[{i}]: expected dict')
                continue
            mid = m.get('id', '')
            if not mid:
                self.error(f'Missions[{i}]: missing id')
                continue
            if mid in seen_ids:
                self.error(f'Missions[{i}] ({mid}): duplicate id')
                continue
            seen_ids.add(mid)
            if not isinstance(m.get('name'), str):
                self.error(f'Missions[{i}] ({mid}): missing name')
                continue
            valid_otypes = {
                'download', 'login', 'bounce', 'combine', 'gsm_transfer',
                'levin_heist', 'mckinnon_intel', 'download_multi',
                'lamp_upload', 'anon_rising',
            }
            otype = m.get('obj_type', '')
            if otype not in valid_otypes:
                self.warn(f'Missions[{i}] ({mid}): unknown obj_type "{otype}"')
            if otype in ('download',) and not m.get('obj_file'):
                self.warn(f'Missions[{i}] ({mid}): download type needs obj_file')
            valid.append(m)
        return valid

    # ── Emails ──

    def validate_emails(self, emails: list) -> list:
        valid = []
        for i, e in enumerate(emails):
            if not isinstance(e, dict):
                self.error(f'Emails[{i}]: expected dict')
                continue
            if not isinstance(e.get('sub'), str):
                self.error(f'Emails[{i}]: missing sub')
                continue
            if not isinstance(e.get('body'), str):
                self.error(f'Emails[{i}]: missing body')
                continue
            valid.append(e)
        return valid

    # ── Gov intel ──

    def validate_gov_intel(self, gov: dict) -> dict:
        if not isinstance(gov, dict):
            self.error('gov_intel.json: expected dict with "types" and "domains"')
            return {'types': [], 'domains': []}
        types = gov.get('types', [])
        for i, t in enumerate(types):
            if not isinstance(t, (list, tuple)) or len(t) < 4:
                self.error(f'gov_intel types[{i}]: expected [id, desc, value, size]')
        domains = gov.get('domains', [])
        if not isinstance(domains, list):
            self.error('gov_intel domains: must be list')
        return gov
