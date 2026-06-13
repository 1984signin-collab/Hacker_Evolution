# Summary

## Goal
- UI cyberpunk premium con Canvas-drawn panels, stat cards, Sentinel AI, enhanced network map

## Constraints & Preferences
- Stack: Python, tkinter, Canvas (no customtkinter, no PIL/SVG)
- Tutto `Canvas.create_*` — niente immagini
- Palette: `#000000` sfondo, `#000504` pannelli, ciano/teal dominante, viola/magenta solo per alert
- Zero decorazioni gratuite — riservate solo allo sfondo HUD
- Abolizione totale emoji da label/menu/notifiche
- Performance: ogni `after()` deve completare in <16ms (60fps)
- L'utente ha scelto "Riscrittura Canvas totale" rispetto a miglioramenti incrementali

## Progress

### Done
- `ui/theme.py` — Theme dataclass con palette calibrata su `update/generated-image.png`:
  - BG_VOID `#000000`, BG_CANVAS `#000504`, BG_SURFACE `#000a0a`, BG_HEADER `#001212`
  - CYAN `#00cccc`, CYAN_MID `#008888`, CYAN_DIM `#004444`, CYAN_ULTRADIM `#002222`
  - MAGENTA `#cc44cc`, GREEN `#00cc88`, AMBER `#ccaa00`, RED `#cc2244`
  - Helper: `rgba()`, `linear()`, `alpha()`, `text_color()`, `with_font()`
- `ui/fonts.py` — FontManager: discover JetBrains Mono → Consolas fallback
- `engine/config.py` — Colors metaclasse: tutte le vecchie costanti (`Colors.bg`, `Colors.cyan`, ecc.) mappano ai nuovi valori Theme
- `ui/hud.py` — riscritto con palette scura teal-only
- `ui/rich_bridge.py` — palette Rich aggiornata
- `ui/widgets/stat_card.py` — CanvasStatCard, CanvasSectionHeader
- `ui/widgets/sentinel_panel.py` — SentinelPanel: IDLE/ANALYZING/ACTIVE, threat bar, scan bars
- `ui/app.py` — layout riscritto:
  - Titolo Canvas con ASCII art
  - Console left (65%) + Right panel Canvas-drawn (33%) con 2×2 stat cards, quick stats, sentinel, hardware, objectives
  - Mappa di rete con header e status (X/N COMPROMISED)
  - Status bar bottom (IP, CONN, TRACE)
  - Map: emoji rimossi (`$`, `⚠`, `📡` → `$`, `!`, `~`, `#`, `@`, `G`), palette Theme, radar sweep, glow layers
  - Context menu: emoji rimossi, palette Theme
  - Menu bar: palette Theme
  - Glitch/Notifications: palette Theme (Colors → Theme)
  - `_animate_sentinel` al posto di `_animate_seps`
  - Console boot: emoji rimosso da messaggio email
  - `Colors.*` completamente eliminato da `ui/app.py`

### In Progress
- (none)

### Blocked
- (nessuno)

## Key Decisions
- Riscrittura Canvas totale (non solo palette swap)
- Stat cards disegnati su Canvas — nessun Frame/Label annidato
- Sentinel con stati IDLE/ANALYZING/ACTIVE e barra threat
- Layout: console 65% + right panel Canvas 33% + mappa full-width
- Status bar persistente (IP, CONN, TRACE level)
- Zero emoji in tutta la UI

## Critical Context
- `ui/app.py` ~1549 righe — tutte le vecchie costanti Colors rimosse, ora solo Theme
- `self._sep_canvases`, `self.sys`, `self.msg`, `self.trace_canvas`, `self.bounce_lbl`, `self.hw_lbls` rimossi
- Vecchi metodi rimossi: `render_msg`, `render_news`, `_animate_seps`, `_draw_sep`, `_glow_bar`, `pulse_label`, `_animated_sep`
- `_()` non implementato (LSP error) — preesistente
- `h_help`, `h_ls`, ecc. sono patched a runtime da `ui.commands` e `ui.panels` — LSP errors preesistenti

## Relevant Files
- `ui/theme.py` — Theme dataclass
- `ui/fonts.py` — FontManager
- `ui/widgets/stat_card.py` — CanvasStatCard, CanvasSectionHeader
- `ui/widgets/sentinel_panel.py` — SentinelPanel
- `ui/app.py` — ~1549 righe, layout riscritto
- `engine/config.py` — Colors metaclasse
- `ui/hud.py` — HUD teal-only
- `ui/rich_bridge.py` — palette Rich
- `ui/panels.py` — import Theme
