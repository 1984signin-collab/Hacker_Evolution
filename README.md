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
| **Hybrid Interface** | Cyberpunk terminal (Rich) + Visual Map (tkinter) |
| **Network Simulation** | Servers, firewalls, ports, real-time connections |
| **Hacking System** | Scan, crack, connect, download, upload, exec |
| **Economy** | Earn credits by selling data, buy upgrades |
| **Darknet Market** | Buy named exploits (SQL injector, brute-force tool, stealth kit, etc.) |
| **Sentinel AI** | Adaptive adversary with DORMANT → ANALYZING → ACTIVE states |
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
│   ├── game.py                 # Game state, network, save/load
│   └── config.py               # Configuration and colors
├── ui/                         # User interface (tkinter + Rich)
│   ├── app.py                  # Main window and event loop
│   ├── commands.py             # Command implementations
│   ├── hud.py                  # Animated heads-up display
│   ├── panels.py               # Side panels and map
│   └── rich_bridge.py          # Rich → tkinter Text widget bridge
├── data/                       # 📁 CONTENT — edit these to mod the game
│   ├── __init__.py             # Auto-loader (reads all .json files)
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

- **Python** — Core language
- **tkinter** — GUI window, map, animated HUD
- **Rich** — Advanced terminal output (tables, panels, progress bars, colors)
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
