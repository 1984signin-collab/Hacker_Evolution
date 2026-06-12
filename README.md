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
| **Dynamic Story** | Unfolds episodically via the STORY command |
| **Hardware System** | RAM, CPU, personal firewall — upgrade your rig |
| **Modular Content** | Missions and emails are individual .json files — add your own without touching code |

### Commands

| Command | Action |
|---|---|
| `HELP` | Show all available commands |
| `SCAN` | Scan local network for active servers |
| `SCANPORTS [IP]` | Scan a server's open ports |
| `CONNECT [IP]` | Connect to a remote server |
| `CRACK` | Crack the firewall of the connected server |
| `LS` | List files on the current server |
| `CAT [file]` | Read a file's contents |
| `DOWNLOAD [file]` | Download a file from the server |
| `UPLOAD [file]` | Upload a file to the server |
| `EXEC [file]` | Execute a file on the server |
| `SERVERS` | List all servers on the network |
| `CONFIG` | Show your system stats |
| `MONEY` | Show your credit balance |
| `STORY` | Reveal the plot episode by episode |
| `LOGOUT` | Disconnect from the current server |
| `TRANSFER [amount] [IP]` | Transfer credits to another hacker |
| `CLEAR` | Clear the terminal |

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
│   ├── gov_intel.json          # 🏛️ Government intel types
│   └── hardware.json           # 🔧 Hardware shop items
├── scripts/
│   └── capture_gif.py          # Gameplay GIF capture script
├── assets/
│   ├── demo.gif                # Demo GIF
│   └── screenshot.png          # Static screenshot
└── requirements.txt            # Python dependencies
```

## 🧩 Creating Content (Mod System)

The game loads all missions and emails from individual `.json` files. **No Python code to touch.** Just drop a file in the right folder and it works.

### 📜 Adding a Mission

Create a new file in `data/missions/` (e.g. `my_mission.json`):

```json
{
  "id": "my_custom_mission",
  "lvl": 3,
  "name": "The Hidden Server",
  "target": null,
  "desc": "Rumors speak of a server no one has ever breached. Find it, crack it, and prove your worth.",
  "obj": "Crack port 443 on a government server and download the file \"classified.db\"",
  "reward": 2500,
  "obj_type": "download",
  "obj_file": "classified.db"
}
```

**Fields explained:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the mission |
| `lvl` | number | Minimum player level to unlock |
| `name` | string | Display name |
| `desc` | string | Lore description |
| `obj` | string | Objective text shown to the player |
| `reward` | number | Money reward on completion |
| `obj_type` | string | Trigger type (`download`, `bounce`, `login`, `combine`, `gsm_transfer`, `levin_heist`, `lamp_upload`, `mckinnon_intel`, `download_multi`, `anon_rising`, `hack`, `crack`, `transfer`, `intel`) |
| `obj_file` | string | (optional) Required file for download missions |
| `obj_count` | number | (optional) Required count for multi-step missions |

### 📧 Adding an Email

Create a new file in `data/emails/` (e.g. `04_hint.json`):

```json
{
  "sub": "A Friendly Warning",
  "lvl": 4,
  "body": "I've heard rumors that Nexus is stepping up their game.\nThey've deployed new intrusion detection systems.\nUpgrade your firewall before hitting the big targets.\n— Darius"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `sub` | string | Subject line |
| `lvl` | number | Level at which the email becomes readable |
| `body` | string | Email body text (use `\n` for line breaks) |

### 🧪 Validation

The game **will not crash** if a JSON file has a syntax error. You'll see a friendly message in the terminal:

```
[ERROR] Data file 'my_mission.json' in data/missions/ is corrupt. Skipping.
```

Fix the file and restart the game.

### 🤝 How to Contribute

> **Want to create content? Just add a `.json` file in `/data/missions/` or `/data/emails/` and submit a Pull Request!**

1. Fork the repository
2. Add your `.json` file(s) to the appropriate folder
3. Test by running the game locally
4. Submit a Pull Request

Your mission could be part of the official game!

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
