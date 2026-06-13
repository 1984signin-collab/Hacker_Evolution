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

## Progress

### Done — Core infrastructure
- `ui/theme.py` — Theme dataclass con palette calibrata su `update/generated-image.png`
- `ui/fonts.py` — FontManager: discover JetBrains Mono → Consolas
- `engine/config.py` — Colors metaclasse backward compatibile
- `ui/hud.py` — HUD riscritto con palette scura teal-only (vignetta, griglia, corner brackets, scanlines, CRT noise)
- `ui/rich_bridge.py` — palette Rich aggiornata

### Done — Widgets
- `ui/widgets/stat_card.py` — CanvasStatCard, CanvasSectionHeader
- `ui/widgets/sentinel_panel.py` — Sentinela con pulse glow per stato, corner brackets animati, scan bar pattern variabile, threat bar animata, dati flow dots
- `ui/widgets/network_map.py` — NetworkMapRenderer: radar grid + sweep, connessioni gradiente, data packets animati, bounce chain mission-critical, glow layers, compromised data orbite, particle emission
- `ui/widgets/boot_screen.py` — BootScreen Canvas: 6s animation con splash ASCII glow, boot messages typing, glitch transition → main UI
- `ui/widgets/alert_overlay.py` — AlertOverlay: overlay modale con dim bg, pannello alert, corner brackets, icon circle, messaggio, progress bar countdown

### Done — Layout app
- `ui/app.py` — Layout riscritto (console 65% + right panel Canvas 33% + mappa + status bar)
- **Map refactor**: inline drawing → NetworkMapRenderer
- **Colors migration**: tutte `Colors.*` → `Theme.*`
- **Emoji removal**: mappa, context menu, menu bar, boot messages
- **Boot replaced**: 25s boot → 6s Canvas BootScreen
- **Alert integration**: AlertOverlay su overlay canvas, animato in loop sentinel
- **Console corner brackets**: Canvas overlay su glow_frame

## Next Steps
- Rimuovere dead code (vecchi metodi boot: `_boot_animate`, `_boot_login_prompt`, ecc.)
- Integrare AlertOverlay nei flussi di gioco (trace alarm, errori scan, ecc.)
- Collegare `SentinelPanel.set_state()` alla logica di gioco reale

## Relevant Files
- `ui/theme.py` — palette
- `ui/fonts.py` — font discovery
- `ui/widgets/__init__.py`
- `ui/widgets/stat_card.py`
- `ui/widgets/sentinel_panel.py`
- `ui/widgets/network_map.py`
- `ui/widgets/boot_screen.py`
- `ui/widgets/alert_overlay.py`
- `ui/app.py` — layout principale, ~1350 righe
- `engine/config.py` — Colors metaclasse
- `ui/hud.py` — HUD teal-only con scanlines
- `ui/rich_bridge.py` — palette Rich
- `ui/panels.py`
