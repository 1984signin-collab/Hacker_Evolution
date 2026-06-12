# Hacker Evolution — Modding API

> "The terminal is your canvas. The network, your playground."

Hacker Evolution supports custom content through simple JSON files. You don't need to write Python code — just create a `.json` file in the right directory, and the game loads it automatically.

---

## 📁 Project Structure

```
Hacker_Evolution/
├── data/
│   ├── missions/        ← Your custom story missions go here
│   ├── emails/          ← Your custom Darius emails go here
│   ├── servers.json     ← Server pool
│   ├── exploits.json    ← Darknet exploit definitions
│   ├── hardware.json    ← Hardware upgrade specs
│   └── gov_intel.json   ← Government intel types
├── docs/                ← This file
├── engine/              ← Game engine (Python)
├── locales/             ← Translation files (.po)
└── ui/                  ← Terminal UI (Python)
```

---

## 📜 Adding a New Story Mission

Create a `.json` file in `data/missions/`. The game loads all missions in this directory and sorts them by `lvl`.

### Example: `data/missions/my_mission.json`

```json
{
  "id": "my_custom_mission",
  "name": "Phantom Protocol",
  "lvl": 3,
  "desc": "Infiltrate the secure archive and download the phantom protocol.",
  "obj_type": "download",
  "obj_file": "phantom_protocol.pdf",
  "reward": 5000,
  "dialogue": [
    {
      "from": "Darius",
      "text": "There's a file on nexus.owc called phantom_protocol.pdf. I need it."
    },
    {
      "from": "System",
      "text": "New legend mission available: Phantom Protocol"
    }
  ]
}
```

### Objective Types (`obj_type`)

| Type              | Description                              | Required Fields     |
|-------------------|------------------------------------------|---------------------|
| `download`        | Download a specific file                 | `obj_file`          |
| `login`           | Successfully log into any server         | —                   |
| `bounce`          | Build a bounce chain of N hops           | `obj_count`         |
| `combine`         | Combine two files in the virus factory   | —                   |
| `gsm_transfer`    | Buy a GSM burner and make a transfer     | —                   |
| `levin_heist`     | Steal money via bounce chain             | `obj_count`         |
| `mckinnon_intel`  | Sell stolen intelligence                 | —                   |
| `download_multi`  | Download N files total                   | `obj_count`         |
| `lamp_upload`     | Upload a file to a server                | —                   |
| `anon_rising`     | Hack gov servers + use bounces           | —                   |

### Mission Fields

| Field       | Type    | Description                                  |
|-------------|---------|----------------------------------------------|
| `id`        | string  | Unique identifier (no spaces)                |
| `name`      | string  | Display name                                 |
| `lvl`       | number  | Minimum player level to unlock               |
| `desc`      | string  | Brief description                            |
| `obj_type`  | string  | One of the objective types above             |
| `obj_file`  | string  | Required for `download` type                 |
| `obj_count` | number  | Required for `bounce`, `download_multi`      |
| `reward`    | number  | Money reward for completion                  |
| `dialogue`  | array   | Optional story text shown on unlock          |

---

## 📧 Adding a New Email from Darius

Create a `.json` file in `data/emails/`. Emails are sorted by `lvl` and only shown when the player reaches that level.

### Example: `data/emails/darknet_intro.json`

```json
{
  "id": "darknet_intro",
  "lvl": 2,
  "sub": "Access to the Darknet",
  "body": "I've left you credentials for the Darknet marketplace.\n\nUse the DARKNET command to buy exploits.\n\nStart with SQL_Injector_v1.exe — it'll crack database servers instantly.\n\n— Darius"
}
```

### Email Fields

| Field  | Type    | Description                        |
|--------|---------|------------------------------------|
| `id`   | string  | Unique identifier                  |
| `lvl`  | number  | Level required to unlock           |
| `sub`  | string  | Email subject line                 |
| `body` | string  | Email body (use `\n` for newlines) |

