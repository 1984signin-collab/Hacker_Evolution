#!/usr/bin/env python3
"""HACKER EVOLUTION — Command Registry (Phase 2: Command System).

Central registry for all commands with metadata, auto-generated HELP.
Singleton — accessed via CommandRegistry.instance().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from .services import DomainEvent, DomainEventType, EventBus


@dataclass
class CommandMeta:
    """Metadata for a registered command."""
    name: str
    handler: Callable
    help_text: str
    usage: str = ''
    aliases: list[str] = field(default_factory=list)
    min_level: int = 0
    admin_only: bool = False
    category: str = 'general'


class CommandRegistry:
    """Singleton registry for all game commands."""

    _instance: CommandRegistry | None = None
    _commands: dict[str, CommandMeta]
    _alias_map: dict[str, str]
    _bus: EventBus

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._commands = {}
            cls._instance._alias_map = {}
            cls._instance._bus = EventBus()
        return cls._instance

    # ── Registration ──

    def register(self, meta: CommandMeta):
        """Register a command with its metadata."""
        self._commands[meta.name] = meta
        for alias in meta.aliases:
            self._alias_map[alias] = meta.name
        self._bus.publish(DomainEvent(
            DomainEventType.SYSTEM, 'command_registered',
            {'name': meta.name}
        ))

    def register_decorator(self, name: str, help_text: str = '',
                           usage: str = '', aliases: list[str] | None = None,
                           min_level: int = 0, admin_only: bool = False,
                           category: str = 'general'):
        """Decorator that registers the decorated function as a command.

        Usage:
            @registry.register_decorator('scan', help_text='Scan a target', usage='scan <ip>')
            def h_scan(args, game):
                ...
        """
        def decorator(func):
            meta = CommandMeta(
                name=name,
                handler=func,
                help_text=help_text,
                usage=usage,
                aliases=aliases or [],
                min_level=min_level,
                admin_only=admin_only,
                category=category,
            )
            self.register(meta)
            return func
        return decorator

    # ── Lookup ──

    def get(self, name: str) -> CommandMeta | None:
        """Look up a command by name or alias."""
        cmd = self._commands.get(name)
        if cmd:
            return cmd
        canonical = self._alias_map.get(name)
        if canonical:
            return self._commands.get(canonical)
        return None

    def has(self, name: str) -> bool:
        return self.get(name) is not None

    def resolve(self, name: str) -> CommandMeta | None:
        """Resolve a name to its canonical CommandMeta."""
        return self.get(name)

    # ── Listing ──

    def list_commands(self, category: str | None = None,
                      player_level: int = 0,
                      include_admin: bool = False) -> list[CommandMeta]:
        """List commands, optionally filtered."""
        results = []
        for cmd in self._commands.values():
            if cmd.admin_only and not include_admin:
                continue
            if category and cmd.category != category:
                continue
            if player_level < cmd.min_level:
                continue
            results.append(cmd)
        # Sort by name
        results.sort(key=lambda c: c.name)
        return results

    def categories(self) -> list[str]:
        """Return all known categories."""
        cats = set()
        for cmd in self._commands.values():
            cats.add(cmd.category)
        return sorted(cats)

    def generate_help(self, player_level: int = 0,
                      include_admin: bool = False) -> str:
        """Auto-generate a formatted HELP text from the registry."""
        lines = []
        categories = self.categories()
        for cat in categories:
            cmds = self.list_commands(cat, player_level, include_admin)
            if not cmds:
                continue
            lines.append(f'\n  [{cat.upper()}]')
            for cmd in cmds:
                usage = f' {cmd.usage}' if cmd.usage else ''
                help_preview = cmd.help_text[:60] if cmd.help_text else ''
                if help_preview:
                    lines.append(f'    {cmd.name:<15} {help_preview}')
                else:
                    lines.append(f'    {cmd.name:<15} {usage}')
                if cmd.aliases:
                    alias_str = ', '.join(cmd.aliases)
                    lines.append(f'    {" ":<15} aliases: {alias_str}')

        if not lines:
            lines.append('  No commands registered.')

        return '\n'.join(lines)

    # ── Dispatch ──

    def dispatch(self, name: str, args: str, game: Any) -> str | None:
        """Look up and call a command handler.

        Returns the handler's return value (typically a display string).
        """
        meta = self.get(name)
        if meta is None:
            return None  # Not found — caller handles fallback
        return meta.handler(args, game)

    # ── State ──

    def to_dict(self) -> dict:
        return {
            'commands': list(self._commands.keys()),
            'aliases': dict(self._alias_map),
        }

    @classmethod
    def reset(cls):
        """Clear registry (useful for testing)."""
        if cls._instance:
            cls._instance._commands = {}
            cls._instance._alias_map = {}
