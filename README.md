# 💻 HACKER EVOLUTION

> *"In a world where data is the new currency, only those who can read between the lines of code will survive."*

**Hacker Evolution** is a terminal-based hacking simulator, inspired by the classic *Hacker Evolution: Untold* (exosyphen studios). Explore a simulated network, scan servers, crack firewalls, steal data, and climb the leaderboard.

![Demo](assets/demo.gif)

---

## 🎮 Story

You are a hacker who receives a mysterious email from **Darius**, a former CTO of **Nexus Corporation** who is now dead. His security system — *Overwatch* — has 14 days of autonomy, and it chose you as the only one who can access his legacy.

Nexus built Overwatch to protect critical infrastructure, but they weaponized it: mass surveillance, data trafficking, election manipulation, and ties to government black ops. The evidence is scattered across their servers — corporate, government, and military.

Your mission: breach Nexus's network, steal the truth, and make a final choice that will change everything.

> *"In cyberspace, no one can hear you type."*

---

## ✨ Features

| Feature | Description |
|---|---|
| **Canvas UI** | Full tkinter Canvas-drawn interface — console, stat cards, network map, boot screen, alert overlay. No images, no customtkinter |
| **Network Simulation** | Servers, firewalls, ports, real-time connections |
| **Hacking System** | Scan, crack, connect, download, upload, exec |
| **Economy** | Earn credits by selling data, buy upgrades |
| **Darknet Market** | Buy named exploits (SQL injector, brute-force tool, stealth kit, etc.) |
| **Sentinel AI** | Adaptive adversary with DORMANT → ANALYZING → ACTIVE states, animated panel |
| **Dynamic World** | Random [SYSTEM]/[NET]/[SEC] events while you play |
| **Dynamic Story** | Unfolds episodically via the STORY command |
| **Hardware System** | RAM, CPU, personal firewall — upgrade your rig |
| **Modular Content** | Missions and emails are individual .json files — add your own without touching code |

### Commands

| Command | Action |
|---|---|
| `HELP` | Show all available commands |
| `SCAN` | Scan local network for active servers |
| `SCANPORTS [IP]` | Scan a server's open ports |
| `CONNECT [IP] [port]` | Connect to a remote server |
| `CRACK [IP] [port]` | Brute-force a password on target port |
| `DECRYPT [IP]` | Decrypt a server's encryption key |
| `LOGIN [IP] [password]` | Log into a server with known credentials |
| `LS` | List files on the current server |
| `CAT [file]` | Read a file's contents |
| `DOWNLOAD [file]` | Download a file from the server |
| `UPLOAD [file]` | Upload a file to the server |
| `EXEC [file]` | Execute a file on the server |
| `SERVERS` | List all servers on the network |
| `ROUTE` | Show the network topology graph |
| `SCHEMATIC` | Show the network grid |
| `DARKNET` | Open the exploit shop (buy tools and worms) |
| `MARKET` | Open the black market (buy burner phones, scanners) |
| `SKILLS` | Open the skill tree (stealth, brute-force, phish) |
| `CONFIG` | Show your system stats and settings |
| `UPGRADE` | Open the hardware upgrade shop |
| `MONEY` | Show your credit balance |
| `STORY` | Reveal the plot episode by episode |
| `MISSIONS` | Show active missions |
| `NEWMISSION` | Generate new contracts |
| `LOGOUT` | Disconnect from the current server |
| `TRANSFER [amount]` | Transfer money from the connected server |
| `BOUNCE [host]` | Add a bounce hop to hide your trace |
| `BOUNCEINFO` | Show current bounce chain |
| `BOUNCEHELP` | Bounce usage guide |
| `KILLTRACE` | Pay $500 to reduce trace by 10% |
| `DELETELOGS` | Delete server access logs |
| `PING [host]` | Test connection to a host |
| `TRACEROUTE [host]` | Trace the route to a host |
| `COMBINE [f1] [f2]` | Combine two files in the virus factory |
| `CRYPTO` | Show crypto market |
| `BUYCRYPTO [coin] [amt]` | Buy cryptocurrency |
| `SELLCRYPTO [coin] [amt]` | Sell cryptocurrency |
| `INTEL` | List stolen intelligence |
| `SELLINTEL [id]` | Sell intel on the black market |
| `STORY` | Hacker legend missions |
| `EMAIL` | Read Darius emails |
| `SWITCH` | Final endgame decision |
| `VIEW` | 3D view of connected server |
| `SKILLS` | Skill tree |
| `STATS` | Show your statistics |
| `ALIAS [name] [cmd]` | Create command alias |
| `UNALIAS [name]` | Remove alias |
| `CLEAR` | Clear the terminal |
| `SOUND` | Toggle sound effects |
| `GLITCH` | Trigger a glitch effect |