---

## 🖥️ Adding a New Darknet Exploit

Edit `data/exploits.json` to add purchasable tools. (Restart required.)

### Example Entry

```json
{
  "id": "my_radar_tool",
  "name": "Radar_Scan_v2.exe",
  "desc": "Reveals all entry points on the network",
  "cost": 1500,
  "level": 2,
  "type": "tool",
  "effect": "global_reveal",
  "content": "# Radar_Scan_v2\n# Network radar scan\n# Usage: EXEC Radar_Scan_v2.exe\n# Reveals all entry servers."
}
```

### Exploit Fields

| Field     | Type   | Description                                    |
|-----------|--------|------------------------------------------------|
| `id`      | string | Unique identifier                              |
| `name`    | string | Display filename (shown in `LS`)               |
| `desc`    | string | Short description                              |
| `cost`    | number | Purchase price                                 |
| `level`   | number | Minimum player level to buy                    |
| `type`    | string | `exploit`, `tool`, `worm`, or `scanner`        |
| `effect`  | string | Gameplay effect (see below)                    |
| `content` | string | File content when downloaded to local storage  |

### Available Effects (`effect`)

| Effect           | Description                                      |
|------------------|--------------------------------------------------|
| `instant_crack`  | Instantly cracks a target port                   |
| `speed_crack`    | 3x crack speed on target                         |
| `reveal_network` | Reveals all neighbor connections                 |
| `speed_decrypt`  | Instant server decryption                        |
| `stealth_boost`  | -50% trace for 5 actions                         |
| `auto_spread`    | Auto-cracks all neighboring servers              |
| `sentinel_bypass`| Suppresses Sentinel AI temporarily               |
| `crypto_boost`   | +50% crypto trading profit                       |
| `trace_reset`    | Resets trace to 0% (one-time)                    |
| `global_reveal`  | Reveals every server on the network              |

---

## 🌐 Adding New Servers

Edit `data/servers.json`. Each entry is an array:

```json
[
  "server-name.corp.com",
  [22, 80, 443],
  1024,
  [["welcome.txt", "Welcome to the server."]],
  50000,
  "Internal corporate server — HR database",
  ["neighbor-1.corp.com", "neighbor-2.corp.com"]
]
```

### Server Array Fields

| Index | Type   | Description                           |
|-------|--------|---------------------------------------|
| 0     | string | Hostname                              |
| 1     | array  | Open port numbers                     |
| 2     | number | Encryption key bits (512–4096)        |
| 3     | array  | Files: `[[name, content], ...]`       |
| 4     | number | Available money to steal              |
| 5     | string | Description shown on `SCAN`           |
| 6     | array  | Neighbor hostnames (for network map)  |

---

## 🛠️ Hardware Upgrades

Edit `data/hardware.json`:

```json
["Firewall","firewall","Doubles trace time",500,2.2,10]
```

| Index | Type   | Description                        |
|-------|--------|------------------------------------|
| 0     | string | Display name                       |
| 1     | string | Internal type identifier           |
| 2     | string | Description text                   |
| 3     | number | Base cost                          |
| 4     | number | Cost multiplier per level          |
| 5     | number | Maximum level                      |

---

## 🔧 Advanced: Python Hooks

The game engine (`engine/game.py`) has extension points:

- `Game.sentinel_tick()` — called on every player command
- `Game.random_event()` — generates system events
- `Game.check_achievements()` — called after significant actions
- `Game.check_story_missions(action)` — called on downloads, bounces, etc.

These are designed to be overridden or extended by subclassing `Game`, but the JSON-based content system is the recommended approach for most mods.

---

## ✅ Contribution Guidelines

1. Fork the repository
2. Create your content file in the appropriate `data/` subdirectory
3. Test it works with the game
4. Open a Pull Request with a clear description of your addition

Your mission, email, or exploit may be included in the next official update!

> "Every great hacker started by modifying the tools they were given."
