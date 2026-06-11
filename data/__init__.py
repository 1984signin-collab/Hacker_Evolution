# Hacker Evolution — Game Data
# Carica tutti i dati di gioco dai file JSON nella directory data/
# Permette di modificare la storia senza toccare una riga di Python.

import json
import os

_data_dir = os.path.dirname(__file__)


def _load_json(filename):
    path = os.path.join(_data_dir, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


# ── Server pool ──
# Lista di [name, ports, key_bits, [[filename, content], ...], money, desc]
SERVERS_POOL = _load_json('servers.json')

# ── Government intel types ──
# {"types": [[id, desc, value, size], ...], "domains": [...]}
_gov = _load_json('gov_intel.json')
GOV_INTEL_TYPES = _gov['types']
GOV_DOMAINS = _gov['domains']

# ── Story missions ──
STORY_MISSIONS = _load_json('missions.json')

# ── Darius emails ──
DARIUS_EMAILS = _load_json('emails.json')

# ── Hardware shop ──
HARDWARE = _load_json('hardware.json')
