#!/usr/bin/env python3
"""Second pass: fix already-converted lines where _('Italian') wasn't translated."""

import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.lang_it import STRINGS as EN2IT
ITALIAN2EN = {v: k for k, v in EN2IT.items()}

FILES = [
    'ui/commands.py',
    'ui/panels.py',
    'ui/app.py',
]

def fix_file(filepath):
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # Fix _('Italian string') → _('English string')
    def replace_inner(m):
        inner = m.group(1)
        if inner in ITALIAN2EN:
            return f"_('{ITALIAN2EN[inner]}')"
        return m.group(0)

    content = re.sub(r"_\('([^']*)'\)", replace_inner, content)
    
    # Fix _fmt('Italian template', ...) → _fmt('English template', ...)
    def replace_fmt_inner(m):
        inner = m.group(1)
        rest = m.group(2)
        if inner in ITALIAN2EN:
            return f"_fmt('{ITALIAN2EN[inner]}'{rest}"
        return m.group(0)

    content = re.sub(r"_fmt\('([^']*)'(.*)", replace_fmt_inner, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  FIXED: {filepath}")
    else:
        print(f"  OK: {filepath}")

for fp in FILES:
    fix_file(fp)
print("Done.")
