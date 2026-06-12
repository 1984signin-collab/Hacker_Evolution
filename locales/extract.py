#!/usr/bin/env python3
"""Extract all _() strings from source code and generate a .pot template.

Usage:
    python locales/extract.py                    # scan all .py files, print counts
    python locales/extract.py --pot > out.pot    # generate .pot file
    python locales/extract.py --md               # print markdown string table

Scans for:
    _("string")
    _('string')
    _fmt("string", ...)
    _fmt('string', ...)
"""

import ast
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Files/directories to skip
SKIP = {
    '.git', '__pycache__', 'locales', 'env', 'venv', '.venv',
    'node_modules', 'scripts', '__init__.py',
}


def find_py_files():
    """Yield all .py files in the repo."""
    for root, dirs, files in os.walk(REPO):
        # Skip in-place
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith('.')]
        for f in files:
            if f.endswith('.py') and f not in SKIP:
                yield Path(root) / f


def extract_strings(filepath):
    """Extract _() and _fmt() string literals from a Python file using AST."""
    strings = set()
    try:
        tree = ast.parse(filepath.read_text(encoding='utf-8'))
    except SyntaxError:
        return strings

    for node in ast.walk(tree):
        # Look for _(...) and _fmt(...) calls
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in ('_', '_fmt'):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        strings.add(arg.value)
    return strings


def main():
    all_strings = set()
    by_file = {}

    for pyfile in find_py_files():
        strs = extract_strings(pyfile)
        if strs:
            by_file[pyfile.relative_to(REPO)] = strs
            all_strings.update(strs)

    mode = sys.argv[1] if len(sys.argv) > 1 else 'summary'

    if mode == '--pot':
        print_pot(all_strings)
    elif mode == '--md':
        print_md(by_file, all_strings)
    else:
        print_summary(by_file, all_strings)


def print_summary(by_file, all_strings):
    print(f"Total unique strings: {len(all_strings)}")
    print(f"Files with translatable strings: {len(by_file)}")
    for fpath, strs in sorted(by_file.items()):
        print(f"  {fpath}: {len(strs)} strings")


def print_md(by_file, all_strings):
    for fpath, strs in sorted(by_file.items()):
        print(f"### {fpath}")
        for s in sorted(strs):
            print(f"- `{s}`")
        print()


def escape_po(s):
    """Escape a string for .po format."""
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    s = s.replace('\t', '\\t')
    return s


def print_pot(all_strings):
    print(r"""# HACKER EVOLUTION — Translation Template
# Copyright (C) 2026 404 Fun Not Found
# This file is distributed under the same license as the HACKER EVOLUTION package.
#
# FIRST AUTHOR <EMAIL@ADDRESS>, 2026.
#
msgid ""
msgstr ""
"Project-Id-Version: HACKER EVOLUTION 1.0\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2026-06-12 12:00+0000\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"Language: \n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
""")
    for s in sorted(all_strings):
        if s == '':
            continue
        escaped = escape_po(s)
        # Wrap long strings at 78 chars
        if len(escaped) <= 76:
            print(f'msgid "{escaped}"')
        else:
            # Split into msgid "" + continuation lines
            print('msgid ""')
            while escaped:
                chunk = escaped[:76]
                escaped = escaped[76:]
                print(f'"{chunk}"')
        print('msgstr ""')
        print()


if __name__ == '__main__':
    main()
