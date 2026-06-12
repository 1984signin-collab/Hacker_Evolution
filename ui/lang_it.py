#!/usr/bin/env python3
"""Italian string dictionary: English → Italian mappings."""
STRINGS = {
    # ── _connected helper ──
    'Not connected to a server.': 'Non connesso a un server.',
    'Money: ${:,}': 'Soldi: ${:,}',
    '=== LEVEL {} ===': '═══ LIVELLO {} ═══',
    '── LOCAL ({}/{} blocks) ──': '── LOCALE ({}/{} blocks) ──',
    'Sound: {}': 'Suono: {}',

    # ── h_help ──
    'AVAILABLE COMMANDS': 'COMANDI DISPONIBILI',
    'Help': 'Aiuto',
    'Find server': 'Trova server',
    'Connect': 'Connettiti',
    'Disconnect': 'Disconnetti',
    'Brute force password': 'Forza password',
    'Decrypt key': 'Decifra chiave',
    'Login with password': 'Accedi con password',
    'List files': 'Lista file',
    'Show file': 'Mostra file',
    'Download': 'Scarica',
    'Upload': 'Carica',
    'Delete': 'Cancella',
    'Transfer money': 'Trasferisci soldi',
    'Run exploit': 'Esegui exploit',
    'Add/remove bounce': 'Aggiungi/rimuovi bounce',
    'Bounce chain': 'Catena bounce',
    'Bounce help': 'Aiuto bounce',
    '-10% trace ($500)': '-10% trace ($500)',
    'Delete server logs': 'Cancella log server',
    'Show hardware': 'Mostra hardware',
    'Upgrade menu': 'Menu upgrade',
    'Next level': 'Prossimo livello',
    'Money': 'Soldi',
    'All servers': 'Tutti i server',
    'Scan ports': 'Scansiona porte',
    'Connection test': 'Test connessione',
    'Trace route': 'Traccia percorso',
    'Network grid': 'Reticolo rete',
    'Active missions': 'Missioni attive',
    'Generate missions': 'Genera missioni',
    'Unlocked trophies': 'Trofei sbloccati',
    'Crypto market': 'Mercato crypto',
    'Buy crypto': 'Compra crypto',
    'Sell crypto': 'Vende crypto',
    'Stolen intelligence list': 'Lista intelligence rubate',
    'Sell intel on black market': 'Vendi intel al mercato nero',
    'Black market': 'Mercato nero',
    'Hacker legend missions': 'Missioni leggende hacker',
    'Read Darius emails': 'Leggi email Darius',
    'Final switch (endgame only)': 'Interruttore finale (solo endgame)',
    'Virus factory': 'Fabbrica virus',
    'Skill tree': 'Skill tree',
    'Create alias': 'Crea alias',
    'Remove alias': 'Rimuovi alias',
    '3D server view': 'Vista 3D server',
    'Stats': 'Statistiche',
    'Glitch effect': 'Effetto glitch',
    'Toggle sound': 'Toggle suono',
    'New game': 'Nuova partita',

    # ── h_servers ──
    'Status': 'Stato',
    'Type': 'Tipo',
    'Name': 'Nome',
    'Description': 'Descrizione',
    'Mission': 'Missione',
    'Reward': 'Ricompensa',

    # ── h_money ──
    'Money: ${}': 'Soldi: ${}',

    # ── h_ls ──
    'LOCAL ({}/{} blocks)': 'LOCALE ({}/{} blocks)',

    # ── h_cat ──
    'Use: CAT <file>': 'Usa: CAT <file>',
    'File not found: {}': 'File non trovato: {}',

    # ── h_delete ──
    'Use: DELETE <file>': 'Usa: DELETE <file>',
    'TRACED!': 'TRACED!',
    '{} deleted.': '{} eliminato.',

    # ── h_scan ──
    'Use: SCAN <host>': 'Usa: SCAN <host>',
    '\n[+] Server FOUND: {}': '\n[+] Server TROVATO: {}',
    '    Ports: {}': '    Porte: {}',
    '    Key: {} bits': '    Chiave: {} bits',
    '    Status: {}': '    Stato: {}',
    'ENCRYPTED': 'CIFRATO',
    'DECRYPTED': 'DECIFRATO',
    '[-] Host not found: {}': '[-] Host non trovato: {}',

    # ── h_scanports ──
    'Use: SCANPORTS <host>': 'Usa: SCANPORTS <host>',
    'Unknown host: {}': 'Host sconosciuto: {}',
    'Scanning ports on {}...': 'Scansione porte su {}...',
    '  Port {}: {}': '  Porta {}: {}',
    'FILTERED': 'FILTRATA',
    'OPEN': 'APERTA',

    # ── h_connect ──
    'Use: CONNECT <host> [port]': 'Usa: CONNECT <host> [port]',
    'Unknown: {}': 'Sconosciuto: {}',
    'Scan {} first': 'Scansiona prima {}',
    'Decrypt {} first': 'Decifra prima {}',
    'Crack {}:{} first': 'Cracka prima {}:{}',
    '[+] Connected to {}:{}': '[+] Connesso a {}:{}',

    # ── h_logout ──
    'Disconnected from {}': 'Disconnesso da {}',
    'Not connected.': 'Non connesso.',

    # ── h_crack ──
    'Use: CRACK <host> [port]': 'Usa: CRACK <host> [port]',
    'Port {} not found': 'Porta {} non trovata',
    'Brute forcing {}:{}... ({} chars)': 'Brute force su {}:{}... ({} chars)',

    # ── h_decrypt ──
    'Use: DECRYPT <host>': 'Usa: DECRYPT <host>',
    '{} already decrypted.': '{} già decifrato.',
    'Decrypting key {} bits...': 'Decifratura chiave {} bits...',

    # ── h_login ──
    'Use: LOGIN <host> <password>': 'Usa: LOGIN <host> <password>',
    '[+] Access to {}:{}': '[+] Accesso a {}:{}',
    'Wrong password.': 'Password errata.',

    # ── h_download ──
    'Use: DOWNLOAD <file>': 'Usa: DOWNLOAD <file>',
    'Download: {} ({}/{})': 'Download: {} ({}/{})',
    'Memory full!': 'Memoria piena!',

    # ── h_upload ──
    'Use: UPLOAD <file>': 'Usa: UPLOAD <file>',
    'Upload: {}': 'Upload: {}',
    'File not found locally: {}': 'File non trovato in locale: {}',

    # ── h_exec ──
    'Use: EXEC <exploit> <host>': 'Usa: EXEC <exploit> <host>',
    'Invalid port.': 'Porta non valida.',
    '[+] Exploit {} executed on {}!': '[+] Exploit {} eseguito su {}!',
    'Exploit not found.': 'Exploit non trovato.',

    # ── h_transfer ──
    'Use: TRANSFER <amount>': 'Usa: TRANSFER <amount>',
    'Invalid amount.': 'Importo non valido.',
    'Server only has ${}': 'Il server ha solo ${}',
    'Transfer ${}...': 'Trasferimento ${}...',

    # ── h_abort ──
    'Cancelled.': 'Annullato.',

    # ── h_config ──
    'HARDWARE CONFIG': 'HARDWARE CONFIG',
    'Component': 'Component',
    'Level': 'Level',
    'Progress': 'Progress',
    'Effect': 'Effect',
    'Memory:': 'Memoria:',
    'Trace:': 'Trace:',
    'Money:': 'Soldi:',

    # ── h_nextlevel ──
    'Moving to next level...': 'Passando al livello successivo...',
    'Level {lvl} unlocked — new targets available': 'Livello {lvl} sbloccato — nuovi target disponibili',
    '=== LEVEL {} ===': '=== LIVELLO {} ===',
    'Generated {} missions.': 'Generate {} missioni.',
    '📧 NEW EMAIL: {} (type EMAIL)': '📧 NUOVA EMAIL: {} (digita EMAIL)',
    '📜 STORY UNLOCKED: {} (type STORY)': '📜 STORY SBLOCCATA: {} (digita STORY)',
    '{} unlocked!': '{} sbloccata!',
    '📜 {} unlocked!': '📜 {} sbloccata!',
    '🏆 Achievement unlocked: {} (+${})': '🏆 Achievement sbloccato: {} (+${})',

    # ── h_newgame ──
    'New Game': 'Nuova Partita',
    'Restart? All progress will be lost.': 'Ricominciare? Tutti i progressi andranno persi.',
    '=== NEW GAME ===': '=== NUOVA PARTITA ===',
    'Type HELP for commands.': 'Digita HELP per i comandi.',
    'New game started.': 'Nuova partita iniziata.',

    # ── h_bounce ──
    'Use: BOUNCE <host>': 'Usa: BOUNCE <host>',
    'Disconnect first.': 'Disconnettiti prima.',
    '{} not hacked.': '{} non hackerato.',
    '{} has no bounces left.': '{} ha finito i rimbalzi.',
    '{} removed from bounce.': '{} rimosso dal bounce.',
    '{} added to bounce. ({} hop)': '{} aggiunto al bounce. ({} hop)',

    # ── h_bounceinfo ──
    'Empty chain.': 'Catena vuota.',
    'Chain ({} hop):': 'Catena ({} hop):',
    'Trace multiplier: {}x': 'Trace multiplier: {}x',

    # ── h_bouncehelp ──
    'BOUNCE HELP': 'BOUNCE HELP',
    'Bounced links increase trace time.': 'I bounced link aumentano il tempo di trace.',
    'Use BOUNCE <host> to add hacked servers.': 'Usa BOUNCE <host> per aggiungere server hackerati.',
    'Trace time = base × (hop+1) × firewall bonus': 'Trace time = base × (hop+1) × firewall bonus',
    'Max 3 bounces per server.': 'Max 3 rimbalzi per server.',
    'You cannot modify bounce while connected.': 'Non puoi modificare il bounce mentre sei connesso.',

    # ── h_killtrace ──
    'Need $500.': 'Servono $500.',
    'Trace reduced to {:.1f}% (-$500)': 'Trace ridotto a {:.1f}% (-$500)',

    # ── h_deletelogs ──
    'Logs deleted. Trace: {:.1f}%': 'Log cancellati. Trace: {:.1f}%',

    # ── _progress ──
    '[+] Password CRACKED on {}:{}!': '[+] Password CRACKATA su {}:{}!',
    '[+] Key DECRYPTED on {}!': '[+] Chiave DECIFRATA su {}!',
    '[+] Transferred ${}': '[+] Trasferiti ${}',
    '⚠️ TRACE 100%! GAME OVER!': '⚠️ TRACE 100%! GAME OVER!',

    # ── h_sound ──
    'Sound: ON': 'Suono: ON',
    'Sound: OFF': 'Suono: OFF',

    # ── h_ping ──
    'Use: PING <host>': 'Usa: PING <host>',
    'PING {}...': 'PING {}...',
    '  Reply from {}: bytes=64 time={}ms TTL={}': '  Risposta da {}: byte=64 tempo={}ms TTL={}',
    '  --- statistics ---': '  --- statistics ---',
    '  Packets: sent=4 received=4 lost=0': '  Pacchetti: inviati=4 ricevuti=4 persi=0',

    # ── h_traceroute ──
    'Use: TRACEROUTE <host>': 'Usa: TRACEROUTE <host>',
    'Traceroute to {}...': 'Traceroute verso {}...',

    # ── h_schematic ──
    'SCHEMATIC — Network Grid': 'SCHEMATIC — Reticolo Rete',

    # ── h_crypto ──
    'CRYPTOCURRENCIES': 'CRYPTOVALUTE',
    '  Total crypto wallet: ${:,.0f}': '  Totale portafoglio crypto: ${:,.0f}',
    '  Use: BUYCRYPTO <coin> <amount>  |  SELLCRYPTO <coin> <amount>': '  Usa: BUYCRYPTO <coin> <amount>  |  SELLCRYPTO <coin> <amount>',
    '  Coins: BTC, ETH, XMR': '  Coins: BTC, ETH, XMR',

    # ── h_buycrypto ──
    'Use: BUYCRYPTO <coin> <amount>': 'Usa: BUYCRYPTO <coin> <amount>',
    'Invalid coin. BTC, ETH, XMR': 'Coin non valida. BTC, ETH, XMR',
    'Need ${:,.0f}': 'Servono ${:,.0f}',
    'Bought {:.4f} {} for ${:,.0f}': 'Comprati {:.4f} {} per ${:,.0f}',
    'Crypto purchase: {:.2f} {}': 'Acquisto crypto: {:.2f} {}',

    # ── h_sellcrypto ──
    'Use: SELLCRYPTO <coin> <amount>': 'Usa: SELLCRYPTO <coin> <amount>',
    'You only have {:.4f} {}': 'Hai solo {:.4f} {}',
    'Sold {:.4f} {} for ${:,}': 'Venduti {:.4f} {} per ${:,}',

    # ── h_combine ──
    'Use: COMBINE <file1> <file2>': 'Usa: COMBINE <file1> <file2>',
    'File not found.': 'File non trovato.',
    '[+] Created {} from {} + {}!': '[+] Creato {} dai file {} + {}!',
    'No valid combination. Try exploit + bin.': 'Nessuna combinazione valida. Prova exploit + bin.',

    # ── h_story ──
    'HACKER LEGEND MISSIONS': 'MISSIONI LEGGENDE HACKER',
    'COMPLETED': 'COMPLETATA',
    'ACTIVE': 'ATTIVA',
    'AVAILABLE': 'DISPONIBILE',
    'LOCKED': 'BLOCCATA',
    'Completed:': 'Completate:',
    '[bold green]Completed:[/] {}/{}': '[bold green]Completate:[/] {}/{}',

    # ── h_intel ──
    'No stolen intelligence.': 'Nessuna intelligence rubata.',
    '📁 STOLEN INTELLIGENCE': '📁 INTELLIGENCE RUBATE',
    'Use SELLINTEL <id> to sell on the black market.': 'Usa SELLINTEL <id> per vendere al mercato nero.',

    # ── h_sellintel ──
    'Use: SELLINTEL <id>  (see INTEL for list)': 'Usa: SELLINTEL <id>  (vedi INTEL per la lista)',
    'Invalid ID.': 'ID non valido.',
    'ID {} not found. Use INTEL for list.': 'ID {} non trovato. Usa INTEL per la lista.',
    '[+] Intelligence sold: {} for ${:,}': '[+] Intelligence venduta: {} per ${:,}',

    # ── h_alias / h_unalias ──
    'Active aliases:': 'Alias attivi:',
    'No aliases.': 'Nessun alias.',
    'Alias: {} → {}': 'Alias: {} → {}',
    'Use: UNALIAS <name>': 'Usa: UNALIAS <nome>',
    'Alias {} removed.': 'Alias {} rimosso.',

    # ── h_stats ──
    'DETAILED STATISTICS': 'STATISTICHE DETTAGLIATE',
    '  Hacked servers:     {}/{}': '  Server hackerati:     {}/{}',
    '  Hack attempts:    {}': '  Tentativi di hack:    {}',
    '  Transfers:        {}': '  Trasferimenti:        {}',
    '  Money stolen:         ${:,}': '  Soldi rubati:         ${:,}',
    '  Bounces used:         {}': '  Bounce usati:         {}',
    '  Missions completed:  {}': '  Missioni completate:  {}',
    '  Max trace:        {:.1f}%': '  Trace massima:        {:.1f}%',
    '  Level:              {}': '  Livello:              {}',
    '  Total money:         ${:,}': '  Soldi totali:         ${:,}',
    '  Score:                {:,}': '  Score:                {:,}',
    '  Play time:          --': '  Tempo gioco:          --',

    # ── h_email ──
    'No emails from Darius.': 'Nessuna email da Darius.',
    '📧 EMAIL — Darius': '📧 EMAIL — Darius',
    '  Subject: {}': '  Oggetto: {}',
    '  (Level {})': '  (Livello {})',

    # ── h_config (stats line) ──
    '  Memory: {}/{} blk  Trace: {:.1f}%  Money: ${:,}': '  Memoria: {}/{} blk  Trace: {:.1f}%  Soldi: ${:,}',

    # ── Rich table titles ──
    'SERVERS ({})': 'SERVER ({})',
    'HARDWARE CONFIG': 'HARDWARE CONFIG',
    '[bold yellow]AVAILABLE COMMANDS[/]': '[bold yellow]COMANDI DISPONIBILI[/]',
    '[bold yellow]HACKER LEGEND MISSIONS[/]': '[bold yellow]MISSIONI LEGGENDE HACKER[/]',

    # ── Game newstemplates (engine/game.py) ──
    'Level {lvl} unlocked — new targets available': 'Livello {lvl} sbloccato — nuovi target disponibili',
    'Server breached! {h}:{p} compromised.': 'Server violato! {h}:{p} compromesso.',
    'Key decrypted for {h}': 'Chiave decifrata per {h}',
    'Funds transferred: ${a} from {h}': 'Fondi trasferiti: ${a} da {h}',
    'Intel {i} sold on black market (+${p})': 'Intel {i} venduto al mercato nero (+${p})',
    'Crypto purchase: {a:.2f} {c}': 'Acquisto crypto: {a:.2f} {c}',
    'Exploit {e} deployed on {h}': 'Exploit {e} deployed su {h}',
    'System online. Darius legacy active.': 'System online. Darius legacy attivo.',
    'New game started.': 'Nuova partita iniziata.',
    'Crack: {}:{}': 'Crack: {}:{}',
    'Decrypt: {}': 'Decrypt: {}',
    'Transfer: ${}': 'Transfer: ${}',
    'GAME OVER - Trace 100%': 'GAME OVER - Trace 100%',
    'Level {} started!': 'Livello {} iniziato!',

    # ── app.py UI labels ──
    'SYSTEM PANEL': 'SYSTEM PANEL',
    ' MONEY ': ' 💰 Soldi ',
    ' TRACE ': ' ⚠️ Trace ',
    ' SCORE ': ' 🏆 Score ',
    ' LEVEL ': ' 📊 Level ',
    ' HACK ': ' 💻 Hack ',
    ' TRACED ': ' 🕵️ Traced ',
    ' BOUNCE ': ' 🔁 BOUNCE ',
    ' HARDWARE ': ' HARDWARE ',
    ' MESSAGES ': ' MESSAGES ',
    'Save': '💾 Salva',
    'Load': '📂 Carica',
    'Export': '📤 Esporta',
    'Import': '📥 Importa',
    'Upgrade': '🔧 Aggiorna',
    'CONSOLE': '▶ CONSOLE',
    '[F1=Help]': '[F1=Help]',

    # ── Menu ──
    'File': 'File',
    'New Game': '🆕 Nuova Partita',
    'Save': '💾 Salva',
    'Load': '📂 Carica',
    'Export...': '📤 Esporta...',
    'Import...': '📥 Importa...',
    'Exit': '🚪 Esci',

    # ── app.py boot/console messages ──
    '\n📧 YOU HAVE 1 NEW EMAIL from Darius. Type EMAIL to read it.': '\n📧 HAI 1 NUOVA EMAIL da Darius. Digita EMAIL per leggerla.',
    'Type HELP for commands.': 'Digita HELP per i comandi.',
    'Type HELP for commands. EMAIL to read Darius.': 'Digita HELP per i comandi. EMAIL per leggere Darius.',
    'Recent news:': 'Notizie recenti:',
    'OBJECTIVES': 'OBIETTIVI',
    '  F2=Objectives  F5=Missions  F6=Achievement  F7=News': '  F2=Obiettivi  F5=Missioni  F6=Achievement  F7=Notizie',
    'No active missions. Type NEWMISSION to generate.': 'Nessuna missione attiva. Digita NEWMISSION per generarli.',
    'ACTIVE MISSIONS': 'MISSIONI ATTIVE',
    'Use NEWMISSION for new missions.': 'Usa NEWMISSION per nuove missioni.',
    'Game saved!': 'Partita salvata!',
    'Game loaded!': 'Partita caricata!',
    'No save found.': 'Nessun salvataggio trovato.',
    'Imported!': 'Importato!',
    'Invalid file.': 'File non valido.',
    # f-strings
    'Unknown command: {}. Type HELP.': 'Comando sconosciuto: {}. Digita HELP.',
    'Key: {}b  Money: ${}  Files: {}': 'Chiave: {}b  Soldi: ${}  Files: {}',
    '  Hacked servers: {}/{}': '  Server hackerati: {}/{}',
    '  Money: ${:,}  |  Score: {}': '  💰 Soldi: ${:,}  |  Score: {}',
    '  Level: {}  |  Achievement: {}/{}': '  📈 Livello: {}  |  🏆 Achievement: {}/{}',
    '  Missions: {}/{} completed': '  📋 Missioni: {}/{} completate',
    'Generated {} new missions!': 'Generate {} nuove missioni!',
    'Exported: {}': 'Esportato: {}',

    # ── h_switch, h_missions, h_view, etc (panels.py) ──
    'Intel already extracted from this server.': 'Intel già estratto da questo server.',
    '[+] INTELLIGENCE EXTRACTED: {} (value ${:,})': '[+] INTELLIGENCE ESTRATTA: {} (valore ${:,})',
    '    Sell on black market with SELLINTEL <id>': '    Vendi al mercato nero con SELLINTEL <id>',
    '[+] {} upgraded to LVL {}!': '[+] {} aggiornato a LVL {}!',
    '[GSM] Burner phone purchased. Use it for covert ops.': '[GSM] Cellulare usa e getta acquistato. Usalo per operazioni coperte.',
    '[+] Purchased: {}': '[+] Acquistato: {}',
    '[+] Skill {} upgraded!': '[+] Skill {} potenziata!',
    'You must complete all legend missions first.': 'Devi completare tutte le missioni leggenda prima.',
    'Completed: {}/{}': 'Completate: {}/{}',
    'You already made a choice.': 'Hai già preso una decisione.',
    'NEXUS CORE MAINFRAME': 'NEXUS CORE MAINFRAME',
    'OVERWATCH — GLOBAL SURVEILLANCE SYSTEM': 'OVERWATCH — SISTEMA DI SORVEGLIANZA GLOBALE',
    ' 🔓  RELEASE EVERYTHING TO THE PUBLIC': ' 🔓  RENDI TUTTO PUBBLICO',
    ' 🔒  DELETE EVERYTHING FOREVER': ' 🔒  CANCELLA TUTTO PER SEMPRE',
    'Connected on port {}': 'Connesso su porta {}',
    'Close': 'Chiudi',

    # ── h_switch dialog ──
    'You must complete all legend missions first.': 'Devi completare tutte le missioni leggenda prima.',

    # ── Language command ──
    'Language set to English.': 'Lingua impostata su Italiano.',
    'Current language: {}': 'Lingua corrente: {}',
    'Use: LANG <en|it>': 'Usa: LANG <en|it>',
    'Available languages: en (English), it (Italiano)': 'Lingue disponibili: en (English), it (Italiano)',

    # ── Added translations ──
    '🇺🇸  UNITED STATES GOVERNMENT': '🇺🇸  GOVERNO DEGLI STATI UNITI',
    '⚠  WARNING: This system is for authorized use only. All access is monitored and logged.  ⚠': '⚠  ATTENZIONE: Questo sistema è solo per uso autorizzato. Tutti gli accessi sono monitorati e registrati.  ⚠',
    'SECURE LOGIN': 'ACCESSO SICURO',
    'Username:': 'Nome utente:',
    'Password:': 'Password:',
    '  SIGN IN  ': '  ACCEDI  ',
    'Cancel': 'Annulla',
    'Portal Login — {}': 'Login Portale — {}',
    'Server: {}': 'Server: {}',
    'CLASSIFIED — {}': 'CLASSIFICATO — {}',
    '🇺🇸  DEPARTMENT OF {}': '🇺🇸  DIPARTIMENTO DI {}',
    'DEFENSE': 'DIFESA',
    'HOMELAND SECURITY': 'SICUREZZA INTERNA',
    'JUSTICE': 'GIUSTIZIA',
    'STATE': 'STATO',
    'TOP SECRET // {} // {}': 'TOP SECRET // {} // {}',
    '📁  {}': '📁  {}',
    '⬇  EXTRACT INTELLIGENCE  ⬇': '⬇  ESTRAI INTELLIGENCE  ⬇',
    '✓  Intel already extracted.': '✓  Intel già estratto.',
    'CLOSE to return to terminal': 'CHIUDI per tornare al terminale',
    'CLOSE PORT': 'CHIUDI PORTA',
    'Intel {i} stolen from {h}!': 'Intel {i} rubato da {h}!',
    '🔧 Hardware Upgrade': '🔧 Aggiornamento Hardware',
    '╔══ UPGRADE HARDWARE ══╗': '╔══ AGGIORNA HARDWARE ══╗',
    'LVL {}/{}': 'LVL {}/{}',
    '⬆ UP': '⬆ AGGIORNA',
    'MAX ✓': 'MAX ✓',
    '💰 ${:,}': '💰 ${:,}',
    '[{}] {}': '[{}] {}',
    '🧠 Skill Tree': '🧠 Skill Tree',
    '╔══ SKILL TREE ══╗': '╔══ SKILL TREE ══╗',
    'Available points: {}': 'Punti disponibili: {}',
    'LVL {}': 'LVL {}',
    'NEXUS Core — Switch': 'Switch Nexus Core',
    '╔══ NEXUS CORE MAINFRAME ══╗': '╔══ NEXUS CORE MAINFRAME ══╗',
    'OVERWATCH — GLOBAL SURVEILLANCE SYSTEM': 'OVERWATCH — SISTEMA DI SORVEGLIANZA GLOBALE',
    '  YOU HAVE ACCESS TO THE MAIN SWITCH.': '  HAI ACCESSO ALL\'INTERRUTTORE PRINCIPALE.',
    '  ONE CHOICE. NO TURNING BACK.': '  UNA SCELTA. NESSUN DIETROFRONT.',
    '🔓  RELEASE EVERYTHING TO THE PUBLIC': '🔓  RENDI TUTTO PUBBLICO',
    '🔒  DELETE EVERYTHING FOREVER': '🔒  CANCELLA TUTTO PER SEMPRE',
    '  NEXUS CORPORATION DATABASE MADE PUBLIC': '  DATABASE NEXUS CORPORATION RESO PUBBLICO',
    '  2.4 billion profiles. 12,847 illegal transactions.': '  2.4 miliardi di profili. 12.847 transazioni illegali.',
    '  34 governments. 7 murders. 12 manipulated elections.': '  34 governi. 7 omicidi. 12 elezioni manipolate.',
    '  EVERYTHING ONLINE. EVERYTHING VISIBLE. FOREVER.': '  TUTTO ONLINE. TUTTO VISIBILE. PER SEMPRE.',
    '🔓 DATABASE PUBLISHED! +$100,000': '🔓 DATABASE PUBBLICATO! +$100,000',
    '  NEXUS CORPORATION DATABASE DELETED': '  DATABASE NEXUS CORPORATION CANCELLATO',
    '  Every trace. Every proof. Every name.': '  Ogni traccia. Ogni prova. Ogni nome.',
    '  The truth buried with Darius. Forever.': '  La verità sepolta con Darius. Per sempre.',
    '  No one will ever know what happened.': '  Nessuno saprà mai cosa è successo.',
    '🔒 DATABASE DESTROYED. The truth is silent.': '🔒 DATABASE DISTRUTTO. La verità tace.',
    '3D View — {}': 'Vista 3D — {}',
    'Connected on port {}': 'Connesso su porta {}',
    'Language set to {}. Restart dialog to see changes.': 'Lingua impostata su {}. Riavvia la finestra per vedere le modifiche.',
    'Settings are saved automatically.': 'Le impostazioni vengono salvate automaticamente.',
    'Use SOUND command in terminal to toggle quickly.': 'Usa il comando SOUND nel terminale per attivare/disattivare rapidamente.',
    'Language changes apply immediately.': 'Le modifiche alla lingua si applicano immediatamente.',
    '  CLOSE  ': '  CHIUDI  ',
    'WARNING: Trace at {t:.0f}% — suspicious activity detected!': 'ALLARME: Trace al {t:.0f}% — attività sospetta rilevata!',
    'HACKBACK! An enemy server stole ${}': 'HACKBACK! Un server nemico ha rubato ${}',
    ' and deleted "{}"': ' e cancellato "{}"',
    'HACKBACK! An enemy server withdrew ${}!': 'HACKBACK! Un server nemico ha prelevato ${}!',
}
