#!/usr/bin/env python3
"""Generate Italian .po from extracted strings + existing lang_it.py.

Usage:
    python locales/migrate_it.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

# ── Step 1: Extract all _() strings from source code ─────────────────────────

from locales.extract import find_py_files, extract_strings, escape_po

def get_source_strings():
    all_strings = set()
    for pyfile in find_py_files():
        all_strings.update(extract_strings(pyfile))
    return all_strings


# ── Step 2: Load existing Italian translations ────────────────────────────────

def load_italian_dict():
    """Load the existing lang_it.py translations."""
    try:
        from ui.lang_it import STRINGS as it_strings
        return it_strings
    except ImportError:
        return {}


# ── Step 3: Generate Italian .po ──────────────────────────────────────────────

PO_HEADER = r'''# HACKER EVOLUTION — Italian Translation
# Copyright (C) 2026 404 Fun Not Found
#
msgid ""
msgstr ""
"Project-Id-Version: HACKER EVOLUTION 1.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2026-06-12 12:00+0000\n"
"PO-Revision-Date: 2026-06-12 12:00+0000\n"
"Last-Translator: \n"
"Language-Team: Italian <it@li.org>\n"
"Language: it\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\n"

'''


def escape_po_str(s):
    """Escape string for .po format."""
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    return s


def format_po_entry(msgid, msgstr):
    """Format a .po entry with proper wrapping."""
    lines = []
    
    # Handle multi-line msgid
    escaped_id = escape_po_str(msgid)
    if len(escaped_id) <= 76 and '\n' not in msgid:
        lines.append(f'msgid "{escaped_id}"')
    else:
        lines.append('msgid ""')
        if '\n' in msgid:
            # Split by newlines
            for part in msgid.split('\n'):
                if part:
                    lines.append(f'"{escape_po_str(part)}\\n"')
                else:
                    lines.append('"\\n"')
        else:
            # Word-wrap long single line
            while escaped_id:
                chunk = escaped_id[:76]
                escaped_id = escaped_id[76:]
                lines.append(f'"{chunk}"')
    
    # Handle multi-line msgstr
    escaped_str = escape_po_str(msgstr)
    if not msgstr:
        lines.append('msgstr ""')
    elif len(escaped_str) <= 76 and '\n' not in msgstr:
        lines.append(f'msgstr "{escaped_str}"')
    else:
        lines.append('msgstr ""')
        if '\n' in msgstr:
            for part in msgstr.split('\n'):
                if part:
                    lines.append(f'"{escape_po_str(part)}\\n"')
                else:
                    lines.append('"\\n"')
        else:
            while escaped_str:
                chunk = escaped_str[:76]
                escaped_str = escaped_str[76:]
                lines.append(f'"{chunk}"')
    
    lines.append('')
    return '\n'.join(lines)


def main():
    source_strings = get_source_strings()
    italian_dict = load_italian_dict()
    
    print(f"Source strings found: {len(source_strings)}")
    print(f"Italian dictionary entries: {len(italian_dict)}")
    
    # Generate .po content
    lines = [PO_HEADER]
    
    matched = 0
    missing = 0
    
    for s in sorted(source_strings):
        if s == '':
            continue
        it = italian_dict.get(s, '')
        if it:
            matched += 1
        else:
            missing += 1
        lines.append(format_po_entry(s, it))
    
    # Also include any lang_it.py entries that are NOT in source strings
    # (they might be legacy but still useful)
    extra = 0
    for s, it in sorted(italian_dict.items()):
        if s not in source_strings and s != '':
            lines.append(format_po_entry(s, it))
            extra += 1
    
    # Write .po file
    po_path = Path(__file__).resolve().parent / 'it' / 'LC_MESSAGES' / 'messages.po'
    po_path.parent.mkdir(parents=True, exist_ok=True)
    po_path.write_text('\n'.join(lines), encoding='utf-8')
    
    print(f"Matched: {matched}, Missing translations: {missing}, Extra (from lang_it): {extra}")
    print(f"Written to: {po_path}")
    print(f"Total entries: {matched + missing + extra}")


if __name__ == '__main__':
    main()
