#!/usr/bin/env python3
"""HACKER EVOLUTION — Network Service (Phase 3: Domain).

Handles scan, connect, neighbor resolution, reachability.
"""

from __future__ import annotations

import random
from typing import Any, Callable

from . import DomainEvent, DomainEventType, EventBus


class NetworkService:
    """Encapsulates network-related game operations."""

    def __init__(self, get_server: Callable[[str], dict | None],
                 get_all_servers: Callable[[], list[dict]],
                 servers: list[dict] | None = None):
        self._get_server = get_server
        self._get_all_servers = get_all_servers
        self._servers = servers or []
        self._bus = EventBus()

    def scan(self, ip: str, player_level: int, max_bounces: int,
             current_server: str | None = None) -> dict:
        """Scan a target IP. Returns info dict."""
        target = self._get_server(ip)
        if target is None:
            return {'success': False, 'msg': 'Target not found.'}

        # Reachability
        if current_server and ip != current_server:
            cur = self._get_server(current_server)
            if cur and ip not in [s.get('name', '') for s in cur.get('links', [])]:
                return {'success': False, 'msg': 'Target not reachable from here.'}

        ports = [p for p in target.get('ports', [])]
        open_ports = [p for p in ports if random.random() > 0.2]

        result = {
            'success': True,
            'name': target.get('name', ip),
            'ip': ip,
            'ports': open_ports,
            'key_bits': target.get('key_bits', 1024),
            'money': target.get('money', 0),
            'desc': target.get('desc', ''),
            'is_gov': target.get('is_gov', False),
        }

        self._bus.publish(DomainEvent(
            DomainEventType.NETWORK, 'scan',
            {'target': ip, 'open_ports': len(open_ports)}
        ))
        return result

    def connect(self, ip: str, port: int,
                current_server: str | None = None) -> dict:
        """Attempt to connect to a port on target."""
        target = self._get_server(ip)
        if target is None:
            return {'success': False, 'msg': 'Target not found.'}

        ports = target.get('ports', [])
        cracked = target.get('cracked', {})

        if port not in ports:
            return {'success': False, 'msg': f'Port {port} is closed or filtered.'}

        is_cracked = cracked.get(port, False)
        result = {
            'success': True,
            'port': port,
            'cracked': is_cracked,
            'name': target.get('name', ip),
        }

        if is_cracked:
            result['files'] = target.get('files', [])

        self._bus.publish(DomainEvent(
            DomainEventType.NETWORK, 'connect',
            {'target': ip, 'port': port}
        ))
        return result

    def resolve_neighbors(self, ip: str) -> list[str]:
        """Return neighbor list for a server."""
        target = self._get_server(ip)
        if target is None:
            return []
        links = target.get('links', [])
        return [s.name if hasattr(s, 'name') else str(s) for s in links]

    def is_reachable(self, source: str, target: str,
                     visited: set | None = None) -> bool:
        """BFS reachability check."""
        all_servers = self._get_all_servers()
        graph = {}
        for s in all_servers:
            sn = s.get('name', '')
            graph[sn] = []
            for link in s.get('links', []):
                ln = link.name if hasattr(link, 'name') else str(link)
                graph[sn].append(ln)

        if visited is None:
            visited = set()
        if source == target:
            return True
        visited.add(source)
        for neighbor in graph.get(source, []):
            if neighbor not in visited:
                if self.is_reachable(neighbor, target, visited):
                    return True
        return False
