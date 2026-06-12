#!/usr/bin/env python3
# HACKER EVOLUTION — Entry point
# Created by 404 Fun Not Found
# Ispirato a Hacker Evolution: Untold (exosyphen studios)

from ui.app import HackerApp

if __name__ == '__main__':
    while True:
        app = HackerApp()
        app.run()
        if not app.restart_requested:
            break