---

## 🕶️ Darknet Market

Buy named exploits and tools with your hacking profits. Type `DARKNET` to open the shop.

| Exploit | Effect |
|---------|--------|
| `SQL_Injector_v1.exe` | Instantly cracks a database server port |
| `Brute_Force_Tool_v2.exe` | 3× crack speed on target |
| `Packet_Sniffer_v3.exe` | Reveals all hidden neighbor connections |
| `Decrypt_Booster_v1.exe` | Instantly decrypts a server key |
| `Stealth_Kit_v2.exe` | −50% trace for 5 actions |
| `Worm_Deluxe_v4.exe` | Auto-cracks all neighboring servers |
| `Firewall_Bypass_v1.exe` | Suppresses Sentinel AI temporarily |
| `Crypto_Miner_v3.exe` | +50% crypto trading profit |
| `Trace_Killer_v1.exe` | Resets trace to 0% (one-time) |
| `Scan_Probe_v5.exe` | Reveals every server on the network |

Each exploit has a **level requirement** and a **cost**. Once purchased, the file is added to your local storage and can be executed with `EXEC`.

---

## 👻 Ghost in the Machine — Sentinel AI

Sentinel is an adaptive adversary that reacts to your actions in real time. It's not a simple trace bar — it's a Finite State Machine that thinks.

### FSM States

```
DORMANT ──(trace > 30%)──→ ANALYZING ──(trace > 60%)──→ ACTIVE
   ↑                                                        │
   └────────────── (trace < 15% for N ticks) ───────────────┘
```

- **DORMANT** — No threat detected. Normal operations.
- **ANALYZING** — Yellow alerts. Trace signatures being scanned.
  - Random `[SENTINEL]` log messages.
- **ACTIVE** — Red alert! Countermeasures deployed:
  - 🔒 **Close ports** — Sentinel closes randomly cracked ports on your current server.
  - 🗑️ **Delete files** — Removes downloaded files from your local storage.
  - 📈 **Amplify trace** — Increases trace level by 5–15%.

### Countering Sentinel

- **KILLTRACE** — Reduces trace level, helping you slip back to DORMANT.
- **Firewall_Bypass_v1.exe** — Suppresses all Sentinel activity while active.
- **Stay stealthy** — Keep trace below 30% and Sentinel won't wake up.

> *The game becomes a chess match: predict Sentinel's moves, time your actions, and strike when it's dormant.*

---

## 🧠 Architecture — Refactoring Roadmap (5 Phases)

The engine was refactored in 5 phases per `update/Fase-Obiettivo-Azioniconcrete-Deliverable.csv`:

### Phase 1 — Hardening (Data Layer)
- **`engine/models.py`** — Typed dataclasses for all content: `Server`, `Mission`, `Email`, `Exploit`, `HardwareItem`, `GovernmentIntel`. Each model has `from_dict()` for JSON deserialization and `to_dict()` for serialization.
- **`engine/validation.py`** — `ContentValidator` centralizzato. Validates servers, hardware, exploits, missions, emails, gov intel at startup. Errors/warnings collected and reported without crashing.
- **`data/__init__.py`** — All `_load_json` calls now pass through the validator.
- **`data/schema/`** — JSON Schema (Draft-07) files for each content type (`mission_schema.json`, `email_schema.json`, `exploit_schema.json`, `server_schema.json`).
- **`tests/test_data.py`** — 35 unit tests covering models and validation edge cases.

### Phase 2 — Command System
- **`engine/command_registry.py`** — `CommandRegistry` singleton with `CommandMeta` (name, handler, help_text, usage, aliases, min_level, admin_only, category). Decorator-style registration and auto-generated HELP.
- Static `h_help` replaced with **dynamic HELP** generated from the registry — filtered by category, player level, and admin status.
- Commands are now registered with metadata (`_register()` calls at the bottom of `ui/commands.py`).

