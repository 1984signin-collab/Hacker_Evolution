"""Bridge between Rich renderables and tkinter Text widget.

Converts Rich's styled Segment output into tkinter Text widget
insertions with color tags — no ANSI parsing needed.
"""
import tkinter as tk
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.text import Text
from rich.rule import Rule
from rich.columns import Columns
from rich.theme import Theme
from rich.style import Style

# Match the game's custom color palette
GAME_THEME = Theme({
    'green':  '#00cc88',
    'red':    '#cc2244',
    'yellow': '#ccaa00',
    'cyan':   '#00cccc',
    'dim':    '#7799aa',
    'white':  '#ddeeff',
    'pink':   '#cc44cc',
    'blue':   '#008888',
    'orange': '#ccaa00',
})

_console = Console(
    force_terminal=True,
    color_system='truecolor',
    theme=GAME_THEME,
    width=80,
)

_tag_counter = 0


def _next_tag():
    global _tag_counter
    _tag_counter += 1
    return f'_rt{_tag_counter}'


def _style_to_kw(style: Style) -> dict:
    """Convert a Rich Style to tkinter Text widget tag kwargs."""
    kw = {}
    if style:
        if style.bold:
            kw['font'] = ('Consolas', 11, 'bold')
        if style.italic:
            kw['font'] = ('Consolas', 11, 'italic')
        if style.color:
            if style.color.triplet:
                kw['foreground'] = style.color.triplet.hex
        if style.bgcolor:
            if style.bgcolor.triplet:
                kw['background'] = style.bgcolor.triplet.hex
    return kw


def _has_style(style) -> bool:
    """Check if a style has any visual effect."""
    if not style:
        return False
    return bool(style.color or style.bgcolor or style.bold or style.italic)


def _insert_styled(widget: tk.Text, text: str, style):
    """Insert text into the widget and apply an optional Rich style as a tag."""
    if not text:
        return
    start = widget.index('end-1c')
    widget.insert(tk.END, text)
    end = widget.index('end-1c')
    if end == start:
        return
    if _has_style(style):
        tag = _next_tag()
        widget.tag_add(tag, start, end)
        kw = _style_to_kw(style)
        if kw:
            widget.tag_config(tag, **kw)


def render_to_widget(widget: tk.Text, renderable, width=None):
    """Render a Rich renderable (Table, Panel, Text, etc.) into a tkinter Text widget.

    Args:
        widget: The tkinter Text widget to render into.
        renderable: A Rich renderable (Table, Panel, str, etc.).
        width: Character width for Rich layout.  Auto-detects from widget if None.
    """
    if width is None:
        try:
            width = int(widget.cget('width'))
        except Exception:
            width = 80
    if width < 20:
        width = 80

    # Build a console with the right width
    _console.width = width
    opts = _console.options

    rendered = list(_console.render(renderable, opts))

    old_state = widget.cget('state')
    widget.config(state=tk.NORMAL)

    for segment in rendered:
        text = segment.text
        style = segment.style

        if text is None:
            continue

        # Handle newlines within segment text
        if '\n' in text:
            parts = text.split('\n')
            for i, part in enumerate(parts):
                if part:
                    _insert_styled(widget, part, style)
                if i < len(parts) - 1:
                    widget.insert(tk.END, '\n')
        elif text:
            _insert_styled(widget, text, style)

    widget.see(tk.END)
    widget.config(state=old_state)


# ─── Helper factories ────────────────────────────────────────────────────────

def make_table(title=None, headers=None, rows=None,
               border_style='cyan', header_style='bold green',
               **kwargs) -> Table:
    """Build a Rich Table with game-consistent styling."""
    table = Table(title=title, title_style='bold cyan',
                  border_style=border_style, **kwargs)
    if headers:
        for h in headers:
            table.add_column(h, header_style=header_style)
    if rows:
        for row in rows:
            table.add_row(*row)
    return table


def make_panel(renderable, title=None,
               border_style='cyan', **kwargs) -> Panel:
    """Build a Rich Panel with game-consistent styling."""
    return Panel(renderable, title=title,
                 title_align='left',
                 border_style=border_style, **kwargs)
