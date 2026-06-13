# Hacker Evolution — Game Data
# Carica tutti i dati di gioco dai file JSON nella directory data/
# Permette di modificare la storia senza toccare una riga di Python.
# Le missioni e le email sono caricate da file individuali in
# data/missions/ e data/emails/ — basta creare un nuovo file .json
# per aggiungere contenuto. Il gioco lo rileva automaticamente.
#
# Phase 1 (Hardening): tutti i contenuti sono validati all'avvio
# tramite ContentValidator. Errori e warning sono stampati su stderr
# ma non bloccano il caricamento — la community può moddare senza
# timore di crashare il gioco.

import json
import os
import sys

from engine.validation import ContentValidator

_data_dir = os.path.dirname(__file__)
_validator = ContentValidator()


def _load_json(filename):
    """Carica un singolo file JSON dalla directory data/."""
    path = os.path.join(_data_dir, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _load_json_dir(subdir):
    """Carica tutti i file .json da una sottodirectory, li ordina per 'lvl'.

    Se un file è corrotto, viene saltato con un messaggio di errore
    amichevole nel terminale, senza crashare il gioco.
    Questo permette alla community di aggiungere facilmente nuovi
    contenuti senza rischiare di rompere tutto.
    """
    items = []
    dir_path = os.path.join(_data_dir, subdir)
    if not os.path.isdir(dir_path):
        print(f'[WARN] Directory data/{subdir}/ not found. Skipping.', file=sys.stderr)
        return items
    for filename in sorted(os.listdir(dir_path)):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(dir_path, filename)
        try:
            with open(filepath, encoding='utf-8') as f:
                items.append(json.load(f))
        except (json.JSONDecodeError, ValueError) as e:
            print(
                f"[ERROR] Data file '{filename}' in data/{subdir}/ is corrupt. "
                f"Skipping. ({e})",
                file=sys.stderr,
            )
        except OSError as e:
            print(
                f"[ERROR] Could not read data/{subdir}/{filename}: {e}",
                file=sys.stderr,
            )
    # Ordina per livello di gioco per consistenza tra esecuzioni
    items.sort(key=lambda x: x.get('lvl', 999))
    return items


# ── Server pool ──
# Lista di [name, ports, key_bits, [[filename, content], ...], money, desc]
SERVERS_POOL = _validator.validate_server_pool(_load_json('servers.json'))

# ── Government intel types ──
# {"types": [[id, desc, value, size], ...], "domains": [...]}
_gov = _validator.validate_gov_intel(_load_json('gov_intel.json'))
GOV_INTEL_TYPES = _gov['types']
GOV_DOMAINS = _gov['domains']

# ── Story missions ── (caricate da file individuali in data/missions/)
STORY_MISSIONS = _validator.validate_story_missions(_load_json_dir('missions'))

# ── Darius emails ── (caricate da file individuali in data/emails/)
DARIUS_EMAILS = _validator.validate_emails(_load_json_dir('emails'))

# ── Hardware shop ──
HARDWARE = _validator.validate_hardware(_load_json('hardware.json'))

# ── Darknet exploits ──
EXPLOITS = _validator.validate_exploits(_load_json('exploits.json'))

# ── Report validation results ──
_validator.report()
