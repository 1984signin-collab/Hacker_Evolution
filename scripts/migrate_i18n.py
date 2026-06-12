#!/usr/bin/env python3
"""One-time migration: wrap Italian strings with _() and _fmt() for i18n.

Run: python scripts/migrate_i18n.py
"""

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
    'engine/game.py',
]

IMPORT_LINE = 'from ui.lang import _, _fmt'

def add_import(content):
    if IMPORT_LINE in content:
        return content, False
    lines = content.split('\n')
    last_import = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            last_import = i
    insert_at = last_import + 1 if last_import >= 0 else 0
    while insert_at < len(lines) and lines[insert_at].strip() == '':
        insert_at += 1
    lines.insert(insert_at, IMPORT_LINE)
    return '\n'.join(lines), True

def extract_fstring_parts(fs_content):
    """Parse f-string body -> (template_with_placeholders, arg_exprs_list)."""
    parts = []
    args = []
    i = 0
    while i < len(fs_content):
        if fs_content[i] == '{':
            depth = 1
            j = i + 1
            while j < len(fs_content) and depth > 0:
                if fs_content[j] == '{':
                    depth += 1
                elif fs_content[j] == '}':
                    depth -= 1
                j += 1
            if depth == 0:
                expr = fs_content[i+1:j-1]
                # Find the LAST ':' at brace-depth 0 and bracket-depth 0
                # (not in strings, not inside {} or []) — that's the format spec separator
                colon_pos = -1
                bd = 0
                brd = 0
                in_sq = False
                in_dq = False
                for k, ch in enumerate(expr):
                    if ch == "'" and not in_dq:
                        in_sq = not in_sq
                    elif ch == '"' and not in_sq:
                        in_dq = not in_dq
                    elif not in_sq and not in_dq:
                        if ch == '{':
                            bd += 1
                        elif ch == '}':
                            bd -= 1
                        elif ch == '[':
                            brd += 1
                        elif ch == ']':
                            brd -= 1
                        elif ch == ':' and bd == 0 and brd == 0:
                            colon_pos = k
                if colon_pos >= 0:
                    var_expr = expr[:colon_pos]
                    fmt_spec = expr[colon_pos+1:]
                    placeholder = '{:' + fmt_spec + '}'
                else:
                    var_expr = expr
                    placeholder = '{}'
                parts.append(placeholder)
                args.append(var_expr.strip())
                i = j
            else:
                parts.append(fs_content[i])
                i += 1
        elif fs_content[i] == '}' and i+1 < len(fs_content) and fs_content[i+1] == '}':
            parts.append('{}')
            i += 2
        else:
            parts.append(fs_content[i])
            i += 1
    return ''.join(parts), args

def process_file(filepath):
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath}")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # 1. Add import
    content, changed = add_import(content)

    # 2. Handle self.console_out(f'...', rest)
    def replace_fstring(m):
        fs_body = m.group(1)
        rest = m.group(2)
        template, args = extract_fstring_parts(fs_body)
        if not args:
            key = template
            if key in ITALIAN2EN:
                return f"self.console_out(_('{ITALIAN2EN[key]}'){rest})"
            return f"self.console_out(_('{key}'){rest})"
        key = template
        if key in ITALIAN2EN:
            english = ITALIAN2EN[key]
        else:
            english = key
        arg_str = ', '.join(args)
        # Escape single quotes in the template (but not the format spec placeholders)
        safe_english = english.replace("'", "\\'")
        # Fix: placeholders like {:>6,} have : in them, don't escape those
        return f"self.console_out(_fmt('{safe_english}', {arg_str}){rest})"

    content = re.sub(
        r"self\.console_out\(f'([^']*)'(,\s*.*)\)",
        replace_fstring,
        content
    )

    # 3. Handle self.console_out('text', rest)
    def replace_plain(m):
        text = m.group(1)
        rest = m.group(2)
        if text in ITALIAN2EN:
            return f"self.console_out(_('{ITALIAN2EN[text]}'){rest})"
        # Even if not in dict, wrap in _() to future-proof
        safe_text = text.replace("'", "\\'")
        return f"self.console_out(_('{safe_text}'){rest})"

    content = re.sub(
        r"self\.console_out\('([^']*)'(,\s*.*)\)",
        replace_plain,
        content
    )

    # 4. Handle Rich panel/table titles
    content = re.sub(
        r"(title=)'([^']*)'",
        lambda m: f"{m.group(1)}_('{m.group(2)}')",
        content
    )
    content = re.sub(
        r"title=f'([^']*)'",
        lambda m: f"title=_('{m.group(1)}')",
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  MODIFIED: {filepath}")
    else:
        print(f"  UNCHANGED: {filepath}")

def main():
    for fp in FILES:
        process_file(fp)
    print("Done.")

if __name__ == '__main__':
    main()