### Phase 3 — Domain Services
- **`engine/services/__init__.py`** — `EventBus` singleton pub/sub system with `DomainEvent` types. Decouples engine logic from UI.
- **`engine/services/economy_service.py`** — `EconomyService`: money management, purchase validation, crypto market simulation.
- **`engine/services/network_service.py`** — `NetworkService`: scan, connect, neighbor resolution, BFS reachability.
- **`engine/services/trace_service.py`** — `TraceService`: trace level management with state tracking (safe/warning/danger/critical).
- **`engine/services/mission_service.py`** — `MissionService`: mission progress checking, completion, reward dispatching.
- **`engine/services/sentinel_service.py`** — `SentinelService`: wraps the SentinelFSM for game integration with event dispatching.
- `Game.services` container provides access to all services at `g.services.economy`, `g.services.network`, etc.

### Phase 4 — FSM & Event Systems
- **`engine/sentinel.py`** — Dedicated `SentinelFSM` class with states `DORMANT → ANALYZING → ACTIVE`. Observable via domain events (`sentinel.state_changed`, `sentinel.port_closed`, `sentinel.file_deleted`, `sentinel.trace_amplified`).
- Counter-strikes: close ports, delete files, amplify trace. De-escalation when trace drops.
- `SentinelService` wraps the FSM and integrates with the game's event bus.

### Phase 5 — UX & Modding
- **JSON Schema** files in `data/schema/` — validate modded content against a formal schema (Draft-07).
- **`DEBUGSTATE`** command — shows internal state of all FSM, services, event bus, command registry, and game state at a glance.
- **`VALIDATECONTENT`** command — re-runs the ContentValidator on all JSON files at runtime. Instant feedback for modders.

---

## 📡 Random System Events

While you work, the terminal feels alive. Every 20–60 seconds, random system messages appear:

```
[SYSTEM] Maintenance window: 5 minutes.
[NET] Unusual traffic from IP 142.xx.xx.xx
[SEC] Firewall signature updated. 12 new rules deployed.
```

These are purely atmospheric — but they create urgency, making you feel like the network is a living, breathing entity.

---

## 🚀 Installation

### Requirements

- **Python 3.10+**
- **tkinter** (included with Python on Windows/macOS; on Linux: `sudo apt install python3-tk`)

### Setup

```bash
# Clone the repository
git clone https://github.com/404funnotfound/hacker-evolution.git
cd hacker-evolution

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Launch the game
python main.py
```

### Generate the GIF (optional)

To regenerate the demo GIF:

```bash
pip install pillow
python scripts/capture_gif.py
```

This will overwrite `assets/demo.gif`.

---

## 🧱 Project Structure

```
hacker-evolution/
├── main.py                     # Entry point
├── engine/                     # Game engine (logic, not content)
│   ├── __init__.py             # Module exports (CommandRegistry, EventBus, etc.)
│   ├── game.py                 # Game state, network, save/load
│   ├── config.py               # Configuration and colors
│   ├── models.py               # Phase 1: Typed dataclasses (Server, Mission, etc.)
│   ├── validation.py           # Phase 1: ContentValidator
│   ├── sentinel.py             # Phase 4: SentinelFSM (DORMANT→ANALYZING→ACTIVE)
│   ├── command_registry.py     # Phase 2: CommandRegistry singleton
│   └── services/               # Phase 3: Service layer (EventBus + Domain Services)
│       ├── __init__.py         # EventBus, DomainEvent, DomainEventType
│       ├── economy_service.py  # Money, crypto, purchase validation
│       ├── network_service.py  # Scan, connect, reachability
│       ├── trace_service.py    # Trace level management
│       ├── mission_service.py  # Mission lifecycle
│       └── sentinel_service.py # SentinelFSM wrapper
├── ui/                         # User interface (tkinter Canvas + Rich)
│   ├── app.py                  # Main window, layout, event loop (~1300 lines)
│   ├── commands.py             # Command implementations + CommandRegistry wiring
│   ├── hud.py                  # Canvas-drawn animated HUD (vignette, scanlines, data rain)
│   ├── panels.py               # Dialog panels (hardware upgrade, config, etc.)
│   ├── theme.py                # Theme dataclass — palette, spacing, font helpers
│   ├── fonts.py                # FontManager — JetBrains Mono / Consolas discovery
│   ├── rich_bridge.py          # Rich → tkinter Text widget bridge
│   └── widgets/                # Canvas-drawn widget components
│       ├── boot_screen.py      # 6s animated Canvas boot (ASCII art, typing, glitch)
│       ├── stat_card.py        # CanvasStatCard, CanvasSectionHeader
│       ├── sentinel_panel.py   # Sentinel AI animated panel (pulse glow, threat bar)
│       ├── network_map.py      # NetworkMapRenderer (radar grid, data packets, particles)
│       └── alert_overlay.py    # Modal alert overlay (info/warning/error/success)
├── data/                       # 📁 CONTENT — edit these to mod the game
│   ├── __init__.py             # Auto-loader + ContentValidator integration
│   ├── schema/                 # Phase 5: JSON Schema files
│   │   ├── mission_schema.json
│   │   ├── email_schema.json
│   │   ├── exploit_schema.json
│   │   └── server_schema.json
│   ├── missions/               # 📜 Story missions (one file per mission)
│   │   ├── 01_captain_crunch.json
│   │   ├── 02_the_414s.json
│   │   └── ...
│   ├── emails/                 # 📧 Darius emails (one file per email)
│   │   ├── 01_welcome.json
│   │   ├── 02_system_blueprint.json
│   │   └── ...
│   ├── servers.json            # 🌐 Server pool
│   ├── exploits.json           # 🕶️ Darknet exploit definitions
│   ├── gov_intel.json          # 🏛️ Government intel types
│   └── hardware.json           # 🔧 Hardware shop items
├── tests/                      # Phase 1: Unit tests
│   ├── __init__.py
│   └── test_data.py            # 35 tests for models + validation
├── docs/                       # 📖 Documentation
│   └── MODDING.md              # Modding API reference
├── scripts/
│   └── capture_gif.py          # Gameplay GIF capture script
├── assets/
│   ├── demo.gif                # Demo GIF
│   └── screenshot.png          # Static screenshot
└── requirements.txt            # Python dependencies
```

