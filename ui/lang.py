#!/usr/bin/env python3
"""HACKER EVOLUTION — Gettext-style i18n system using .po files.

Uses standard .po files in locales/{lang}/LC_MESSAGES/messages.po.

To add a new language:
  1. Create locales/{code}/LC_MESSAGES/messages.po
  2. Fill in msgid → msgstr translations
  3. Restart the game — the new language appears in Settings

No compilation step needed. .po files are parsed directly at runtime.

Usage in code:
    from ui.lang import _, _fmt, set_lang, get_lang, LANGUAGES

    label = _('Connect')                          # simple string
    msg   = _fmt('Scan {host} first', host=h)     # with variables
"""

import re
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
_LOCALES_DIR = Path(__file__).resolve().parent.parent / 'locales'

# ── Runtime state ─────────────────────────────────────────────────────────────
_current_lang = 'en'
_translations = {}  # language_code -> {msgid: msgstr}
_LANG_CODES = ['en']  # list of available language codes

# ── Known language display names (extend when adding new languages) ───────────
_LANGUAGE_NAMES = {
    'en': 'English',
    'it': 'Italiano',
    'fr': 'Français',
    'de': 'Deutsch',
    'es': 'Español',
    'pt': 'Português',
    'pt_BR': 'Português (Brasil)',
    'ru': 'Русский',
    'zh': '中文',
    'ja': '日本語',
    'ko': '한국어',
    'ar': 'العربية',
    'nl': 'Nederlands',
    'pl': 'Polski',
    'tr': 'Türkçe',
}


# ═══════════════════════════════════════════════════════════════════════════════
# .po file parser
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_po(filepath):
    """Parse a .po file into {msgid: msgstr} dictionary.

    Handles:
      - Basic:  msgid "hello"\\nmsgstr "ciao"
      - Multiline msgid/msgstr
      - Empty msgid (file header metadata)
      - Comments (#, #., #:, #|, #~)
      - Escape sequences (\\\\n, \\\\", \\\\\\\\)
    """
    translations = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (FileNotFoundError, IOError):
        return translations

    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Strip header (everything up to first blank line after msgid "" msgstr "...")
    # We process all entries including the header, but skip entries starting with #~

    entries = re.split(r'\n(?=msgid)', content)

    for entry in entries:
        entry = entry.strip()
        if not entry or entry.startswith('#~'):
            continue

        msgid = ''
        msgstr = ''
        reading = None  # 'id' or 'str'

        for line in entry.split('\n'):
            line_stripped = line.strip()

            # Skip comment lines
            if line_stripped.startswith('#') and not line_stripped.startswith('#~'):
                continue
            if line_stripped.startswith('#~'):
                msgid = ''
                msgstr = ''
                break  # obsolete entry, skip entirely

            # msgid "..." — may be empty (msgid "")
            m = re.match(r'^msgid\s+"(.*)"\s*$', line_stripped, re.DOTALL)
            if m:
                reading = 'id'
                msgid = _po_unescape(m.group(1))
                continue

            # msgstr "..." — may be empty (msgstr "")
            m = re.match(r'^msgstr\s+"(.*)"\s*$', line_stripped, re.DOTALL)
            if m:
                reading = 'str'
                msgstr = _po_unescape(m.group(1))
                continue

            # Continuation line: "text"
            m = re.match(r'^"(.*)"\s*$', line_stripped, re.DOTALL)
            if m:
                if reading == 'id':
                    msgid += _po_unescape(m.group(1))
                elif reading == 'str':
                    msgstr += _po_unescape(m.group(1))

        if msgid and reading is not None:
            translations[msgid] = msgstr

    return translations


def _po_unescape(s):
    """Unescape a .po string value.

    Handles \\n, \\t, \\\\, \\", \\r, and octal/hex escapes.
    """
    # Must handle backslash before anything else
    s = s.replace('\\n', '\n')
    s = s.replace('\\t', '\t')
    s = s.replace('\\r', '\r')
    s = s.replace('\\"', '"')
    s = s.replace('\\\\', '\\')
    return s


# ═══════════════════════════════════════════════════════════════════════════════
# Language discovery & loading
# ═══════════════════════════════════════════════════════════════════════════════

def _scan_locales():
    """Scan locales/ directory and load all available .po files."""
    global _LANG_CODES, _translations

    _translations = {}
    _LANG_CODES = ['en']

    if not _LOCALES_DIR.exists():
        _LOCALES_DIR.mkdir(parents=True, exist_ok=True)
        return

    for entry in sorted(_LOCALES_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith('.'):
            continue
        po_file = entry / 'LC_MESSAGES' / 'messages.po'
        if po_file.exists():
            _translations[entry.name] = _parse_po(po_file)
            _LANG_CODES.append(entry.name)


# ═══════════════════════════════════════════════════════════════════════════════
# Public API — mirrors gettext convention
# ═══════════════════════════════════════════════════════════════════════════════

def LANGUAGES():
    """Return dict of available language codes → display names."""
    result = {'en': _LANGUAGE_NAMES.get('en', 'English')}
    for code in _LANG_CODES:
        if code != 'en':
            name = _LANGUAGE_NAMES.get(code, code.title())
            result[code] = name
    return result


def set_lang(code: str):
    """Switch the active language at runtime.

    Args:
        code: Language code ('en', 'it', 'fr', etc.)

    Falls back to English if the language is not available.
    """
    global _current_lang
    if code == 'en' or code in _translations:
        _current_lang = code


def get_lang() -> str:
    """Return the current language code (e.g. 'en', 'it')."""
    return _current_lang


def get_lang_name(code=None) -> str:
    """Return the display name for a language code.

    Args:
        code: Language code (default: current language)

    Returns:
        Display name like 'English', 'Italiano', etc.
    """
    if code is None:
        code = _current_lang
    langs = LANGUAGES()
    return langs.get(code, code)


def _(text: str) -> str:
    """Translate an English string to the current language.

    Falls back to the original English text if no translation is found.
    In English mode this is a no-op.

    Args:
        text: English source string

    Returns:
        Translated string, or original text if no translation available
    """
    if _current_lang == 'en':
        return text
    lang_dict = _translations.get(_current_lang)
    if lang_dict is None:
        return text
    return lang_dict.get(text, text)


def _fmt(text: str, *args, **kwargs) -> str:
    """Translate and format with variables.

    Always use this for strings containing variables — word order
    differs between languages.

    Examples:
        _fmt('Scan {host} first', host=hostname)          # keyword
        _fmt('Transfer ${}', amt)                          # positional
        _fmt('{} on {} ({} hops)', host, port, hops)       # multiple positional
    """
    return _(text).format(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# Initialize: scan and load all available translations
# ═══════════════════════════════════════════════════════════════════════════════
_scan_locales()
