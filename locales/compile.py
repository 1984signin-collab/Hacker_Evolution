#!/usr/bin/env python3
"""Compile .po translation files into .mo binary files.

Usage:
    python locales/compile.py              # compile all .po -> .mo for all languages
    python locales/compile.py it           # compile only Italian
    python locales/compile.py it fr        # compile specific languages

The .mo binary format follows the GNU gettext specification:
https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html
"""

import os
import struct
import sys
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent


def parse_po(filepath):
    """Parse a .po file and return a list of (msgid, msgstr) tuples.

    Handles:
      - Simple:  msgid "hello"\nmsgstr "ciao"
      - Multiline: msgid "line1\\n"\n"line2\\n"
      - Empty msgid (header): msgid ""\nmsgstr "Header: ...\\n"
      - Comments (#, #., #:, #|, #~)
      - Escape sequences (\\n, \\", \\\\)
    """
    translations = []
    content = filepath.read_text(encoding='utf-8')

    lines = content.split('\n')
    msgid_parts = None
    msgstr_parts = None
    reading = None  # 'id' or 'str'
    in_entry = False

    def unescape(s):
        """Handle .po escape sequences."""
        s = s.replace('\\"', '\x00QUOTE\x00')
        s = s.replace('\\\\', '\x00BACK\x00')
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        s = s.replace('\\r', '\r')
        s = s.replace('\x00QUOTE\x00', '"')
        s = s.replace('\x00BACK\x00', '\\')
        return s

    for line in lines:
        stripped = line.strip()

        # Skip comment lines
        if stripped.startswith('#'):
            continue

        # msgid "..." or msgid ""
        if stripped.startswith('msgid '):
            # Save previous entry
            if in_entry and msgid_parts is not None:
                msgid = ''.join(msgid_parts)
                msgstr = ''.join(msgstr_parts) if msgstr_parts else ''
                translations.append((msgid, msgstr))

            msgid_parts = []
            msgstr_parts = []
            in_entry = True
            reading = 'id'

            # Extract content after msgid
            rest = stripped[6:].strip()  # 'msgid' is 5 chars, plus space
            if rest.startswith('"') and rest.endswith('"'):
                content = rest[1:-1]
                msgid_parts.append(unescape(content))
            continue

        # msgstr "..." or msgstr ""
        if stripped.startswith('msgstr '):
            reading = 'str'
            rest = stripped[7:].strip()
            if rest.startswith('"') and rest.endswith('"'):
                content = rest[1:-1]
                msgstr_parts.append(unescape(content))
            continue

        # Continuation line: "..."
        if stripped.startswith('"') and in_entry:
            content = stripped[1:-1]
            if reading == 'id':
                msgid_parts.append(unescape(content))
            elif reading == 'str':
                msgstr_parts.append(unescape(content))
            continue

        # Blank line ends entry
        if stripped == '':
            if in_entry and msgid_parts is not None:
                msgid = ''.join(msgid_parts)
                msgstr = ''.join(msgstr_parts) if msgstr_parts else ''
                translations.append((msgid, msgstr))
                msgid_parts = None
                msgstr_parts = None
                in_entry = False
            reading = None
            continue

    # Last entry
    if in_entry and msgid_parts is not None:
        msgid = ''.join(msgid_parts)
        msgstr = ''.join(msgstr_parts) if msgstr_parts else ''
        translations.append((msgid, msgstr))

    return translations


def write_mo(translations, output_path):
    """Write a .mo binary file from a list of (msgid, msgstr) tuples.

    Formats:
      - Header: magic(4B) + version(4B) + count(4B) +
                id_table_offset(4B) + str_table_offset(4B)
      - Hash table size (4B) + hash table offset (4B) — both 0 (no hash)
      - For each string: length(4B) + offset(4B)
      - String table: null-terminated strings concatenated
    """
    # Filter out entries with empty msgid (header) — it's kept for structure
    entries = translations

    # Encode all strings as null-terminated bytes
    id_strings = []
    str_strings = []
    for msgid, msgstr in entries:
        id_strings.append(msgid.encode('utf-8') + b'\x00')
        str_strings.append(msgstr.encode('utf-8') + b'\x00')

    n = len(entries)

    # Build the string tables
    id_table = b''.join(id_strings)
    str_table = b''.join(str_strings)

    # Calculate offsets
    # Header: 7 × 4B = 28B
    # Hash table skip: 2 × 4B = 8B (both 0 for hash_size, hash_offset)
    # Original strings table: n × 8B
    # Translation strings table: n × 8B
    # Then the string data

    header_size = 28  # 7 int32
    hash_skip = 8     # hash_size + hash_offset
    orig_table_size = n * 8
    trans_table_size = n * 8

    orig_table_offset = header_size + hash_skip
    trans_table_offset = orig_table_offset + orig_table_size
    id_table_offset = trans_table_offset + trans_table_size
    str_table_offset = id_table_offset + len(id_table)

    with open(output_path, 'wb') as f:
        # Magic number (little-endian)
        f.write(struct.pack('<I', 0x950412de))
        # Version
        f.write(struct.pack('<I', 0))
        # Number of entries
        f.write(struct.pack('<I', n))
        # Offset of original strings table
        f.write(struct.pack('<I', orig_table_offset))
        # Offset of translation strings table
        f.write(struct.pack('<I', trans_table_offset))
        # Hash table size (0 = no hash table)
        f.write(struct.pack('<I', 0))
        # Hash table offset
        f.write(struct.pack('<I', 0))

        # Original strings table: length + offset for each entry
        offset = id_table_offset
        for s in id_strings:
            f.write(struct.pack('<II', len(s) - 1, offset))  # length without null
            offset += len(s)

        # Translation strings table: length + offset
        offset = str_table_offset
        for s in str_strings:
            f.write(struct.pack('<II', len(s) - 1, offset))
            offset += len(s)

        # String data
        f.write(id_table)
        f.write(str_table)

    return len(entries)


def compile_language(lang_code):
    """Compile .po to .mo for a single language."""
    po_file = LOCALES_DIR / lang_code / 'LC_MESSAGES' / 'messages.po'
    mo_file = LOCALES_DIR / lang_code / 'LC_MESSAGES' / 'messages.mo'

    if not po_file.exists():
        print(f"  ✗ {lang_code}: no .po file at {po_file.relative_to(LOCALES_DIR.parent)}")
        return False

    translations = parse_po(po_file)
    count = len(translations)
    if count == 0:
        print(f"  ⚠ {lang_code}: .po file is empty")
        return False

    mo_file.parent.mkdir(parents=True, exist_ok=True)
    write_mo(translations, mo_file)
    print(f"  ✓ {lang_code}: {count} strings → {mo_file.relative_to(LOCALES_DIR.parent)}")
    return True


def main():
    # Determine which languages to compile
    args = sys.argv[1:]

    if args:
        langs = args
    else:
        # Auto-detect: all directories under locales/ that have .po files
        langs = []
        for entry in sorted(LOCALES_DIR.iterdir()):
            if entry.is_dir() and not entry.name.startswith('.'):
                po = entry / 'LC_MESSAGES' / 'messages.po'
                if po.exists():
                    langs.append(entry.name)

    if not langs:
        print("No .po files found to compile.")
        return

    print(f"Compiling {len(langs)} language(s)...")
    success = 0
    for lang in langs:
        if compile_language(lang):
            success += 1

    print(f"\nDone: {success}/{len(langs)} compiled successfully.")


if __name__ == '__main__':
    main()
