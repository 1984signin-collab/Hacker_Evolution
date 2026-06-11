"""Generate animated GIF of Hacker Evolution gameplay.

Runs the game normally (with boot) but at high speed and captures frames.
"""
import sys
import os
import time
import tkinter as tk

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _PROJECT_ROOT)


def capture_window(root):
    """Capture the tkinter window as a PIL Image."""
    from PIL import ImageGrab
    root.update_idletasks()
    root.update()
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    return ImageGrab.grab(bbox=(x, y, x + w, y + h))


def main():
    from ui.app import HackerApp
    from engine.game import g

    print("Starting Hacker Evolution for GIF capture...")

    # Monkey-patch to skip boot/login window (just for capture)
    import ui.app as app_mod

    original_boot = app_mod.HackerApp._fake_boot_desktop
    def skip_boot(self):
        """Skip the boot/login window entirely for GIF capture."""
        self._boot_state = 'DONE'
        self._boot_silent = True

    app_mod.HackerApp._fake_boot_desktop = skip_boot

    app = HackerApp()
    root = app.root

    # Let the app settle
    root.update()
    time.sleep(0.2)

    # Restore original boot method (not needed anymore)
    app_mod.HackerApp._fake_boot_desktop = original_boot

    # Clean console, write rich intro
    app.console.config(state=tk.NORMAL)
    app.console.delete('1.0', tk.END)
    app.console.config(state=tk.DISABLED)

    app.console_rich('[bold yellow]███[/][bold green]███[/][bold cyan]███[/] '
                     '[bold white]HACKER EVOLUTION[/] '
                     '[bold yellow]███[/][bold green]███[/][bold cyan]███[/]')
    app.console_rich('[dim]Sistema inizializzato. Digita HELP per i comandi.[/]')
    app.console_rich('')
    root.update()
    time.sleep(0.2)

    all_frames = []

    def type_and_capture(cmd_text):
        """Simulate typing + execute a command, capture frames."""
        frames = []
        # Show empty prompt
        app.input_var.set('')
        root.update()
        # Type character by character
        for i in range(len(cmd_text)):
            app.input_var.set(cmd_text[:i + 1])
            app.input.icursor(tk.END)
            root.update()
            time.sleep(0.05)
            if i % 2 == 0 or i == len(cmd_text) - 1:
                frames.append(capture_window(root))
        # Press Enter
        app.on_cmd(None)
        root.update()
        time.sleep(0.15)
        # Capture output
        for _ in range(5):
            root.update()
            time.sleep(0.06)
            frames.append(capture_window(root))
        return frames

    # Frame 1: initial screen
    all_frames.append(capture_window(root))
    time.sleep(0.1)

    # HELP command
    print("  Capturing HELP...")
    all_frames.extend(type_and_capture('HELP'))

    # SERVERS
    print("  Capturing SERVERS...")
    all_frames.extend(type_and_capture('SERVERS'))

    # CONFIG
    print("  Capturing CONFIG...")
    all_frames.extend(type_and_capture('CONFIG'))

    # STORY
    print("  Capturing STORY...")
    all_frames.extend(type_and_capture('STORY'))

    # Generate GIF
    print(f"  Generating GIF from {len(all_frames)} frames...")
    gif_path = os.path.join(_PROJECT_ROOT, 'assets', 'demo.gif')
    os.makedirs(os.path.dirname(gif_path), exist_ok=True)

    frames_opt = all_frames[::2]
    frames_opt[0].save(
        gif_path,
        save_all=True,
        append_images=frames_opt[1:],
        duration=100,
        loop=0,
        optimize=True,
    )
    print(f"  GIF saved: {gif_path} ({len(frames_opt)} frames)")

    # Static screenshot
    preview = os.path.join(_PROJECT_ROOT, 'assets', 'screenshot.png')
    frames_opt[0].save(preview)
    print(f"  Screenshot saved: {preview}")

    root.destroy()
    print("Done!")


if __name__ == '__main__':
    main()
