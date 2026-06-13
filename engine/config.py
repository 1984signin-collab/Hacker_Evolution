#!/usr/bin/env python3
# HACKER EVOLUTION — Config / Constants
#
# Colors are now defined in ui/theme.py.
# This module re-exports Colors for backward compatibility
# during the W1 refactoring.

import sys
import os

SAVE_FILE = 'he_save.json'
AUTO_FILE = 'he_auto.json'

# Legacy Colors class — maps to new Theme via property aliases
# so that old code like Colors.bg, Colors.cyan still works.
class ColorsMeta(type):
    """Metaclass for lazy Theme import — avoids circular deps."""

    def __getattr__(cls, name):
        from ui.theme import Theme
        MAPPING = {
            'bg':        'BG_VOID',
            'dark':      'BG_CANVAS',
            'darker':    'BG_SURFACE',
            'black':     'BG_VOID',
            'cyan':      'CYAN',
            'cyan2':     'CYAN_MID',
            'cyan3':     'CYAN_DIM',
            'cyan4':     'CYAN_ULTRADIM',
            'blue':      'CYAN_MID',
            'blue2':     'CYAN_DIM',
            'dim':       'TEXT_DIM',
            'red':       'RED',
            'red_dark':  'RED_DIM',
            'yellow':    'AMBER',
            'orange':    'AMBER',
            'green':     'GREEN',
            'green2':    'GREEN',
            'pink':      'MAGENTA',
            'white':     'TEXT',
            'panel_bg':  'BG_SURFACE',
            'border':    'CYAN_ULTRADIM',
            'border2':   'CYAN_DIM',
            'grid':      'CYAN_ULTRADIM',
        }
        attr = MAPPING.get(name)
        if attr is not None:
            return getattr(Theme, attr)
        raise AttributeError(f"Colors has no attribute '{name}'")


class Colors(metaclass=ColorsMeta):
    """Legacy color constants — maps to Theme via metaclass.

    All new code should import Theme directly:
        from ui.theme import Theme
    """


KATA = list('ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ0123456789ABCDEF')
