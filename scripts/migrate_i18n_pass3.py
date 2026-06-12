#!/usr/bin/env python3
"""Third pass: translate add_news and add_log calls with Italian strings."""

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

# Extra entries not yet in the dictionary
EXTRA = {
    'Nuova partita iniziata.': 'New game started.',
    'System online. Darius legacy attivo.': 'System online. Darius legacy active.',
}
ITALIAN2EN.update(EXTRA)

def fix_file(filepath):
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # Fix add_news('Italian template', ...) and add_log('Italian text', ...)
    def replace_plain(m):
        prefix = m.group(1)  # add_news( or add_log(
        inner = m.group(2)
        rest = m.group(3)
        if inner in ITALIAN2EN:
            # rest starts with comma, includes closing ) of add_news/add_log
            return f"{prefix}_('{ITALIAN2EN[inner]}'){rest}"
        return m.group(0)

    content = re.sub(
        r"((?:\w+\.)?add_(?:news|log)\()'([^']*)'(.*)",
        replace_plain,
        content
    )

    # Fix add_log(f'Italian {var} text', ...) — f-string cases
    def replace_fstring(m):
        prefix = m.group(1)  # g.add_log(
        inner = m.group(2)   # f-string content between f' and '
        rest = m.group(3)    # everything after the closing ' to end of function call
        
        # Simple f-string parse: replace {expr} with {} placeholders
        template_parts = []
        args = []
        i = 0
        while i < len(inner):
            if inner[i] == '{':
                depth = 1
                j = i + 1
                while j < len(inner) and depth > 0:
                    if inner[j] == '{': depth += 1
                    elif inner[j] == '}': depth -= 1
                    j += 1
                if depth == 0:
                    expr = inner[i+1:j-1]
                    # Check for format spec (last : at brace-depth 0)
                    colon = -1
                    bd = 0
                    in_sq = False
                    in_dq = False
                    for k, ch in enumerate(expr):
                        if ch == "'" and not in_dq: in_sq = not in_sq
                        elif ch == '"' and not in_sq: in_dq = not in_dq
                        elif not in_sq and not in_dq:
                            if ch == '{': bd += 1
                            elif ch == '}': bd -= 1
                            elif ch == ':' and bd == 0: colon = k
                    if colon >= 0:
                        var_expr = expr[:colon]
                        fmt_spec = expr[colon+1:]
                        template_parts.append('{:' + fmt_spec + '}')
                    else:
                        var_expr = expr
                        template_parts.append('{}')
                    args.append(var_expr.strip())
                    i = j
                else:
                    template_parts.append(inner[i])
                    i += 1
            else:
                template_parts.append(inner[i])
                i += 1
        
        template = ''.join(template_parts)
        
        if template in ITALIAN2EN:
            english = ITALIAN2EN[template]
        else:
            english = template
        
        if args:
            arg_str = ', '.join(args)
            return f"{prefix}_fmt('{english}', {arg_str}){rest}"
        else:
            return f"{prefix}_('{english}'){rest}"

    content = re.sub(
        r"((?:\w+\.)?add_(?:news|log)\()f'([^']*)'(.*)",
        replace_fstring,
        content
    )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  FIXED: {filepath}")
    else:
        print(f"  OK: {filepath}")

for fp in FILES:
    fix_file(fp)
print("Done.")