## 🧩 Creating Content (Mod System)

Full documentation: **📖 [docs/MODDING.md](docs/MODDING.md)**

The game loads all missions, emails, and exploits from individual `.json` files. **No Python code to touch.** Just drop a file in the right folder and it works.

### Quick Examples

**📜 Add a mission** — create `data/missions/my_mission.json`:

```json
{
  "id": "my_custom_mission",
  "name": "The Hidden Server",
  "lvl": 3,
  "desc": "Breach the rumored hidden server.",
  "obj_type": "download",
  "obj_file": "classified.db",
  "reward": 2500
}
```

**📧 Add an email** — create `data/emails/my_email.json`:

```json
{
  "sub": "A Friendly Warning",
  "lvl": 4,
  "body": "Nexus deployed new IDS systems.\nUpgrade your firewall.\n— Darius"
}
```

**🕶️ Add a Darknet exploit** — add an entry to `data/exploits.json`:

```json
{
  "id": "my_radar",
  "name": "Radar_Scan_v2.exe",
  "desc": "Reveals all entry points on the network",
  "cost": 1500,
  "level": 2,
  "type": "tool",
  "effect": "global_reveal",
  "content": "# Radar_Scan_v2 — network radar scan"
}
```

### 🧪 Validation

The game **will not crash** if a JSON file has a syntax error. You'll see a friendly warning in the terminal:

```
[ERROR] Data file 'my_mission.json' in data/missions/ is corrupt. Skipping.
```

Fix the file and restart the game.

### 🤝 How to Contribute

1. Fork the repository
2. Add your `.json` file(s) to the appropriate folder
3. Test by running the game locally
4. Submit a Pull Request

Your mission, email, or exploit could be part of the official game!

---

## 🛠 Tech Stack

- **Python 3.10+** — Core language
- **tkinter Canvas** — Full UI rendering (console, stat cards, network map, boot screen, alert overlay, HUD). Every pixel drawn with `create_*` — no images, no customtkinter
- **Rich** — Terminal output formatting (tables, panels, colors) via Rich→tkinter bridge
- **Theme engine** — Dataclass-based palette (16 colors, RGBA helpers) with dark teal/cyan primary and magenta alerts
- **PIL/Pillow** — GIF capture (ancillary script only)
- **Threading** — Async network operations

---

## 📜 License

MIT — feel free to fork, modify, and contribute.

---

<div align="center">
  Built with ☕ by <b>404 Fun Not Found</b><br>
  <sub>*Inspired by Hacker Evolution: Untold (exosyphen studios, 2007)*</sub>
</div>
